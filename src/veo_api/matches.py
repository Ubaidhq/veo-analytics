import requests
from veo_api.authentication import get_headers, BASE_URL

class Match:
    """
    A class to represent a match.
    """
    def __init__(self, match_id: str, timeline: dict, title: str, links: list, recordings: list):
        self.match_id = match_id
        self.timeline = timeline # e.g{start: '2024-12-21T15:57:41.440Z', end: '2024-12-21T16:00:00.000Z'}
        self.title = title
        self.links = links
        self.recordings = recordings

    def __repr__(self):
        return f"Match(id={self.match_id}, title={self.title})"

def list_matches(page_size=20):
    """
    Fetch a list of matches from the Veo API, handling pagination.

    :param page_size: Number of matches to retrieve per page (default 20).
    :return: A list of Match objects if successful, otherwise raises an Exception.
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
                    match_id=match['id'],
                    timeline=match['timeline'],
                    title=match['title'],
                    links=match['links'],
                    recordings=match['recordings']
                )
                for match in matches_data.get('items', [])
            ])

            # Check for next page token to handle pagination
            # If a next_page_token is present, it indicates there are more pages of matches to fetch.
            next_page_token = matches_data.get('next_page_token')
            if not next_page_token:
                break
        else:
            raise Exception(f"Failed to fetch matches. Status code: {response.status_code}")

    return matches
