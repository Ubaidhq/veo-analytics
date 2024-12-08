import os

def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def get_clip_save_path(video_id):
    """ Return the path where the downloaded clip should be saved """
    clips_dir = "./clips/"
    ensure_directory_exists(clips_dir)
    return os.path.join(clips_dir, f"{video_id}.mp4")

def cleanup_files(clips_paths):
    """
    Deletes the specified video files.

    :param clips_paths: List of paths to the video clips to be deleted.
    :return: None
    """
    for path in clips_paths:
        try:
            os.remove(path)
            print(f"Deleted {path}")
        except OSError as e:
            print(f"Error deleting {path}: {e}")