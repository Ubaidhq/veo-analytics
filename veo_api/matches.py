import requests
from .authentication import get_headers, BASE_URL
def list_matches(page_size=20):
    """
    Fetch a list of matches from the Veo API.

    :param page_size: Number of matches to retrieve per page (default 20).
    :return: A list of matches if successful, otherwise raises an Exception.
    """
    url = f"{BASE_URL}matches?page_size={page_size}"
    headers = get_headers()

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        matches = response.json()
        return matches
    else:
        raise Exception(f"Failed to fetch matches. Status code: {response.status_code}")
