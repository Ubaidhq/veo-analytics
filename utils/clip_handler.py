import requests
from .file_handler import get_clip_save_path

def download_clip(clip: dict) -> str:
    """
    Download a video clip from the provided clip data and save it to disk.

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
    video_id = clip.get('id')
    save_path = get_clip_save_path(video_id)

    # Download the video
    response = requests.get(stream_url, stream=True)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Video downloaded successfully and saved to {save_path}")
    else:
        raise Exception(f"Failed to download video. Status code: {response.status_code}")

    return save_path

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
        download_clip(clip_data)
    except Exception as e:
        print(f"Error during download: {e}") 