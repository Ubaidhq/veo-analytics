import cv2
import torch
from moviepy.editor import VideoFileClip
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# Load YOLOv5 model (assuming YOLOv11 is similar)
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

def detect_ball(frame):
    """
    Detect the ball in a given frame using YOLO.

    Arguments:
        frame: The video frame to process.

    Returns:
        The frame with a bounding box drawn around the detected ball.
    """
    # Make a writable copy of the frame
    frame = frame.copy()

    results = model(frame)
    detections = results.xyxy[0]  # Get the detections

    for det in detections:
        # Assuming class 32 is the ball, adjust based on your model
        if det[-1] == 32:
            x1, y1, x2, y2, conf, cls = det
            # Draw a rectangle around the detected ball
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.putText(frame, f"Ball: {conf:.2f}", (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    return frame

def process_video(input_path, output_path):
    """
    Process a video to detect and display the ball.

    Arguments:
        input_path: Path to the input video file.
        output_path: Path to save the processed video.
    """
    clip = VideoFileClip(input_path)

    # Process each frame
    new_clip = clip.fl_image(detect_ball)

    # Write the output video
    new_clip.write_videofile(output_path, codec='libx264')

def main():
    input_path = "/Users/ubaidhoque/Projects/veo-analytics/clips/a535b755-a810-46cf-9507-7138b98256e0.mp4"  # Replace with your video file path
    output_path = "/Users/ubaidhoque/Projects/veo-analytics/output/output.mp4"  # Output file path

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"The file {input_path} does not exist.")

    process_video(input_path, output_path)

if __name__ == "__main__":
    main()

    !pip install roboflow

from roboflow import Roboflow
rf = Roboflow(api_key="NHD5Yxv23xhefQmJ1UTX")
project = rf.workspace("nikhil-chapre-xgndf").project("detect-players-dgxz0")
version = project.version(7)
dataset = version.download("yolov11")
                