import requests
from io import BytesIO
from PIL import Image
import os

# load frame once
frame_path = os.path.join(os.getcwd(), "images", "frame.png") 
frame = Image.open(frame_path)

# Function to download the image from a URL

def download_image(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        return img
    except Exception as e:
        print(f"Error downloading image: {e}")
    return None

def resize_image(image, frame_path, size=(500, 700)):  # Customize the size as you like
    card_img = image.resize(size, Image.Resampling.LANCZOS)
    frame = Image.open(frame_path).resize(size, Image.Resampling.LANCZOS)
    return card_img, frame

def add_frame_to_card(card_img, frame_img):
    try:
        # Ensure the frame is properly placed over the card image
        card_img.paste(frame_img, (0, 0), frame_img)  # Use frame_img as the mask for transparency
        return card_img
    except Exception as e:
        print(f"Error in adding frame to card: {e}")
        return None


