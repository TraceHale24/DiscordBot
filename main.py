# bot.py
from collections import namedtuple
from datetime import datetime, timedelta
import discord
from dotenv import load_dotenv
import requests
import os
import sqlite3
import random

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
OPTIONS = [('🟥', '\U0001F7E5'), ('🟦', '\U0001F7E6'), ('🟨', '\U0001F7E8'),
           ('🟩', '\U0001F7E9'), ('🟧', '\U0001F7E7'), ('🟪', '\U0001F7EA')]

intents = discord.Intents.all()
client = discord.Client(intents=intents)

# read in users
with open("data.txt", "r") as f:
    cols = f.readline().split()
    User = namedtuple('User', cols)
    users = [User(*row.split()) for row in f.readlines()]
users.sort()

def show_polls(message):
    db = sqlite3.connect("polls.db")
    cursor = db.cursor()
    query = "SELECT * FROM Polls WHERE endTime > {}".format(
        datetime.now().timestamp())
    poll_data = cursor.execute(query).fetchall()

    res = []
    for i in range(len(poll_data)):
        row = list(poll_data[i])
        res.append("{}?\nEnds {}\nLink: {}".format(
            row[0], datetime.fromtimestamp(float(row[3])).ctime(), row[4]))

    cursor.close()
    db.close()
    return '\n\n'.join(res)


async def add_poll(message):
    try:
        # parse out parameters
        name_raw, params_raw = message.content.split("? ")
        name = name_raw.split("/createpoll ")[1]
        *options, duration = params_raw.split("; ")
        if not (1 < len(options) <= len(OPTIONS)):
            raise Exception("too many poll options")

        # split up duration
        D, H, M, S = map(int, duration.split(":"))
        endTime = (message.created_at + timedelta(days=D,
                   hours=H, minutes=M, seconds=S)).timestamp()

        # send message, initialize voting options
        voting = '\n'.join(['{}  {}'.format(OPTIONS[i][0], options[i])
                           for i in range(len(options))])
        result = await message.channel.send("Poll Created:\n{}?\n{}".format(name, voting))
        for _, code in OPTIONS[:len(options)]:
            await result.add_reaction(code)

        # store poll in database
        db = sqlite3.connect("polls.db")
        cursor = db.cursor()
        query = """INSERT INTO Polls 
        (name, options, endTime, messageID) 
        VALUES (?, ?, ?, ?)"""
        data_tuple = (name, ",".join(options), endTime, result.jump_url)
        cursor.execute(query, data_tuple)
        db.commit()
        cursor.close()
        db.close()

    except:
        await message.channel.send("Usage: `[Name of Poll]? [Option1]; [Option2]; ... [Option{}]; [DD]:[HH]:[MM]:[SS]`, where the given time is how long the poll should last".format(len(OPTIONS)))


def create_scoreboard(content):
    # constants to be used in API calls
    COLUMNS = ['kd', 'winRate', 'minutesPlayed']
    TIME_WINDOW = 'lifetime' if 'lifetime' in content else 'season'
    for m in ['solo', 'duo', 'squad']:
        if m in content:
            MODE = m
            break
    else:
        MODE = 'overall'

    # generate scoreboard message
    res = ['```',
           '{} scoreboard ({})'.format(MODE, TIME_WINDOW),
           '{:<7}{:>8}{:>9}{:>15}'.format('name', *COLUMNS)
           ]
    for user in users:
        headers = {'Authorization': 'cd4ed170-0db8-4ecd-9744-2d60fd0a6648'}
        params = {'name': user.user,
                  'accountType': user.accountType,
                  'timeWindow': TIME_WINDOW,
                  'image': 'none'
                  }

        r = requests.get('https://fortnite-api.com/v2/stats/br/v2',
                         params=params,
                         headers=headers).json()
        stats = r['data']['stats']['all'][MODE]

        if stats:
            res.append('{:<7}{:>8.3f}{:>9.3f}{:>15}'.format(
                user.name, *[stats[col] for col in COLUMNS]))
        else:
            res.append('{:<7}{:>8}{:>9}{:>15}'.format(
                user.name, *['NONE']*3))

    res.append('```')
    return '\n'.join(res)


def fortnite_blast(nickname, channel):
    status = ["trying to get some dubs", "online",
              "in need of party members", "playing a few rounds"]
    call_to_arms = ["Ready up", "Squad up", "Hop on now" "Join them"]
    return "{} is {}. {}!".format(nickname, random.choice(status), random.choice(call_to_arms))


@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')


@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my Discord Server!')
    # note: this process will need to be updated now, because users is a list of namedtuples now
    # user_data[member.name] = member.userId#
    # Write the username to the data.txt so make sure its updated.
    # f.write(user_data[member.name] + " " + member.userId)


@client.event
async def on_member_update(before, after):
    if after.activity and before.activity != after.activity:
        if "fortnite" in after.activity.name.lower():
            channel = client.get_channel(945836161451061258)
            await channel.send(fortnite_blast(after.nick, channel))
        if "pycharm" in after.activity.name.lower():
            channel = client.get_channel(945846689237958667)
            await channel.send(f"{after.display_name} is working on my body ;)")

        else:
            channel = client.get_channel(945782914019377154)
            await channel.send(f"{after.display_name} has started doing {after.activity.name}")




@client.event
async def on_message(message):
    # print(message.author)
    if message.author == client.user:
        return

    if message.content == "/polls":
        res = show_polls(message)
        await message.channel.send(res)
    if message.content.startswith("/createpoll"):
        await add_poll(message)
    if message.content.startswith("/scoreboard"):
        m = await message.channel.send("Generating scoreboard...")
        res = create_scoreboard(message.content)
        await m.edit(res)

    ur_mom = random.randint(0, 100)
    if ur_mom == 69 or ("who" in message.content and not random.randint(0, 4)):
        await message.reply("ur mom lol")


client.run(TOKEN)
