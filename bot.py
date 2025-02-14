import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import random
import time

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

# initialize grab cooldown
grab_cooldowns = {}


@bot.event
async def on_ready():
    print("Mingyu Bot just logged in!")
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send(f"Yo! Mingyu bot just logged in.")

@bot.command()
@commands.cooldown(1, 3600, commands.BucketType.user)
async def drop(ctx):
    # retrieve the user's id, the person who used the command
    user_id = ctx.author.id
    channel = bot.get_channel(CHANNEL_ID)
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
    await reaction.message.channel.send(f"{user.mention} gained a **{card['name']}** photocard! 🤭")


@drop.error
async def drop_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"{ctx.author.mention}, you need to wait {round(error.retry_after)} seconds before using the command again.")


bot.run(TOKEN)