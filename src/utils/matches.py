import requests
from veo_api.authentication import get_headers, BASE_URL

class Match:
    """
    A class to represent a match.
    """
    def __init__(self, id: str, timeline: dict, title: str, links: list, recordings: list):
        self.id = id
        self.timeline = timeline # e.g{start: '2024-12-21T15:57:41.440Z', end: '2024-12-21T16:00:00.000Z'}
        self.title = title
        self.links = links
        self.recordings = recordings

    def __repr__(self):
        return f"Match(id={self.match_id}, title={self.title})"
