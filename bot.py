import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import random
import time
import json
from PIL import Image, ImageOps
from images_helpers import download_image, add_frame_to_card, merge_images_horizontally


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

    # Announce the drop
    await channel.send(f"🚨 {ctx.author.mention} came to drop some photocards! 🚨")

    # reactions
    reactions = ["🫰", "🫶", "🥰"]
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
        
        # Save the merged image for inspection
        merged_image_path = "merged_image_with_frame.png"
        merged_image.save(merged_image_path)
        print(f"Merged image with frames saved as '{merged_image_path}'")
        
        # Add the image to the embed
        embed.set_image(url=f"attachment://{merged_image_path}")
        
        # Send the embed and the image
        await ctx.send(embed=embed, file=discord.File(merged_image_path))
    else:
        print("Failed to download all images.")
        await ctx.send("Failed to process the card images.")



# @bot.command()
# async def drop(ctx):
#     user_id = ctx.author.id
#     channel = bot.get_channel(CHANNEL_ID)
#     cooldown_timer = 3600
#     current_time = time.time()

#     # Check cooldown
#     last_drop = drop_cooldowns.get(user_id, 0)
#     if current_time - last_drop < cooldown_timer:
#         remaining_time = cooldown_timer - (current_time - last_drop)
#         hours, remainder = divmod(remaining_time, 3600)
#         minutes, seconds = divmod(remainder, 60)
#         timer_message = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
#         await ctx.send(f"{ctx.author.mention}, please wait {timer_message} before dropping again!")
#         return

#     # Announce the drop
#     await channel.send(f"🚨 {ctx.author.mention} came to drop some photocards! 🚨")

#     # reactions
#     reactions = ["🫰", "🫶", "🥰"]

#     # Drop 3 random cards
#     unique_cards = {card['image']: card for card in cards}.values()  # Remove duplicates based on image URL
    
#     dropped_cards = random.sample(list(unique_cards), 3)  # Ensure unique cards
    
#     print(f"Dropped Cards: {', '.join([card['name'] for card in dropped_cards])}")

#     card_images = []
#     all_card_info = []  # List to store info for all dropped cards

#     for card in dropped_cards:
#         print(f"Attempting to download: {card['name']} - {card['image']}")
#         card_img = download_image(card['image'])
#         frame_path = "./images/frame.png"
        
#         if card_img:
#             print(f"Downloaded: {card['name']}")
#             framed_card = add_frame_to_card(card_img, frame_path)
#             if framed_card:
#                 print(f"Framed: {card['name']}")
#                 card_images.append(framed_card)
#                 # Save card information for this card
#                 card_info = {
#                     "name": card['name'],
#                     "group": card['group'],
#                     "image": framed_card
#                 }
#                 all_card_info.append(card_info)
#             else:
#                 print(f"Failed to frame: {card['name']}")
#         else:
#             print(f"Failed to download: {card['name']}")

#     print(f"Total cards processed: {len(card_images)}")

#     # Merge the framed images horizontally with spacing
#     merged_image = merge_images_horizontally(card_images, spacing=30)
#     merged_image_path = "./images/merged_drop.png"
#     merged_image.save(merged_image_path)

#     # Send the merged image as one message
#     embed = discord.Embed(
#         title="✨ Card Drop! ✨",
#         description=f"{ctx.author.mention} just dropped some cards!",
#         color=discord.Color.blue()
#     )
#     file = discord.File(merged_image_path, filename="merged_drop.png")
#     embed.set_image(url="attachment://merged_drop.png")

#     message = await ctx.send(embed=embed, file=file)
    
#     # Add reactions to the message
#     for reaction in reactions:
#         await message.add_reaction(reaction)
    
#     # Save the dropped card info for each card in this drop
#     message_card_map[message.id] = all_card_info

#     # Update cooldown for the user
#     drop_cooldowns[user_id] = current_time


# @bot.command()
# async def drop(ctx):
#     user_id = ctx.author.id
#     channel = bot.get_channel(CHANNEL_ID)
#     cooldown_timer = 3600
#     current_time = time.time()

#     # Check cooldown
#     last_drop = drop_cooldowns.get(user_id, 0)
#     if current_time - last_drop < cooldown_timer:
#         remaining_time = cooldown_timer - (current_time - last_drop)
#         hours, remainder = divmod(remaining_time, 3600)
#         minutes, seconds = divmod(remainder, 60)
#         timer_message = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
#         await ctx.send(f"{ctx.author.mention}, please wait {timer_message} before dropping again!")
#         return

#     # Announce the drop
#     await channel.send(f"🚨 {ctx.author.mention} came to drop some photocards! 🚨")

#     # reactions
#     reactions = ["🫰", "🫶", "🥰"]

#     # Drop 3 random cards
#     dropped_cards = random.sample(cards, 3)
#     card_images = []
#     all_card_info = []  # List to store info for all dropped cards

#     for card in dropped_cards:
#         print(f"Attempting to download: {card['name']}")
#         card_img = download_image(card['image'])
#         frame_path = "./images/frame.png"
        
#         if card_img:
#             print(f"Downloaded: {card['name']}")
#             framed_card = add_frame_to_card(card_img, frame_path)
#             if framed_card:
#                 print(f"Framed: {card['name']}")
#                 card_images.append(framed_card)
#                 # Save card information for this card
#                 card_info = {
#                     "name": card['name'],
#                     "group": card['group'],
#                     "image": framed_card
#                 }
#                 all_card_info.append(card_info)
#             else:
#                 print(f"Failed to frame: {card['name']}")
#         else:
#             print(f"Failed to download: {card['name']}")

#     print(f"Total cards processed: {len(card_images)}")

#     # Merge the framed images horizontally with spacing
#     merged_image = merge_images_horizontally(card_images, spacing=30)
#     merged_image_path = "./images/merged_drop.png"
#     merged_image.save(merged_image_path)

#     # Send the merged image as one message
#     embed = discord.Embed(
#         title="✨ Card Drop! ✨",
#         description=f"{ctx.author.mention} just dropped some cards!",
#         color=discord.Color.blue()
#     )
#     file = discord.File(merged_image_path, filename="merged_drop.png")
#     embed.set_image(url="attachment://merged_drop.png")

#     message = await ctx.send(embed=embed, file=file)
    
#     # Add reactions to the message
#     for reaction in reactions:
#         await message.add_reaction(reaction)
    
#     # Save the dropped card info for each card in this drop
#     message_card_map[message.id] = all_card_info

#     # Update cooldown for the user
#     drop_cooldowns[user_id] = current_time


@bot.event
async def on_reaction_add(reaction, user):
    # ignore the bot's reactions
    if user == bot.user:
        return 
    
    user_id = user.id
    message_id = reaction.message.id

    # Get the card's info, the user grabs
    card = message_card_map.get(message_id)

    # check if card exists, return early if it doesn't
    if not card:
        return
    
    # add cooldown for grab
    cooldown_time = 3600 # seconds -> 1 hour
    current_time = time.time()

    # check if the user is on cooldown
    last_grab = grab_cooldowns.get(user_id, 0)
    if current_time - last_grab < cooldown_time:
        remaining_time = cooldown_time - (current_time - last_grab)
        hours, remainder = divmod(remaining_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_left = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        await reaction.message.channel.send(f"{user.mention} You already grabbed a photocard! Wait {time_left} before grabbing another!")
        return
    
    # if the user doesn't have an inventory, initialize it/create an inventory for them
    if user_id not in user_collection:
        user_collection[user_id] = []
    card = message_card_map.get(message_id)

    # Check if card exists and is a list with at least one item
    if not card or not isinstance(card, list):
        return

    # Access the first card in the list (assuming there's only one card per message)
    card = card[0]  # Now card is a dictionary
    

    # check if the card has already been grabbed by the user
    if card['image'] not in user_collection[user_id]:
        # Save the image path into the user's collection
        image_path = add_frame_to_card(card['image'], "frame_path.png")  # Use your actual frame path
        if image_path:
            user_collection[user_id].append(image_path)
        
        # update json file
        with open("collection.json", "w") as data_file:
            json.dump(user_collection, data_file, indent=4)

        # update cooldown
        grab_cooldowns[user_id] = current_time

        # send the message in the channel if user reacts to grab a card
        await reaction.message.channel.send(f"{user.mention} gained a **{card['name']}** photocard! 🤩")



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