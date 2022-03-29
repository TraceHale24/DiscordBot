# DiscordBot

## Files

### `main.py`
The bot. There is a lot going on in this file, but some key things from this file are:
- `@client.event` functions are things that the bot is listening for
- `on_message` is where text-based commands will be added
- Functions prior to the `@client.event` section are helper functions for the events being watched by the bot

### `data.txt`
This contains the different users in the Discord server, along with the information necessary to complete Fortnite API calls (such as generating scoreboards).

### `polls.db`
This is a SQLite database containing a table of the different polls that have been or are being conducted on the server.
