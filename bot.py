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

# initialize a list of cards
cards = [
    {"name": "Chaewon", "group": "LESSERAFIM", "image": "https://cdn.discordapp.com/attachments/1339477207541878814/1339728557601193994/FQtyWk0XEAgLOKp.png?ex=67afc6f3&is=67ae7573&hm=994356a547f7d9359d241c2b4a1a4a5c3f63b32bb0792a1e1a798f722692d03e&" },
    {"name": "Yujin", "group": "IVE", "image": "https://cdn.discordapp.com/attachments/1339477207541878814/1339729192191000739/image.png?ex=67afc78a&is=67ae760a&hm=e6f252d54685294351fc906ad6570efa6505b5ac5e0f14e04e77a18985fcbcbc&" },
    {"name": "Rosé", "group": "BLACKPINK", "image": "https://cdn.discordapp.com/attachments/1339289261651787786/1339730876677881876/thumb-qui-est-rose-des-blackpink-premier-album-rosie-apt-kpop.png?ex=67afc91b&is=67ae779b&hm=94ba48d5d208b1da58333863fbd5e66b7f779421506fa52be1832981f697955a&"}, 
]

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

# initialize user's collection
user_collection = {}

frame_path = "./images/frame.png"

# load data
if os.path.exists("collection.json"):
    with open("collection.json", "r") as data_file:
        user_collection = json.load(data_file)

# save data
with open("collection.json", "w") as data_file:
    json.dump(user_collection, data_file, indent=4)


@bot.event
async def on_ready():
    print("Mingyu Bot just logged in!")
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send(f"Yo! Mingyu bot just logged in.")



@bot.command()
async def drop(ctx):
    user_id = ctx.author.id
    channel = bot.get_channel(CHANNEL_ID)
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

    # Drop 3 random cards
    dropped_cards = random.sample(cards, 3)
    card_images = []

    # reactions
    reactions = ["🫰", "🫶", "🥰"]

    for card in dropped_cards:
        print(f"Attempting to download: {card['name']}")
        card_img = download_image(card['image'])
        frame_path = "./images/frame.png"
        
        if card_img:
            print(f"Downloaded: {card['name']}")
            framed_card = add_frame_to_card(card_img, frame_path)
            if framed_card:
                print(f"Framed: {card['name']}")
                card_images.append(framed_card)
            else:
                print(f"Failed to frame: {card['name']}")
        else:
            print(f"Failed to download: {card['name']}")

    print(f"Total cards processed: {len(card_images)}")

    # Merge the framed images horizontally with spacing
    merged_image = merge_images_horizontally(card_images, spacing=30)
    merged_image_path = "./images/merged_drop.png"
    merged_image.save(merged_image_path)

    # Send the merged image as one message
    embed = discord.Embed(
        title="✨ Card Drop! ✨",
        description=f"{ctx.author.mention} just dropped some cards!",
        color=discord.Color.blue()
    )
    file = discord.File(merged_image_path, filename="merged_drop.png")
    embed.set_image(url="attachment://merged_drop.png")

    message = await ctx.send(embed=embed, file=file)
    # Add reactions to the message
    for index, reaction in enumerate(reactions):
        await message.add_reaction(reaction)

    drop_cooldowns[user_id] = current_time




# @bot.command()
# async def drop(ctx):
#     # retrieve the user's id, the person who used the command
#     user_id = ctx.author.id
#     channel = bot.get_channel(CHANNEL_ID)
    
#     cooldown_timer = 3600
#     current_time = time.time()

#     last_drop = drop_cooldowns.get(user_id, 0)
#     if current_time - last_drop < cooldown_timer:
#         remaining_time = cooldown_timer - (current_time - last_drop)

#         hours, remainder = divmod(remaining_time, cooldown_timer)
#         minutes, seconds = divmod(remainder, 60)
#         timer_message = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"

#         await ctx.send(f"{ctx.author.mention}, you already dropped cards! Please wait {timer_message} until dropping again!")
#         return

#     await channel.send(f"🚨 {ctx.author.mention} came to drop some photocards! 🚨")

#     # drop 3 random cards from cards list
#     dropped_cards = random.sample(cards, 3)

#     reactions = ["🫰", "🫶", "🥰"]

#     # store resized images
#     card_images = []

#     for index, card in enumerate(dropped_cards):
#         # randomly assign rarity
#         rarity = random.choices(list(rarities.keys()), weights=rarities.values(), k=1)[0]
        
#         card_url = card['image']
#         frame_path = os.path.join(os.getcwd(), "images", "frame.png")  # Path to the frame image

#         # download image
#         card_img = download_image(card_url)

#         if card_img:
#             resized_card_img, resized_frame = resize_image(card_img, frame_path)
#             # Add frame to the card image
#             framed_card = add_frame_to_card(resized_card_img, resized_frame)

#             if framed_card:
#                 # Save the framed card image to a path
#                 framed_card_path = "framed_card.png"
#                 framed_card.save(framed_card_path)

#                 # Create embed for the card
#                 embed = discord.Embed(
#                     title=f"{rarity} Card Dropped!",
#                     description=f"**{card['name']}** - **{card['group']}**",
#                     color=discord.Color.blue()
#                 )

#                 merged_images = merge_images(card_images)
#                 merged_image_path = "merged_cards.png"
#                 merged_images.save(merged_image_path)

#                 # Create the Discord file object using the saved framed card path
#                 file = discord.File(merged_image_path, filename="merged_card.png")
                
#                 # Attach the image in the embed
#                 embed.set_image(url="attachment://merged_card.png")
                
#                 # Send the embed with the image and file
#                 message = await ctx.send(embed=embed, file=file)
                
#                 # Add reactions to the message
#                 for index, reaction in enumerate(reactions):
#                     await message.add_reaction(reaction)

#                 # card info
#                 card_info = {
#                     "name": card['name'],
#                     "group": card['group'],
#                     "rarity": rarity,
#                     "image": framed_card_path,
#                 }

#                 # store card info
#                 message_card_map[message.id] = card_info

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
        hours, remainder = divmod(remaining_time, cooldown_time)
        minutes, seconds = divmod(remainder, 60)
        time_left = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        await reaction.message.channel.send(f"{user.mention} You already grabbed a photocard! Wait {time_left} before grabbing another!")
        return
    
    # if the user doesn't have an inventory, initialize it/create an inventory for them
    if user_id not in user_collection:
        user_collection[user_id] = []

    # add to the user's collection if they haven't grabbed it already
    if card not in user_collection[user_id]:
        user_collection[user_id].append(card)

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