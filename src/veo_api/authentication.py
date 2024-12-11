import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the token from the .env file
VEO_API_TEMP_TOKEN = os.getenv("VEO_API_TEMP_TOKEN")
BASE_URL = os.getenv("BASE_URL")

def get_headers():
    """ Returns headers for authentication with the Veo API """
    if not VEO_API_TEMP_TOKEN:
        raise ValueError("API Token is missing. Please set it in the .env file.")
    
    headers = {
        "Authorization": f"Bearer {VEO_API_TEMP_TOKEN}",
        "Content-Type": "application/json"
    }
    return headers

