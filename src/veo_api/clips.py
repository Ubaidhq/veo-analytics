import requests
from typing import List, Dict, Any
from .authentication import get_headers, BASE_URL

def list_clips(match_id: str, page_size: int = 20) -> List[Dict[str, Any]]:
    """
    Fetch a list of clips for a given match from the Veo API, handling pagination.

    Arguments:
        match_id (str): The ID of the match to fetch clips for.
        page_size (int): Number of clips to retrieve per page (default 20).

    Returns:
        List[Dict[str, Any]]: A list of filtered clips if successful.
    """
    clips = []
    next_page_token = None

    while True:
        url = f"{BASE_URL}clips?match={match_id}&page_size={page_size}"
        if next_page_token:
            url += f"&page_token={next_page_token}"

        headers = get_headers()
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            # Filter clips based on tags
            filtered_clips = [
                clip for clip in data.get('items', [])
                if 'tags' in clip and any(tag in ['shot-on-goal', 'goal'] for tag in clip['tags'])
            ]
            clips.extend(filtered_clips)

            # Check for next page token
            next_page_token = data.get('next_page_token')
            if not next_page_token:
                break
        else:
            raise Exception(f"Failed to fetch clips. Status code: {response.status_code}")

    return clips 