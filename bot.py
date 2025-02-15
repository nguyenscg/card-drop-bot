import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import random
import time
import json
from PIL import Image, ImageOps
from images_helpers import download_image, resize_image, add_frame_to_card, merge_images_horizontally
from data_helpers import load_collection, save_collection, add_card_to_collection


# load environment variables from .env
load_dotenv()

# get token from env
TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = 1339285083302920277

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
collection_data = load_collection()

# Load cards from the JSON file at startup
try:
    with open("cards.json", encoding="utf-8") as file:
        cards = json.load(file)
    print("Cards loaded:", cards)
except FileNotFoundError:
    print("cards.json file not found. Please check if it exists.")
    cards = [] 

# initialize rarities: common, rare, epic, legendary
rarities = {
    "Common": 50,
    "Rare": 25,
    "Epic": 15,
    "Legendary": 10,
}

# initialize empty dictionary to save card info
message_card_map = {}

# initialize drop cooldown
drop_cooldowns = {}

# initialize grab cooldown
grab_cooldowns = {}

# # initialize user's collection
# user_collection = {}

frame_path = "./images/frame.png"



# Initialize user_collection if the file doesn't exist or is empty
if os.path.exists("collection.json"):
    with open("collection.json", "r") as data_file:
        try:
            user_collection = json.load(data_file)
        except json.JSONDecodeError:
            # Handle case where the JSON is malformed
            print("Error loading the JSON data. Starting with an empty collection.")
            user_collection = {}
else:
    # If the file doesn't exist, initialize an empty collection
    user_collection = {}

# Checking for incomplete data in user_collection
for user_id, cards in user_collection.items():
    for card in cards:
        # Check if "image" is missing or empty
        if not card.get("image"):
            print(f"Missing image for card: {card['name']} from {card['group']}")
            card['image'] = "default_image_url"  # Provide a default image URL or path

# Save data
with open("collection.json", "w") as data_file:
    json.dump(user_collection, data_file, indent=4)

print("User collection saved successfully.")


@bot.event
async def on_ready():
    # Load cards from the JSON file when the bot is ready
    try:
        with open("cards.json", "r") as f:
            global cards
            cards = json.load(f)
            print("Cards loaded:", cards)
    except FileNotFoundError:
        print("Error: 'cards.json' file not found!")
    except json.JSONDecodeError:
        print("Error: Failed to decode 'cards.json'. Make sure it contains valid JSON.")
    
    print("Mingyu Bot just logged in!")
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send(f"Yo! Mingyu bot just logged in.")

def assign_random_rarity(card):
    # Use random.choices() to select a rarity based on the weights
    rarity = random.choices(list(rarities.keys()), list(rarities.values()), k=1)[0]
    card['rarity'] = rarity
    return card

@bot.command()
async def drop(ctx):
    user_id = ctx.author.id
    channel = bot.get_channel(CHANNEL_ID)
    
    # cooldown
    cooldown_timer = 3600
    current_time = time.time()

    # Check cooldown
    last_drop = drop_cooldowns.get(user_id, 0)
    if current_time - last_drop < cooldown_timer:
        remaining_time = cooldown_timer - (current_time - last_drop)
        hours, remainder = divmod(remaining_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        timer_message = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        await ctx.send(f"{ctx.author.mention}, please wait {timer_message} before dropping again!")
        return

    # Announce the drop (but without reactions yet)
    drop_message = await channel.send(f"🚨 {ctx.author.mention} came to drop some photocards! 🚨")

    # Ensure there are enough cards to sample from
    if len(cards) < 3:
        print("Error: Not enough cards to sample from.")
        await ctx.send("Not enough cards available for this drop!")
        return  # Exit the command early if not enough cards

    # Print available cards for debugging
    print("Cards available for dropping:", cards)

    # Select a number of cards that exists in the list (up to 3)
    num_cards_to_drop = min(3, len(cards))

    # Randomly select 3 cards (or fewer if there are not enough)
    dropped_cards = random.sample(cards, num_cards_to_drop)

    # Create the embed
    embed = discord.Embed(
        title="✨ Card Drop! ✨",
        description=f"{ctx.author.mention} just dropped some cards!",
        color=discord.Color.blue()
    )

    # Process and display the dropped cards
    card_images = []
    for card in dropped_cards:
        assign_random_rarity(card)
        card_img = download_image(card['image'])
        if card_img:
            framed_card = add_frame_to_card(card_img, frame_path)
            if framed_card:
                card_images.append(framed_card)
            else:
                print(f"Failed to add frame to: {card['name']}")
        else:
            print(f"Failed to download: {card['name']}")

    if len(card_images) == num_cards_to_drop:
        # Merge images horizontally
        merged_image = merge_images_horizontally(card_images, spacing=30)
        
        # Resize the image if needed
        merged_image = resize_image(merged_image)
        
        # Compress the image if needed
        merged_image_path = "merged_image_with_frame.png"
        merged_image.save(merged_image_path)

        print(f"Merged image with frames saved as '{merged_image_path}'")

        # Send the embed and image as a file
        with open(merged_image_path, "rb") as f:
            file = discord.File(f, filename="merged_image_with_frame.png")
            embed.set_image(url="attachment://merged_image_with_frame.png")  # Attach image in embed
            message = await ctx.send(embed=embed, file=file)  # Send message with file and embed
        try:
            os.remove(merged_image_path)
            print(f"Deleted temporary file: {merged_image_path}")
        except Exception as e:
            print(f"Failed to delete {merged_image_path}: {e}")

        # Map the dropped cards to the message
        message_card_map[message.id] = dropped_cards

        # Add reactions after sending the image
        reactions = ["🫰", "🫶", "🥰"]
        for reaction in reactions:
            await message.add_reaction(reaction)

    else:
        print("Failed to download all images.")
        await ctx.send("Failed to process the card images.")
    
    # Update cooldown for the user
    drop_cooldowns[user_id] = current_time



import time

# Store the cooldown timestamps for each user
grab_cooldowns = {}

@bot.event
async def on_reaction_add(reaction, user):
    """Handles card collection when a user reacts"""
    if user.bot:
        return  # Ignore bot reactions

    user_id = user.id
    message_id = reaction.message.id

    # Get the list of cards from the message map
    cards = message_card_map.get(message_id)

    if not cards:
        return  # If no cards are linked to this message, ignore

    # Cooldown check
    cooldown_timer = 3600  # 1 hour cooldown
    current_time = time.time()

    last_grab = grab_cooldowns.get(user_id, 0)
    if current_time - last_grab < cooldown_timer:
        remaining_time = cooldown_timer - (current_time - last_grab)
        hours, remainder = divmod(remaining_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        timer_message = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        await reaction.message.channel.send(f"{user.mention}, please wait {timer_message} before grabbing another card!")
        return

    # Map reactions to cards
    emoji_to_card = {"🫰": 0, "🫶": 1, "🥰": 2}
    if reaction.emoji in emoji_to_card:
        selected_card = cards[emoji_to_card[reaction.emoji]]

        # Save card to user's collection
        add_card_to_collection(user_id, selected_card)

        rarity = selected_card.get('rarity', 'Unknown')

        await reaction.message.channel.send(f"{user.mention} gained a {rarity}-Tier **{selected_card['name']}** photocard! 🤩")

        # Update cooldown
        grab_cooldowns[user_id] = current_time




@bot.command()
async def collection(ctx):
    """Displays the user's collected cards"""
    user_id = str(ctx.author.id)
    collection_data = load_collection()

    if user_id not in collection_data or not collection_data[user_id]:
        await ctx.send(f"{ctx.author.mention}, you don't have any photocards yet! 🃏")
        return

    # Build an embed with all collected cards
    embed = discord.Embed(
        title=f"{ctx.author.name}'s Collection",
        color=discord.Color.green()
    )

    for card in collection_data[user_id]:
        embed.add_field(name=card['group'], value=f"{card.get('rarity', 'Unknown')} - **{card['name']}**", inline=False)

    await ctx.send(embed=embed)

bot.run(TOKEN)