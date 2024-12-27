import os
import requests
import logging
from typing import Dict, List, Any
from threading import Lock
from tqdm import tqdm
from datetime import datetime

from moviepy.editor import VideoFileClip, concatenate_videoclips

from utils.clips import Clip
from veo_api.api_handler import APIHandler

DEFAULT_TAGS = ['shot-on-goal', 'goal']

class ClipHandler:
    """
    Class to handle downloading and manipulating clips.  This class should be able to handle clips
    for multiple matches.
    """
    def __init__(self) -> None:
        self.clips: dict[str, list[Clip]] = []
        pass

    @staticmethod
    def save_clip_to_disk(clip: Clip, lock: Lock, offset: int):
        """
        Save a clip's content to disk and return the path to the saved clip.

        The VEO API currently returns stream urls for the both the full video and shorter clip.  T
        he logic behind this deicison on their side is unknown.  

        Shorter clips can be identified by the fact that their stream urls end in 'video.mp4'
        """
        stream_url = clip.stream_url
        if stream_url.endswith('video.mp4'):
            # This is a clip
            APIHandler.download_clip(clip, lock)
        else:
            # This is the full video stream url
            # Check if the full video is already downloaded
            match_name = clip.match.title.replace(' ', '_')
            full_video_path = f"./full_game_footage/{match_name}.mp4"
            if not os.path.exists(full_video_path):
                # Download the full video
                APIHandler.download_file(clip.stream_url, full_video_path)
            else:
                logging.info(f"Full video already downloaded for {match_name}")
                ClipHandler.clip_video(full_video_path, clip.start_time, clip.end_time, clip.match.start_time, match_name, clip.tags, offset)

    @staticmethod
    def clip_video(video_path: str, clip_start_time: str, clip_end_time: str, recording_start_time: str, match_name: str, tag: str, offset: int) -> None:
        """
        Clip a segment from the video based on start and end times relative to the recording start time.

        Arguments:
            video_path (str): Path to the full video.
            clip_start_time (str): Start time of the clip in ISO 8601 format.
            clip_end_time (str): End time of the clip in ISO 8601 format.
            recording_start_time (str): Start time of the recording in ISO 8601 format.
            match_name (str): Path where the clipped video will be saved.
            tag (str): Tag of the clip for logging purposes.
            offset (int): Number of seconds to trim from the start and end of the clip.

        Returns:
            None
        """
        # Parse the datetime strings
        recording_start = datetime.fromisoformat(recording_start_time.replace('Z', '+00:00'))
        clip_start = datetime.fromisoformat(clip_start_time.replace('Z', '+00:00'))
        clip_end = datetime.fromisoformat(clip_end_time.replace('Z', '+00:00'))

        # Calculate the start and end offsets in seconds, adjusting by the offset
        start_seconds = (clip_start - recording_start).total_seconds() + offset
        end_seconds = (clip_end - recording_start).total_seconds() - offset

        # Ensure the adjusted times are within valid bounds
        if start_seconds < 0:
            start_seconds = 0
        if end_seconds < start_seconds:
            end_seconds = start_seconds

        # Convert start time to minutes:seconds for logging
        start_minutes = int(start_seconds // 60)
        start_seconds_remainder = int(start_seconds % 60)
        start_time_formatted = f"{start_minutes}:{start_seconds_remainder:02}"

        output_path = f"./output/{match_name}_{tag}.mp4"
        if os.path.exists(output_path):
            logging.info(f"Clip already exists at {output_path}")
            return

        logging.info(f"Saving clip '{output_path}' starting at {start_time_formatted} (mm:ss)")

        with VideoFileClip(video_path) as video:
            # Extract the subclip with audio
            clip = video.subclip(start_seconds, end_seconds)
            clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

    def concatenate_clips(clips: List[Clip], output_path: str) -> None:
        """
        Concatenate multiple video clips into one with audio.

        Arguments:
            clip_paths (List[str]): List of paths to the video clips.
            output_path (str): Path where the final video will be saved.

        Returns:
            None
        """
        clips = [VideoFileClip(clip.save_path) for clip in clips]
        final_clip = concatenate_videoclips(clips, method="compose")
        final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')