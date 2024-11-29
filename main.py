from typing import Dict, Any
from veo_api.matches import list_matches
from veo_api.clips import list_clips
from utils.clip_handler import download_clip
from utils.video_processing import concatenate_clips

def main() -> None:
    # Step 1: Fetch the list of matches
    try:
        matches: Dict[str, Any] = list_matches()
        print("Matches fetched successfully:")
        all_clip_paths = []
        for match in matches['items']:
            match_id: str = match['id']
            match_name: str = match.get('title', 'Unnamed')
            print(f"Match ID: {match_id}, Match Name: {match_name}")

            # Step 2: Fetch and filter clips for each match
            try:
                clips = list_clips(match_id)
                print(f"Clips for Match ID {match_id}:")
                for clip in clips:
                    print(f"Clip ID: {clip['id']}, Tags: {clip['tags']}")
                    # Download each clip
                    clip_path = download_clip(clip)
                    all_clip_paths.append(clip_path)
            except Exception as e:
                print(f"Error fetching clips for match {match_id}: {e}")

        # Step 3: Concatenate all downloaded clips
        if all_clip_paths:
            output_path = "./clips/concatenated_video.mp4"
            concatenate_clips(all_clip_paths, output_path)
            print(f"All clips concatenated and saved to {output_path}")

    except Exception as e:
        print(f"Error fetching matches: {e}")

if __name__ == "__main__":
    main()
