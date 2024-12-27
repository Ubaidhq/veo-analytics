from utils.matches import Match
from datetime import datetime

class Clip:
    def __init__(self, clip_id: str, tags: list, start_time: str, end_time: str, url: str, stream_url: str, match: Match):
        self.clip_id = clip_id
        self.tags = tags
        self.start_time = start_time
        self.end_time = end_time
        self.url = url
        self.stream_url = stream_url
        self.match = match
        self.save_path = None
    
    def __repr__(self):
        return (
            f"Clip(id={self.clip_id}, tags={self.tags}, start_time={self.start_time}, "
            f"end_time={self.end_time}, url={self.url}, stream_url={self.stream_url}, "
            f"match_id={self.match.id})"
        )
    
    def __str__(self):
        return (
            f"Clip from match: {self.match.title} with tags: {self.tags}. "
            f"Duration: {self.duration}. Start time: {self.start_time}"
        )
    
    @property
    def duration(self):
        # Convert start_time and end_time to datetime objects
        start_dt = datetime.fromisoformat(self.start_time.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(self.end_time.replace('Z', '+00:00'))
        # Return the duration in seconds
        return (end_dt - start_dt).total_seconds()