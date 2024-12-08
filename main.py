import os
import argparse
from datetime import datetime
from threading import Thread, Lock
from veo_api.matches import list_matches
from veo_api.clips import list_clips
from utils.clip_handler import download_full_video, clip_video
from utils.video_processing import concatenate_clips
from moviepy.editor import VideoFileClip
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the number of threads from the environment variable, default to 4
NUM_THREADS = int(os.getenv('NUM_THREADS', 4))

# Initialize a lock for thread-safe operations
lock = Lock()

def download_clip(clip, full_video_path, recording_start_time, video_duration, offset, all_clip_paths):
    clip_start_time = clip['timeline']['start']
    clip_end_time = clip['timeline']['end']
    tag = clip.get('tags', 'No Tag')  # Assuming 'tags' is a list or string

    # Calculate the start and end offsets in seconds
    start_seconds = (datetime.fromisoformat(clip_start_time.replace('Z', '+00:00')) - recording_start_time).total_seconds()
    end_seconds = (datetime.fromisoformat(clip_end_time.replace('Z', '+00:00')) - recording_start_time).total_seconds()

    if start_seconds >= video_duration or end_seconds > video_duration:
        with lock:
            print(f"Skipping clip {clip['id']} due to invalid timeline.")
        return

    clip_output_path = f"./clips/{clip['id']}_clipped.mp4"
    clip_video(full_video_path, clip_start_time, clip_end_time, recording_start_time.isoformat(), clip_output_path, tag, offset)

    with lock:
        all_clip_paths.append(clip_output_path)

def process_match(match, offset):
    match_id = match['id']
    match_name = match.get('title', 'Unnamed')
    print(f"Processing match: {match_name} with ID: {match_id}")

    # Parse the recording start time
    recording_start_time = datetime.fromisoformat(match['timeline']['start'].replace('Z', '+00:00'))

    # Check if the full video is already downloaded
    full_video_path = f"./clips/{match_id}.mp4"
    if not os.path.exists(full_video_path):
        print(f"Full video for match ID '{match_id}' not found in clips directory. Downloading...")
        # Download the full video using any clip's stream link
        clips = list_clips(match_id)
        if clips:
            full_video_path = download_full_video(clips[0])
        else:
            print(f"No clips found for Match ID {match_id} to download the full video.")
            return

    # Check the duration of the downloaded video
    with VideoFileClip(full_video_path) as video:
        video_duration = video.duration
        print(f"Full video duration: {video_duration} seconds")

    # Step 2: Fetch clips for the match
    try:
        clips = list_clips(match_id)
        if not clips:
            print(f"No clips found for Match ID {match_id}")
            return

        # Sort clips by their start time
        clips.sort(key=lambda clip: datetime.fromisoformat(clip['timeline']['start'].replace('Z', '+00:00')))

        # Create a thread pool for downloading clips
        all_clip_paths = []
        with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
            futures = []
            for clip in clips:
                future = executor.submit(download_clip, clip, full_video_path, recording_start_time, video_duration, offset, all_clip_paths)
                futures.append(future)

            # Wait for all threads to complete
            for future in futures:
                future.result()

        # Step 3: Concatenate all extracted clips
        if all_clip_paths:
            output_path = f"./output/{match_id}_concatenated_video.mp4"
            concatenate_clips(all_clip_paths, output_path)
            print(f"All clips concatenated and saved to {output_path}")

    except Exception as e:
        print(f"Error processing match {match_id}: {e}")

def main(match_id: str = None, offset: int = 5):
    # Step 1: Fetch the list of matches
    try:
        matches = list_matches()
        print("Matches fetched successfully:")

        if match_id:
            # Process a specific match
            match_found = False
            for match in matches['items']:
                if match.get('id', '') == match_id:
                    match_found = True
                    process_match(match, offset)
                    break
            if not match_found:
                print(f"Match ID '{match_id}' not found.")
        else:
            # Process only the first match
            if matches['items']:
                process_match(matches['items'][0], offset)
            else:
                print("No matches available to process.")

    except Exception as e:
        print(f"Error fetching matches: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process and concatenate clips for a specific match.")
    parser.add_argument("match_id", type=str, nargs='?', help="The ID of the match to process.")
    parser.add_argument("--offset", type=int, default=5, help="Number of seconds to trim from the start and end of each clip.")
    args = parser.parse_args()

    main(args.match_id, args.offset)
