import requests
from veo_api.authentication import get_headers, BASE_URL
from utils.clip import Clip
from utils.match import Match

class APIHandler:
    def __init__(self, page_size=20):
        self.page_size = page_size

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
