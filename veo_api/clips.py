import requests
from typing import List, Dict, Any
from .authentication import get_headers, BASE_URL

def list_clips(match_id: str, page_size: int = 20) -> List[Dict[str, Any]]:
    """
    Fetch a list of clips for a given match from the Veo API.

    :param match_id: The ID of the match to fetch clips for.
    :param page_size: Number of clips to retrieve per page (default 20).
    :return: A list of filtered clips if successful, otherwise raises an Exception.
    """
    url = f"{BASE_URL}clips?match={match_id}&page_size={page_size}"
    headers = get_headers()

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        clips = response.json()
        # Filter clips based on tags
        filtered_clips = [
            clip for clip in clips.get('items', [])
            if 'tags' in clip and any(tag in ['shot-on-goal', 'goal'] for tag in clip['tags'])
        ]
        return filtered_clips
    else:
        raise Exception(f"Failed to fetch clips. Status code: {response.status_code}") 