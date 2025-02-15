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
def download_image(image_url):
    try:
        # If it's a URL, download it
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))  # Converts to an image object
        return image
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None

# Resize image to match frame size
def resize_image(image, max_size=(1024, 1024)):
    """Resize image to fit within max_size."""
    img = image.copy()
    img.thumbnail(max_size, Image.Resampling.LANCZOS)  # Use LANCZOS for high-quality downsampling
    return img

def compress_image(image, output_path, quality=75):
    """Compress image to a specified quality level."""
    image.save(output_path, quality=quality, optimize=True)


# Save image to disk and return the file path
def save_image(image, filename):
    try:
        image.save(filename)
        return filename
    except Exception as e:
        print(f"Error saving image: {e}")
        return None

# Add frame to the card
def add_frame_to_card(image, frame_path):
    try:
        # Load the frame image
        frame = Image.open(frame_path)

        # Resize the card image to fit the frame (if necessary)
        image = image.resize(frame.size)

        # Apply the frame to the card image
        image_with_frame = Image.alpha_composite(image.convert("RGBA"), frame.convert("RGBA"))
        return image_with_frame
    except Exception as e:
        print(f"Error adding frame to card: {e}")
        return None


# Merge images horizontally, resize to match height
def resize_image_maintain_aspect_ratio(image, base_width):
    """Resize the image to a specific width while maintaining aspect ratio."""
    # Calculate the ratio of the new width to the old width
    w_percent = base_width / float(image.size[0])
    h_size = int(float(image.size[1]) * float(w_percent))
    return image.resize((base_width, h_size), Image.Resampling.LANCZOS)

def merge_images_horizontally(images, spacing=100):
    """Merge a list of images horizontally with specified spacing."""
    
    # Resize images to a consistent width while maintaining aspect ratio
    base_width = 300  # Set the width for resizing
    images = [resize_image_maintain_aspect_ratio(img, base_width) for img in images]

    # Calculate the total width and height of the merged image with spacing
    total_width = sum(img.width for img in images) + (spacing * (len(images) - 1))
    max_height = max(img.height for img in images)
    
    # Create a new blank image with the calculated width and height
    merged_image = Image.new('RGB', (total_width, max_height), (0, 0, 0))
    
    # Position for the first image
    x_offset = 0
    
    # Paste each image into the merged image with spacing
    for img in images:
        merged_image.paste(img, (x_offset, 0))
        x_offset += img.width + spacing  # Move the x_offset for the next image
    
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




