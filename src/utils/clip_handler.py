import os
import requests
from tqdm import tqdm
from datetime import datetime
from moviepy.editor import VideoFileClip, concatenate_videoclips
from utils.file_handler import get_clip_save_path
import logging
from typing import Dict, List

def download_clip(clip: Dict, all_clip_paths: List[str], lock) -> None:
    """
    Download a video clip from the provided clip data and save it to disk.

    Arguments:
        clip (Dict): A dictionary containing clip information.
        all_clip_paths (List[str]): List to store paths of all downloaded clips.
        lock: A threading lock to ensure thread-safe operations on shared resources.

    Returns:
        None
    """
    try:
        stream_url = None
        for link in clip.get('links', []):
            if link.get('rel') == 'stream':
                stream_url = link.get('href')
                break

        if not stream_url:
            logging.error("Stream URL not found in clip data.")
            return

        video_id = clip.get('id')
        save_path = os.path.join('./clips', f"{video_id}.mp4")

        logging.info(f"Downloading clip from {stream_url} to {save_path}")

        response = requests.get(stream_url, stream=True)
        if response.status_code != 200:
            logging.error(f"Failed to download clip. Status code: {response.status_code}")
            return

        total_size = int(response.headers.get('content-length', 0))
        block_size = 8192  # 8 KB

        with open(save_path, 'wb') as f, tqdm(
            total=total_size, unit='iB', unit_scale=True, desc=video_id
        ) as bar:
            for chunk in response.iter_content(chunk_size=block_size):
                f.write(chunk)
                bar.update(len(chunk))

        with lock:
            all_clip_paths.append(save_path)
            logging.info(f"Clip downloaded and saved to {save_path}")

    except Exception as e:
        logging.error(f"Error downloading clip {clip.get('id')}: {e}")

# def clip_video(video_path: str, clip_start_time: str, clip_end_time: str, recording_start_time: str, output_path: str, tag: str, offset: int) -> None:
#     """
#     Clip a segment from the video based on start and end times relative to the recording start time.

#     Arguments:
#         video_path (str): Path to the full video.
#         clip_start_time (str): Start time of the clip in ISO 8601 format.
#         clip_end_time (str): End time of the clip in ISO 8601 format.
#         recording_start_time (str): Start time of the recording in ISO 8601 format.
#         output_path (str): Path where the clipped video will be saved.
#         tag (str): Tag of the clip for logging purposes.
#         offset (int): Number of seconds to trim from the start and end of the clip.

#     Returns:
#         None
#     """
#     # Parse the datetime strings
#     recording_start = datetime.fromisoformat(recording_start_time.replace('Z', '+00:00'))
#     clip_start = datetime.fromisoformat(clip_start_time.replace('Z', '+00:00'))
#     clip_end = datetime.fromisoformat(clip_end_time.replace('Z', '+00:00'))

#     # Calculate the start and end offsets in seconds, adjusting by the offset
#     start_seconds = (clip_start - recording_start).total_seconds() + offset
#     end_seconds = (clip_end - recording_start).total_seconds() - offset

#     # Ensure the adjusted times are within valid bounds
#     if start_seconds < 0:
#         start_seconds = 0
#     if end_seconds < start_seconds:
#         end_seconds = start_seconds

#     # Convert start time to minutes:seconds for logging
#     start_minutes = int(start_seconds // 60)
#     start_seconds_remainder = int(start_seconds % 60)
#     start_time_formatted = f"{start_minutes}:{start_seconds_remainder:02}"

#     logging.info(f"Saving clip '{tag}' starting at {start_time_formatted} (mm:ss)")

#     with VideoFileClip(video_path) as video:
#         # Extract the subclip with audio
#         clip = video.subclip(start_seconds, end_seconds)
#         clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

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