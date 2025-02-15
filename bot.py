import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import random
import time
from images_helpers import download_image, resize_image, add_frame_to_card, merge_images_horizontally
from json_data_helpers import card_collection

# load environment variables from .env
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = 1339716688748216392

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# load card database at startup
cards = card_collection()

# initialize rarities
rarities = {
    "Common": 50,
    "Rare": 25,
    "Epic": 15,
    "Legendary": 10,
}

# initialize empty map to save card info
message_card_map = {}

# initialize drop cooldown to store user and times
drop_cooldowns = {}

# initialize grab cooldown to store user and times
grab_cooldowns = {}

# frame image's path
frame_path = "./images/frame.png"

# generate random rarity for each card when dropped
def assign_random_rarity(card):
    rarity = random.choices(list(rarities.keys()), list(rarities.values()), k=1)[0]
    card['rarity'] = rarity
    return card

# bot startup
@bot.event
async def on_ready():
    # Prints that the bot successful is up and running
    print(f"Yo! Mingyu bot ({bot.user}) has logged in.")
    channel = bot.get_channel(CHANNEL_ID)
    # send message to the channel
    await channel.send(f"Yo, Mingyu is here! Let's party!!")

# drop command
@bot.command()
async def drop(ctx):
    user_id = ctx.author.id
    channel = bot.get_channel(CHANNEL_ID)

    # send a message if !drop is used in the wrong channel
    if ctx.channel.id != CHANNEL_ID:
        await ctx.send(f"Hey! The photocards are not in this area.")
        return
    
    # cooldown timer
    cooldown_timer = 3600 # 1 hour
    current_time = time.time()

    # check if the user is on cooldown
    # last_drop = drop_cooldowns(user_id, 0)
    # if current_time - last_drop < cooldown_timer:
    #     remaining_time = cooldown_timer - (current_time - last_drop)
    #     hours, remainder = divmod(remaining_time, 3600)
    #     minutes, seconds = divmod(remainder, 60)
    #     timer_message = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
    #     await ctx.send(f"{ctx.author.mention}, please wait {timer_message} before dropping again!")
    #     return
    
    # Announce that user is dropping cards
    drop_message = await channel.send(f"🚨 {ctx.author.mention} came to drop some photocards! 🚨")
    print("Cards available for dropping: ", cards)

    # randomly select 3 cards from database
    dropped_cards = random.sample(cards, 3)

    # create embed for when user is dropping cards
    embed = discord.Embed(
        title="✨ Card Drop! ✨",
        description=f"{ctx.author.mention} just dropped some cards!",
        color=discord.Color.blue()
    )

    # Images for photos
    card_images = []
    for card in dropped_cards:
        assign_random_rarity(card)
        card_img = download_image(card['image'])
        if card_img:
            framed_card = add_frame_to_card(card_img, frame_path)
            if framed_card:
                card_images.append(framed_card)

    # update cooldown timer on the user
    # drop_cooldowns[user_id] = current_time

bot.run(TOKEN)