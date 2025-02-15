import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import random
import time
import json
from PIL import Image, ImageOps
from images_helpers import download_image, resize_image, add_frame_to_card, merge_images_horizontally


# load environment variables from .env
load_dotenv()

# get token from env
TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = 1339716688748216392

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# Load cards from the JSON file at startup
try:
    with open("cards.json", "r") as f:
        cards = json.load(f)
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



@bot.event
async def on_reaction_add(reaction, user):
    # Ignore the bot's reactions
    if user == bot.user:
        return 
    
    user_id = user.id
    message_id = reaction.message.id

    # Get the card's info from the message map
    card = message_card_map.get(message_id)

    # If card doesn't exist, return early
    if not card:
        return

    # Download the card image
    card_image = download_image(card['image'])
    if not card_image:
        print(f"Failed to download card image for {card['name']}")
        return

    # Add frame to the card
    framed_card = add_frame_to_card(card_image, "frame_path.png")
    if framed_card:
        # Process the framed card (e.g., save, add to user's collection)
        print(f"Framed card {card['name']} added!")
    else:
        print(f"Failed to frame card {card['name']}")


@bot.command()
async def collection(ctx):
    user_id = ctx.author.id

    if user_id not in user_collection:
        await ctx.send(f"{ctx.author.mention} your collection looks empty right now. Use !drop if you want to start collecting!")
        return
    
    # get the user's collection
    collection = user_collection[user_id]

    embed = discord.Embed(
        title=f"**{ctx.author.display_name}'s collection**",
        color=discord.Color.blue()
    )
    for card in collection:
        embed.add_field(
            name=f"**{card['group']}**",
            value=f"**{card['name']}** - **Rarity**: {card['rarity']}",
            inline=False
        )
    await ctx.send(embed=embed)

bot.run(TOKEN)