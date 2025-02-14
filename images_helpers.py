import random
from PIL import Image
import requests
from io import BytesIO
import os

cards = [
    {"name": "Chaewon", "group": "LESSERAFIM", "image": "https://cdn.discordapp.com/attachments/1339477207541878814/1340092206312198228/Kim-Chaewon-31.png?ex=67b1199f&is=67afc81f&hm=f0cbf766ff776589e6530b9907b729a2392e044da5149db626335df473f69034&" },
    {"name": "Yujin", "group": "IVE", "image": "https://cdn.discordapp.com/attachments/1339477207541878814/1340092248930386021/ive-the-1st-album-ive-ive-concept-photo-1-yujin-gaeul-rei-v0-18eef3tdeora1.png?ex=67b119a9&is=67afc829&hm=6d9a0108aa31e88f23bd3d509f6bde3275b28f8c7e615e9a40f14bd87c86839a&" },
    {"name": "Rosé", "group": "BLACKPINK", "image": "https://cdn.discordapp.com/attachments/1339289261651787786/1339730876677881876/thumb-qui-est-rose-des-blackpink-premier-album-rosie-apt-kpop.png?ex=67b11a9b&is=67afc91b&hm=27feb3560255e9631833a741eb5a814825b0dc860c39c871e2082c131061d0cb&"}, 
]


# Download image from URL
def download_image(url):
    try:
        response = requests.get(url)
        print(f"Downloading from {url}, Status code: {response.status_code}")  # Add this line for debugging
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
    except Exception as e:
        print(f"Error downloading image: {e}")
    return None

# Resize image to match frame size
def resize_image(image, size=(500, 700)):
    return image.resize(size, Image.Resampling.LANCZOS)

# Save image to disk and return the file path
def save_image(image, filename):
    try:
        image.save(filename)
        return filename
    except Exception as e:
        print(f"Error saving image: {e}")
        return None

# Add frame to the card
def add_frame_to_card(card_img, frame_path, size=(500, 700)):
    try:
        card_img = resize_image(card_img, size).convert("RGBA")
        frame = Image.open(frame_path).convert("RGBA").resize(size)
        framed_card = Image.alpha_composite(card_img, frame)
        
        return framed_card  # Return the PIL.Image object directly instead of file path
    except Exception as e:
        print(f"Error adding frame to card: {e}")
        return None


# Merge images horizontally, resize to match height
def merge_images_horizontally(images, spacing=20):
    if not images:
        return None

    # Ensure all images are the same height
    heights = [img.height for img in images]
    target_height = min(heights)

    # Resize images to the same height and convert to RGB
    resized_images = []
    for img in images:
        resized_img = img.resize((int(img.width * target_height / img.height), target_height))
        resized_images.append(resized_img.convert("RGB"))  # Convert to RGB to avoid transparency issues

    # Calculate total width with spacing
    total_width = sum(img.width for img in resized_images) + spacing * (len(resized_images) - 1)

    # Create a blank white background for the merged image
    merged_image = Image.new("RGB", (total_width, target_height), (0, 0, 0))

    # Paste images side-by-side with spacing
    x_offset = 0
    for img in resized_images:
        merged_image.paste(img, (x_offset, 0))
        x_offset += img.width + spacing

    return merged_image



# Test function
def test_drop():
    # Ensure there are at least 3 cards to sample from
    if len(cards) < 3:
        print("Not enough cards to sample from.")
        return
    
    # Randomly select 3 cards
    dropped_cards = random.sample(cards, 3)

    card_images = []
    
    # Download and add frames to images
    for card in dropped_cards:
        card_img = download_image(card['image'])
        if card_img:
            framed_card = add_frame_to_card(card_img, "frame.png")  # Ensure the frame image is correctly referenced
            if framed_card:
                card_images.append(framed_card)  # Append the PIL.Image object, not the file path
            else:
                print(f"Failed to add frame to: {card['name']}")
        else:
            print(f"Failed to download: {card['name']}")

    if len(card_images) == 3:
        # Merge images horizontally
        merged_image = merge_images_horizontally(card_images, spacing=30)
        
        # Save the merged image for inspection
        merged_image.save("test_merged_image_with_frame.png")
        print("Merged image with frames saved as 'test_merged_image_with_frame.png'")
    else:
        print("Failed to download all images.")




