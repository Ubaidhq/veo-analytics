# Veo footage processing for social media content

This repository provides tools for processing sports match videos captured by VEO cameras. It allows you to download full match recordings, extract specific clips based on timeline data, and concatenate these clips into a single video suitable for social media sharing. 

## Features

- **Download Full Match Videos**: Automatically download the entire match video using provided stream links from VEO cameras.
- **Clip Extraction**: Extract specific segments from the full video based on timeline data, including start and end times.
- **Audio Handling**: Ensure that both video and audio are included in the extracted clips.
- **Concatenation**: Combine multiple clips into a single video file, maintaining audio synchronization.
- **Logging**: Log the processing of each clip, including its tag and start time in the match.

## Usage

### Prerequisites

- Python 3.x
- Required Python packages: `moviepy`, `requests`, `tqdm`

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   ```

2. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

### Environment Configuration

Create a `.env` file in the root of the project with the following environment variables:

- `VEO_API_TEMP_TOKEN`: Your temporary API token, which can be fetched from the VEO API Explorer.
- `BASE_URL`: The base URL for the VEO API, typically `https://api.veo.co/`.
- `NUM_THREADS`: The number of threads to use for concurrent processing, e.g., `4`.

Example `.env` file:

```.env
VEO_API_TEMP_TOKEN=your_api_temp_token_here
BASE_URL=https://api.veo.co/
NUM_THREADS=4
```

### Running the Script

To process a specific match by its ID:

```bash
python main.py "match-id"
```

To process the first match in the list:

```bash
python main.py
```

## Configuration

- Ensure that the `clips` and `output` directories exist in the root of the repository for storing downloaded and processed videos.

## File Structure

- `main.py`: The main script to run the video processing workflow.
- `utils/clip_handler.py`: Contains functions for downloading and clipping videos.
- `utils/video_processing.py`: Contains functions for concatenating video clips.
- `veo_api/matches.py`: Contains functions to list matches.
- `veo_api/clips.py`: Contains functions to list clips for a match.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.
