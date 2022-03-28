# bot.py
import os
from datetime import datetime
import discord
import mysql.connector
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
#GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()
user_data = {}
f = open("data.txt", "r")
data = f.readlines()
for line in data:
    vals = line.split(" ")
    user_data[vals[0]] = vals[1][:-1]

f.close()

def read_polls():
    polls = []
    poll_file = open("polls.txt", "r")
    poll_data = poll_file.readlines()
    for j in range(len(poll_data)):
        split_poll = poll_data[j].split("] [")
        row = []
        for i in range(len(split_poll)):
            word = split_poll[i]
            if j != len(poll_data) - 1 and i == 2:
                word = word[:-1]
            if i == 0:
                word = word[1:]
            elif ']' in word:
                word = word[:-1]
            row.append(word)
        polls.append(row)
    poll_file.close()
    return polls


def get_remaining_time(end):
    start_time = datetime.now()
    time_split = end.split(" ")
    time_split_end = time_split[3].split(":")
    end_time = datetime(int(time_split[2]), int(time_split[0]), int(time_split[1]), int(time_split_end[0]), int(time_split_end[1]), int(time_split_end[2]))
    remaining_time = end_time - start_time
    if remaining_time.days == 0:
        return "0 Days, " + str(remaining_time) + " Left"
    return str(remaining_time) + " Left"

def print_polls(pollVals):
    output = "Name\tDescription\tRemaining\n"
    for row in pollVals:
        time_left = get_remaining_time(row[2])
        output += row[0] + "\t" + row[1] + "\t" + str(time_left) + "\n"
    return output


def create_poll(poll_info):
    f_read = open("polls.txt", "r")

    polls = f_read.readlines()
    f_read.close()
    poll_info = poll_info[12:]
    f = open("polls.txt", "w+")
    for data in polls:
        f.write(data + "\n")
    f.write(poll_info)
    f.close()



@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')


@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my Discord Server!')
    # user_data[member.name] = member.userId#
    # Write the username to the data.txt so make sure its updated.
    # f.write(user_data[member.name] + " " + member.userId)


@client.event
async def on_message(message):
    print(message.author)
    if message.author == client.user:
        return
    temp = "This is a test message for the Python Bot Version"
    if message.content.lower() == "Test":
        await message.channel.send(temp)

    if "/polls" == message.content:
        res = print_polls(read_polls())
        await message.channel.send(res)
    if "/createpoll" in message.content:
        create_poll(message.content)





client.run(TOKEN)