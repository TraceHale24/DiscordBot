from collections import namedtuple
from datetime import datetime, timedelta
import discord
from discord.ext import tasks
from dotenv import load_dotenv
import requests
import os
import sqlite3
import random
import schedule
import time
import threading

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
client = discord.Client(intents=intents)

# Read in users
with open("data.txt", "r") as f:
    cols = f.readline().split()
    User = namedtuple('User', cols)
    users = [User(*row.split()) for row in f.readlines()]
users.sort()

def create_reminder(content, channel_id):
    reminder_content = content.split(" ")
    if len(reminder_content) < 3:
        return "Structure is /reminder 2024-11-3T17:30 Message Goes Here"

    reminder_date_time = reminder_content[1].split("T")
    reminder_message = " ".join(reminder_content[2:])

    reminder_date = reminder_date_time[0].split("-")
    reminder_time = reminder_date_time[1].split(":")

    time_to_send = datetime(int(reminder_date[0]), int(reminder_date[1]), int(reminder_date[2]), int(reminder_time[0]), int(reminder_time[1]))
    sent = False
    tag_everyone = True

    # Insert the data into the events table
    conn = sqlite3.connect("DiscordBot.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO events (timeToSend, sent, message, tagEveryone)
        VALUES (?, ?, ?, ?)
    ''', (time_to_send, sent, reminder_message, tag_everyone))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    return "Reminder Created"

def create_scoreboard(content):
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
           '{:<7}{:>7}{:>9}{:>10}'.format('name', *COLUMNS[:-1], 'playTime')
           ]
    for user in users:
        headers = {'Authorization': os.getenv('API_KEY')}
        params = {'name': user.user,
                  'accountType': user.accountType,
                  'timeWindow': TIME_WINDOW,
                  'image': 'none'
                  }

        r = requests.get('https://fortnite-api.com/v2/stats/br/v2',
                         params=params,
                         headers=headers).json()

        print(r)
        if r['status'] != 200:
            continue

        stats = r['data']['stats']['all'][MODE]

        if stats:
            res.append('{:<7}{:>7.3f}{:>9.3f}{:>10}'.format(
                user.name, *[stats[col] for col in COLUMNS]))
        else:
            res.append('{:<7}{:>7}{:>9}{:>10}'.format(
                user.name, *['NONE']*3))

    res.append('```')
    return '\n'.join(res)

async def check_events():
    """Check for events whose timeToSend has passed and process them."""
    now = datetime.now()
    conn = sqlite3.connect("DiscordBot.db")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT message FROM events WHERE timeToSend <= ? AND sent = 0
    ''', (now,))
    
    events_to_send = cursor.fetchall()
    channel = client.get_channel(960725761973690398)
    for event in events_to_send:
        message = event[0]
        # Here you would add your logic to send the message (e.g., to a Discord channel)

        await channel.send(f"@everyone {message}")
        
        # Update the event to mark it as sent
        cursor.execute('''
            UPDATE events SET sent = 1 WHERE message = ?
        ''', (message,))
    
    conn.commit()
    conn.close()


@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my Discord Server!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("/scoreboard"):
        m = await message.channel.send("Generating scoreboard...")
        res = create_scoreboard(message.content)
        await m.edit(content=res)

    if message.content.startswith("/reminder"):
        result = create_reminder(message.content, message.channel)
        await message.reply(result)


@tasks.loop(minutes=5)
async def scheduled_event_check():
    await check_events()

@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')
    scheduled_event_check.start() 

client.run(TOKEN)
