import os
import argparse
import logging
import sys
from datetime import datetime
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from typing import List

from dotenv import load_dotenv
from moviepy.editor import VideoFileClip

from veo_api.api_handler import APIHandler
from utils.clips import Clip
from utils.clip_handler import ClipHandler
from utils.matches import Match

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(threadName)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

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
            logging.info(f"Skipping clip {clip['id']} due to invalid timeline.")
        return

    clip_output_path = f"./clips/{clip['id']}_clipped.mp4"
    logging.info(f"Processing clip {clip['id']} with tag {tag}.")
    ClipHandler.clip_video(full_video_path, clip_start_time, clip_end_time, recording_start_time.isoformat(), clip_output_path, tag, offset)

    with lock:
        all_clip_paths.append(clip_output_path)

def process_match(match: Match, offset, use_clips, tags):
    logging.info(f"Processing match: {match.title}")

    # Parse the recording start time
    recording_start_time = datetime.fromisoformat(match.timeline['start'].replace('Z', '+00:00'))

    if use_clips:
        # Use individual clip streams
        clips: List[Clip] = APIHandler.fetch_clips(match, tags=tags)
        if not clips:
            logging.warning(f"No clips found for Match {match.title}")
            return

        # Sort clips by their start time
        clips.sort(key=lambda clip: datetime.fromisoformat(clip.start_time.replace('Z', '+00:00')))

        # Collect all clip paths
        all_clip_paths = []
        for clip in clips:
            stream_url = clip.stream_url
            if stream_url:
                all_clip_paths.append(stream_url)
            else:
                logging.warning(f"No stream link found for clip {clip['id']}")

        # Concatenate all extracted clips
        if all_clip_paths:
            output_path = f"./output/{match.title}{'_'.join(tags)}.mp4"
            ClipHandler.concatenate_clips(all_clip_paths, output_path)
            logging.info(f"All clips concatenated and saved to {output_path}")

    else:
        # Check if the full video is already downloaded
        full_video_path = f"./clips/{match.id}.mp4"
        if not os.path.exists(full_video_path):
            logging.info(f"Full video for match: {match.title} not found in clips directory. Downloading...")
            # Download the full video using any clip's stream link
            clips = APIHandler.fetch_clips(match, tags=tags)
            if clips:
                full_video_path = APIHandler.download_video(clips[0])
            else:
                logging.warning(f"No clips found for match: {match.title} to download the full video.")
                return

        # Check the duration of the downloaded video
        with VideoFileClip(full_video_path) as video:
            video_duration = video.duration
            logging.info(f"Full video duration: {video_duration} seconds")

        # Step 2: Fetch clips for the match
        try:
            clips = APIHandler.fetch_clips(match.id, tags=tags)
            if not clips:
                logging.warning(f"No clips found for match: {match.title}")
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
                output_path = f"./output/{match.title}{'_'.join(tags)}.mp4"
                ClipHandler.concatenate_clips(all_clip_paths, output_path)
                logging.info(f"All clips concatenated and saved to {output_path}")

        except Exception as e:
            logging.error(f"Error processing match {match.id}: {e}", exc_info=True)

def main(args):
    parser = argparse.ArgumentParser(description="Process and concatenate clips for a specific match.")
    parser.add_argument("--match_id", type=str, nargs='?', help="The ID of the match to process.")
    parser.add_argument("--offset", type=int, default=5, help="Number of seconds to trim from the start and end of each clip.")
    parser.add_argument("--use-clips", action='store_true', help="Use individual clip streams instead of downloading the full video.")
    parser.add_argument("--tags", type=str, nargs='*', default=['shot-on-goal', 'goal'], help="Tags to filter clips by.")
    args = parser.parse_args()

    # Print the configuration in a blocked format
    logging.info(
        "\nConfiguration:\n"
        f"{'match_id:':<12} {args.match_id}\n"
        f"{'offset:':<12} {args.offset}\n"
        f"{'use_clips:':<12} {args.use_clips}\n"
        f"{'tags:':<12} {', '.join(args.tags)}"
    )

    # Step 1: Fetch the list of matches
    try:
        matches: List[Match] = APIHandler.fetch_matches()
        logging.info("Matches fetched successfully.")

        if args.match_id:
            # Process a specific match
            match_found = False
            for match in matches:
                if match.id == args.match_id:
                    match_found = True
                    process_match(match, args.offset, args.use_clips, args.tags)
                    break
            if not match_found:
                logging.warning(f"Match ID '{args.match_id}' not found.")
        else:
            # Process only the first match
            if matches:
                latest_match = matches[0]
                process_match(latest_match, args.offset, args.use_clips, args.tags)
            else:
                logging.warning("No matches available to process.")

    except Exception as e:
        logging.error(f"Error fetching matches: {e}", exc_info=True)

if __name__ == "__main__":
    main(sys.argv[1:])
