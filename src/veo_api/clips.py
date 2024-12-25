from veo_api.matches import Match

class Clip:
    def __init__(self, clip_id: str, tags: list, start_time: str, end_time: str, url: str, stream_url: str, match: Match):
        self.clip_id = clip_id
        self.tags = tags
        self.start_time = start_time
        self.end_time = end_time
        self.url = url
        self.stream_url = stream_url
        self.match = match
    
    def __repr__(self):
        return f"Clip(id={self.clip_id}, tags={self.tags}, start_time={self.start_time},
          end_time={self.end_time}, url={self.url}, stream_url={self.stream_url}, match_id={self.match.match_id})"
    
    def __str__(self):
        return f"Clip from match: {self.match.title} with tags: {self.tags}.  Duration: {self.clip.duration}.
        Start time: {self.start_time}"
    
    @property
    def duration(self):
        return self.end_time - self.start_time