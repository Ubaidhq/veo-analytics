import requests
import logging
import os
from tqdm import tqdm
from typing import List

from veo_api.authentication import get_headers, BASE_URL
from utils.clips import Clip
from utils.matches import Match

class APIHandler:
    @staticmethod
    def fetch_matches(page_size=20):
        """
        Fetch a list of matches from the Veo API, handling pagination.
        """
        matches = []
        next_page_token = None

        while True:
            url = f"{BASE_URL}matches?page_size={page_size}"
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
    def fetch_clips(match: Match, tags=None, page_size=20):
        """
        Fetch a list of clips for a given match from the Veo API, handling pagination.
        """
        if tags is None:
            tags = []

        clips = []
        next_page_token = None

        while True:
            url = f"{BASE_URL}clips?match={match.id}&page_size={page_size}"
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
    
    @staticmethod
    def download_clip(clip: Clip, lock) -> None:
        """
        Download a video clip from the provided clip data and save it to disk.

        Arguments:
            clip: A dictionary containing clip information.
            lock: A threading lock to ensure thread-safe operations on shared resources.

        Returns:
            None
        """
       
        stream_url = clip.stream_url

        if not stream_url:
            logging.error("Stream URL not found for clip.")
            return

        video_name = f"{clip.match.title.replace(' ', '_')}_{clip.tags[0]}_{clip.start_time}.mp4"
        save_path = os.path.join('./clips', video_name)
        clip.save_path = save_path

        if os.path.exists(save_path):
            logging.info(f"Clip already exists at {save_path}")
            return

        try:
            APIHandler.download_file(stream_url, save_path)
            logging.info(f"Clip downloaded and saved to {save_path}")

        except Exception as e:
            logging.error(f"Error downloading {save_path}: {e}")

    @staticmethod
    def download_file(stream_url, save_path):
        """
        Downloads a file from the given stream URL and saves it to the specified path.

        :param stream_url: The URL of the file to download.
        :param save_path: The path where the file should be saved.
        :return: None
        """
        logging.info(f"Downloading file from {stream_url} to {save_path}")

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
# def download_clip(clip, full_video_path, recording_start_time, video_duration, offset, all_clip_paths):
#     clip_start_time = clip.start_time
#     clip_end_time = clip.end_time
#     tag = clip.tags # Assuming 'tags' is a list or string

#     # Calculate the start and end offsets in seconds
#     start_seconds = (datetime.fromisoformat(clip_start_time.replace('Z', '+00:00')) - recording_start_time).total_seconds()
#     end_seconds = (datetime.fromisoformat(clip_end_time.replace('Z', '+00:00')) - recording_start_time).total_seconds()

#     if start_seconds >= video_duration or end_seconds > video_duration:
#         with lock:
#             logging.info(f"Skipping clip {clip.id} due to invalid timeline.")
#         return

#     clip_output_path = f"./clips/{clip.clip_id}_clipped.mp4"
#     logging.info(f"Processing clip {clip.clip_id} with tag {tag}.")
#     ClipHandler.clip_video(full_video_path, clip_start_time, clip_end_time, recording_start_time.isoformat(), clip_output_path, tag, offset)

#     with lock:
#         all_clip_paths.append(clip_output_path)