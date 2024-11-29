import os

def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def get_clip_save_path(video_id):
    """ Return the path where the downloaded clip should be saved """
    clips_dir = "./clips/"
    ensure_directory_exists(clips_dir)
    return os.path.join(clips_dir, f"{video_id}.mp4")
