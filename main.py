# bot.py
from collections import namedtuple
from datetime import datetime
import discord
from dotenv import load_dotenv
import mysql.connector
import requests
import os
import sqlite3


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()
# read in users
with open("data.txt", "r") as f:
    cols = f.readline().split()
    User = namedtuple('User', cols)
    users = [User(*row.split()) for row in f.readlines()]
users.sort()

def get_time_remaining(end_time, interval = "default"):
    now = datetime.now()
    end_time_split = end_time.split(":")
    year_hour = end_time_split[2].split(" ")
    second, minutes, hours, days, months, years = end_time_split[4], end_time_split[3], year_hour[1], end_time_split[1], end_time_split[0], year_hour[0]
    end = datetime(int(years), int(months), int(days), int(hours), int(minutes), int(second))
    duration = end - now
    duration_in_s = duration.total_seconds()

    #days
    days = (duration_in_s // 86400)
    duration_in_s %= 86400
    hours = (duration_in_s // 3600)
    duration_in_s %= 3600
    minutes = duration_in_s // 60
    duration_in_s %= 60
    seconds = duration_in_s

    return [days, hours, minutes, seconds]

def show_polls(message):
    db = sqlite3.connect("polls.db")
    cursor = db.cursor()
    query = """SELECT * FROM Polls"""
    poll_data = cursor.execute(query).fetchall()
    res = ""
    for i in range(len(poll_data)):
        poll_data[i] = list(poll_data[i])
        time_remaining = get_time_remaining(poll_data[i][3])

        res += poll_data[i][0] + " \nEnds in: " + \
               str(int(time_remaining[0])) + " Days " + \
               str(int(time_remaining[1])) + " Hours " + \
               str(int(time_remaining[2])) +" Minutes "+ \
               str(int(time_remaining[3])) + " Seconds \nLINK: " + poll_data[i][4] + "\n"

    cursor.close()
    db.close()
    return res


async def add_poll(message):
    split_name = message.content.split("\"")
    if len(split_name) != 8:
        name = split_name[1]
        opOne = split_name[3]
        opTwo = split_name[5]
        endTime = split_name[7]
        db = sqlite3.connect("polls.db")
        cursor = db.cursor()
        result = await message.channel.send(f"@everyone Poll Created:\n {name}\n🟦 for {opOne} and 🟥 for {opTwo}")
        await result.add_reaction("\U0001F7E6")
        await result.add_reaction("\U0001F7E5")

        query = """INSERT INTO Polls 
        (name, optionOne, optionTwo, endTime, messageID) 
        VALUES
        (?, ?, ?, ?, ?)"""
        data_tuple = (name, opOne, opTwo, endTime, result.jump_url)
        cursor.execute(query, data_tuple)
        db.commit()
        cursor.close()
        db.close()

    else:
        await message.channel.send("Usage \"Name of Poll\" \"OptionOne\" \"OptionTwo\" \"(End Time) MM:DD:YYYY HH:MM:SS\"")




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
async def on_message(message):
    print(message.author)
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



client.run(TOKEN)
