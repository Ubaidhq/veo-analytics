import os
import requests
import logging
from typing import Dict, List, Any

from tqdm import tqdm
from datetime import datetime

from moviepy.editor import VideoFileClip, concatenate_videoclips
from utils.clips import Clip

DEFAULT_TAGS = ['shot-on-goal', 'goal']

class ClipHandler:
    """
    Class to handle downloading and manipulating clips.  This class should be able to handle clips
    for multiple matches.
    """
    def __init__(self) -> None:
        self.clips: dict[str, list[Clip]] = []
        pass

    def clip_video(video_path: str, clip_start_time: str, clip_end_time: str, recording_start_time: str, output_path: str, tag: str, offset: int) -> None:
        """
        Clip a segment from the video based on start and end times relative to the recording start time.

        Arguments:
            video_path (str): Path to the full video.
            clip_start_time (str): Start time of the clip in ISO 8601 format.
            clip_end_time (str): End time of the clip in ISO 8601 format.
            recording_start_time (str): Start time of the recording in ISO 8601 format.
            output_path (str): Path where the clipped video will be saved.
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

        logging.info(f"Saving clip '{tag}' starting at {start_time_formatted} (mm:ss)")

        with VideoFileClip(video_path) as video:
            # Extract the subclip with audio
            clip = video.subclip(start_seconds, end_seconds)
            clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

    def concatenate_clips(clip_paths: List[str], output_path: str) -> None:
        """
        Concatenate multiple video clips into one with audio.

        Arguments:
            clip_paths (List[str]): List of paths to the video clips.
            output_path (str): Path where the final video will be saved.

        Returns:
            None
        """
        clips = [VideoFileClip(clip) for clip in clip_paths]
        final_clip = concatenate_videoclips(clips, method="compose")
        final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')