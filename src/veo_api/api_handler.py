import requests
import logging
import os
from tqdm import tqdm
from typing import List

from veo_api.authentication import get_headers, BASE_URL
from utils.clips import Clip
from utils.matches import Match

class APIHandler:
    def __init__(self, page_size=20):
        self.page_size = page_size

    @staticmethod
    def fetch_matches(self):
        """
        Fetch a list of matches from the Veo API, handling pagination.
        """
        matches = []
        next_page_token = None

        while True:
            url = f"{BASE_URL}matches?page_size={self.page_size}"
            if next_page_token:
                url += f"&page_token={next_page_token}"

            headers = get_headers()
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                matches_data = response.json()
                matches.extend([
                    Match(
                        id=match['id'],
                        timeline=match['timeline'],
                        title=match['title'],
                        links=match['links'],
                        recordings=match['recordings']
                    )
                    for match in matches_data.get('items', [])
                ])

                next_page_token = matches_data.get('next_page_token')
                if not next_page_token:
                    break
            else:
                raise Exception(f"Failed to fetch matches. Status code: {response.status_code}")

        return matches

    @staticmethod
    def fetch_clips(self, match, tags=None):
        """
        Fetch a list of clips for a given match from the Veo API, handling pagination.
        """
        if tags is None:
            tags = []

        clips = []
        next_page_token = None

        while True:
            url = f"{BASE_URL}clips?match={match.id}&page_size={self.page_size}"
            if next_page_token:
                url += f"&page_token={next_page_token}"

            headers = get_headers()
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                filtered_clips = [
                    Clip(
                        clip_id=clip['id'],
                        tags=clip['tags'],
                        start_time=clip['timeline']['start'],
                        end_time=clip['timeline']['end'],
                        url=clip['links'][0]['href'],
                        stream_url=next((link['href'] for link in clip.get('links', []) if link.get('rel') == 'stream'), None),
                        match=match
                    )
                    for clip in data.get('items', [])
                    if 'tags' in clip and any(tag in tags for tag in clip['tags'])
                ]
                clips.extend(filtered_clips)

                next_page_token = data.get('next_page_token')
                if not next_page_token:
                    break
            else:
                raise Exception(f"Failed to fetch clips. Status code: {response.status_code}")

        return clips
    
    def download_clip(clip: Clip, all_clip_paths: List[str], lock) -> None:
        """
        Download a video clip from the provided clip data and save it to disk.

        Arguments:
            clip: A dictionary containing clip information.
            all_clip_paths: List to store paths of all downloaded clips.
            lock: A threading lock to ensure thread-safe operations on shared resources.

        Returns:
            None
        """
        try:
            stream_url = clip.stream_url

            if not stream_url:
                logging.error("Stream URL not found for clip.")
                return

            video_name = f"{clip.match.title}_{clip.tags[0]}_{clip.start_time}.mp4"
            save_path = os.path.join('./clips', video_name)

            logging.info(f"Downloading clip from {stream_url} to {save_path}")

            response = requests.get(stream_url, stream=True)
            if response.status_code != 200:
                logging.error(f"Failed to download clip. Status code: {response.status_code}")
                return

            total_size = int(response.headers.get('content-length', 0))
            block_size = 8192  # 8 KB

            with open(save_path, 'wb') as f, tqdm(
                total=total_size, unit='iB', unit_scale=True, desc=save_path
            ) as bar:
                for chunk in response.iter_content(chunk_size=block_size):
                    f.write(chunk)
                    bar.update(len(chunk))

            with lock:
                all_clip_paths.append(save_path)
                logging.info(f"Clip downloaded and saved to {save_path}")

        except Exception as e:
            logging.error(f"Error downloading {save_path}: {e}")
