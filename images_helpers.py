from PIL import Image
import requests
from io import BytesIO
import os

# Download image from URL
def download_image(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
    except Exception as e:
        print(f"Error downloading image: {e}")
    return None

# Resize image to match frame size
def resize_image(image, size=(500, 700)):
    return image.resize(size, Image.Resampling.LANCZOS)

# Add frame to the card
def add_frame_to_card(card_img, frame_path, size=(500, 700)):
    try:
        card_img = resize_image(card_img, size).convert("RGBA")
        frame = Image.open(frame_path).convert("RGBA").resize(size)
        framed_card = Image.alpha_composite(card_img, frame)
        return framed_card
    except Exception as e:
        print(f"Error adding frame to card: {e}")
        return None

# Merge multiple framed cards side-by-side
def merge_cards_side_by_side(cards, size=(500, 700), spacing=20):
    total_width = (size[0] * len(cards)) + (spacing * (len(cards) - 1))
    merged_image = Image.new("RGBA", (total_width, size[1]), (255, 255, 255, 0))

    x_offset = 0
    for card in cards:
        if card:
            merged_image.paste(card, (x_offset, 0), card)
            x_offset += size[0] + spacing

    merged_path = os.path.join(os.getcwd(), "merged_cards.png")
    merged_image.save(merged_path)
    return merged_path




def merge_images_horizontally(images, spacing=20):
    if not images:
        return None

    print(f"Number of images received: {len(images)}")

    # Ensure all images are the same height
    heights = [img.height for img in images]
    target_height = min(heights)
    print(f"Target height: {target_height}")

    # Resize images to the same height
    resized_images = []
    for i, img in enumerate(images):
        try:
            resized_img = img.resize((int(img.width * target_height / img.height), target_height))
            resized_images.append(resized_img)
            print(f"Image {i+1} resized: {resized_img.size}")
        except Exception as e:
            print(f"Failed to resize image {i+1}: {e}")

    # Calculate total width with spacing
    total_width = sum(img.width for img in resized_images) + spacing * (len(resized_images) - 1)
    print(f"Total width: {total_width}")

    # Create transparent background
    merged_image = Image.new("RGBA", (total_width, target_height), (0, 0, 0, 0))

    # Paste images side-by-side with spacing
    x_offset = 0
    for i, img in enumerate(resized_images):
        try:
            merged_image.paste(img, (x_offset, 0), mask=img)
            print(f"Pasted image {i+1} at x_offset: {x_offset}")
            x_offset += img.width + spacing
        except Exception as e:
            print(f"Failed to paste image {i+1}: {e}")

    print(f"Final image width: {merged_image.width}")
    return merged_image

