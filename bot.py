import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import random
import time
import json

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
    {"name": "Jungkook", "group": "BTS", "image": "https://cdn.discordapp.com/attachments/1339474263769485323/1339475981286506496/8b5104036f8271731ba6ab5845b9900b.png?ex=67af8478&is=67ae32f8&hm=4b8e50b6ef8373df6526017a4a1c1b58ba95b486b7e3471d502eee782c0fe062&" },
    {"name": "Sophia", "group": "KATSEYE", "image": "https://cdn.discordapp.com/attachments/1339477207541878814/1339478432475512903/IMG3301-R01-007A-copy-compressed-819x1024.png?ex=67aede00&is=67ad8c80&hm=aed2167b15b8f36bd1591c44f65d815e166601913a4e167c1818d3a405dd3e02&"},
    {"name": "Rosé", "group": "BLACKPINK", "image": "https://cdn.discordapp.com/attachments/1339289261651787786/1339730876677881876/thumb-qui-est-rose-des-blackpink-premier-album-rosie-apt-kpop.png?ex=67afc91b&is=67ae779b&hm=94ba48d5d208b1da58333863fbd5e66b7f779421506fa52be1832981f697955a&"},
    {"name": "Wonyoung", "group": "IVE", "image": "https://cdn.discordapp.com/attachments/1339289261651787786/1339350547576389824/18979de98b5294c93dbb99321f3ba50f.png?ex=67afb866&is=67ae66e6&hm=440d9e01ed5ab27df207808c2016772643639c9971ecba583b19d5f9fc8c711b&"},
    {"name": "Mingyu", "group": "SEVENTEEN", "image": "https://cdn.discordapp.com/attachments/1339289261651787786/1339351397530992650/image.png?ex=67afb931&is=67ae67b1&hm=94161996d979599bd52a36f1675239e5aa1209f9fd4dd7966a09b5b3b362877d&"},
    {"name": "Karina", "group": "aespa", "image": "https://cdn.discordapp.com/attachments/1339289261651787786/1339351625156005949/bed76e498a0f9a3e20d9c43901e4a324.png?ex=67afb967&is=67ae67e7&hm=cbf19ed3a87486fac26fa998f0c8c033c04fd484783f40b28091c99c1892e836&"},
    {"name": "Jennie", "group": "BLACKPINK", "image": "https://cdn.discordapp.com/attachments/1339289261651787786/1339350341073768469/EwmnwoSWEAIjnrm.png?ex=67afb835&is=67ae66b5&hm=9925e175a00e3ae71e259947700c08df89df5e939349f3831829148df63c304b&"},    
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

# load data
try:
    with open("collection.json", "r") as data_file:
        usercollection = json.load(data_file)
except FileNotFoundError:
    # initialize user's collection
    user_collection = {}

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
    # retrieve the user's id, the person who used the command
    user_id = ctx.author.id
    channel = bot.get_channel(CHANNEL_ID)
    
    cooldown_timer = 3600
    current_time = time.time()

    last_drop = drop_cooldowns.get(user_id, 0)
    if current_time - last_drop < cooldown_timer:
        remaining_time = cooldown_timer - (current_time - last_drop)

        hours, remainder = divmod(remaining_time, cooldown_timer)
        minutes, seconds = divmod(remainder, 60)
        timer_message = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"

        await ctx.send(f"{ctx.author.mention}, you already dropped cards! Please wait {timer_message} until dropping again!")
        return
    # when the user uses !drop, this will print
    await channel.send(f"🚨 {ctx.author.mention} came to drop some photocards! 🚨")

    # drop 3 random cards from cards list
    dropped_cards = random.sample(cards, 3)

    # reactions in order of cards
    reactions = ["🫰", "🫶", "🥰"]

    for index, card in enumerate(dropped_cards):
        # randomly assign rarity
        rarity = random.choices(list(rarities.keys()), weights=rarities.values(), k=1)[0]

        # create embed for each card
        embed = discord.Embed(
            title=f"{rarity} Card Dropped!",
            description=f"**{card['name']}** - **{card['group']}**",
            color=discord.Color.blue()
        )
        embed.set_image(url=card['image'])

        # send embed 
        message = await ctx.send(embed=embed)

        # add the reactions to message
        await message.add_reaction(reactions[index])

        # card info
        card_info = {
            "name": card['name'],
            "group": card['group'],
            "rarity": rarity,
            "image": card['image'],
        }

        # store card info
        message_card_map[message.id] = card_info
    drop_cooldowns[user_id] = current_time

@bot.event
async def on_reaction_add(reaction, user):
    # ignore the bot's reactions
    if user == bot.user:
        return 
    
    user_id = user.id
    message_id = reaction.message.id

    # Get the card's info, the user grabs
    card = message_card_map.get(message_id)

    # check if card exists
    if not card:
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