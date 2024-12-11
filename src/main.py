import os
import argparse
import logging
from typing import List, Dict, Optional
from veo_api.matches import list_matches
from veo_api.clips import list_clips
from utils.clip_handler import download_clip, concatenate_clips
from utils.file_handler import cleanup_files
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from datetime import datetime
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# Load environment variables from .env file
load_dotenv()

# Get the number of threads from the environment variable, default to 4
NUM_THREADS = int(os.getenv('NUM_THREADS', 4))

# Initialize a lock for thread-safe operations
lock = Lock()

def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Process and concatenate clips for a specific match.")
    parser.add_argument("match_id", type=str, nargs='?', help="The ID of the match to process.")
    parser.add_argument("--offset", type=int, default=5, help="Number of seconds to trim from the start and end of each clip.")
    return parser.parse_args()

def process_clips_for_match(match: Dict, offset: int) -> None:
    """
    Process all clips for a given match.

    Arguments:
        match (Dict): A dictionary containing match information.
        offset (int): Number of seconds to trim from the start and end of each clip.

    Returns:
        None
    """
    match_id = match['id']
    match_name = match.get('title', 'Unnamed')
    logging.info(f"Processing match: {match_name} with ID: {match_id}")

    clips = list_clips(match_id)
    if not clips:
        logging.warning(f"No clips found for Match ID {match_id}")
        return

    all_clip_paths = []

    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = [executor.submit(download_clip, clip, all_clip_paths, lock) for clip in clips]
        for future in futures:
            future.result()  # Ensure all downloads complete

    # Sort the downloaded clips by their start time
    try:
        all_clip_paths.sort(key=lambda path: next(
            datetime.fromisoformat(clip['timeline']['start'].replace('Z', '+00:00'))
            for clip in clips if os.path.basename(path).startswith(clip['id'])
        ))
    except Exception as e:
        logging.error(f"Error sorting downloaded clips: {e}")
        return

    if all_clip_paths:
        output_path = f"./output/{match_id}_concatenated_video.mp4"
        concatenate_clips(all_clip_paths, output_path)
        logging.info(f"All clips concatenated and saved to {output_path}")
        cleanup_files(all_clip_paths)
        logging.info("Temporary clip files cleaned up.")

def fetch_matches() -> Optional[Dict]:
    """
    Fetch matches from the API.

    Returns:
        Optional[Dict]: A dictionary of matches if successful, otherwise None.
    """
    try:
        matches = list_matches()
        logging.info("Matches fetched successfully.")
        return matches
    except Exception as e:
        logging.error(f"Error fetching matches: {e}")
        return None

def process_matches(matches: Optional[Dict], match_id: Optional[str] = None, offset: int = 5) -> None:
    """
    Process matches based on the provided match ID.

    Arguments:
        matches (Optional[Dict]): A dictionary of matches.
        match_id (Optional[str]): The ID of the match to process.
        offset (int): Number of seconds to trim from the start and end of each clip.

    Returns:
        None
    """
    if not matches:
        logging.warning("No matches available to process.")
        return

    if match_id:
        match_found = False
        for match in matches['items']:
            if match.get('id', '') == match_id:
                match_found = True
                process_clips_for_match(match, offset)
                break
        if not match_found:
            logging.warning(f"Match ID '{match_id}' not found.")
    else:
        process_clips_for_match(matches['items'][0], offset)

def main() -> None:
    """
    Main function to orchestrate fetching and processing of matches.

    Returns:
        None
    """
    args = parse_arguments()
    matches = fetch_matches()
    process_matches(matches, args.match_id, args.offset)

if __name__ == "__main__":
    main()
