import requests
from tqdm import tqdm
from datetime import datetime
from moviepy.editor import VideoFileClip
from utils.file_handler import get_clip_save_path

def download_full_video(clip: dict) -> str:
    """
    Download the full video from the provided clip data and save it to disk.

    :param clip: A dictionary containing clip information.
    :return: The path where the video is saved.
    """
    # Find the stream URL in the links
    stream_url = None
    for link in clip.get('links', []):
        if link.get('rel') == 'stream':
            stream_url = link.get('href')
            break

    if not stream_url:
        raise ValueError("Stream URL not found in clip data.")

    # Determine the save path
    video_id = clip.get('match')  # Use match ID to avoid duplicate downloads
    save_path = get_clip_save_path(video_id)

    # Download the video with progress bar
    response = requests.get(stream_url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 8192  # 8 KB

    with open(save_path, 'wb') as f, tqdm(
        total=total_size, unit='iB', unit_scale=True, desc=video_id
    ) as bar:
        for chunk in response.iter_content(chunk_size=block_size):
            f.write(chunk)
            bar.update(len(chunk))

    if response.status_code != 200:
        raise Exception(f"Failed to download video. Status code: {response.status_code}")

    print(f"Video downloaded successfully and saved to {save_path}")
    return save_path

def clip_video(video_path: str, clip_start_time: str, clip_end_time: str, recording_start_time: str, output_path: str, tag: str, offset: int) -> None:
    """
    Clip a segment from the video based on start and end times relative to the recording start time.

    :param video_path: Path to the full video.
    :param clip_start_time: Start time of the clip in ISO 8601 format.
    :param clip_end_time: End time of the clip in ISO 8601 format.
    :param recording_start_time: Start time of the recording in ISO 8601 format.
    :param output_path: Path where the clipped video will be saved.
    :param tag: Tag of the clip for logging purposes.
    :param offset: Number of seconds to trim from the start and end of the clip.
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

    print(f"Saving clip '{tag}' starting at {start_time_formatted} (mm:ss)")

    with VideoFileClip(video_path) as video:
        # Extract the subclip with audio
        clip = video.subclip(start_seconds, end_seconds)
        clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

if __name__ == '__main__':
    # Example clip data for testing
    clip_data = {
        "id": "85fe2297-6c79-47b5-a86a-126adf845b59",
        "links": [
            {
                "rel": "stream",
                "href": "https://c.veocdn.com/22c7ec07-9381-45ec-a54d-1b9c281b/video.mp4#t=4993",
                "type": "video/mp4"
            }
        ]
    }

    try:
        print("Downloading clip...")
        download_full_video(clip_data)
    except Exception as e:
        print(f"Error during download: {e}") 