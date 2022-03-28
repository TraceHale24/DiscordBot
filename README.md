# DiscordBot

## Files

### `main.py`
The bot. There is a lot going on in this file, but some key things from this file are:
- `@client.event` functions are things that the bot is listening for
- `on_message` is where text-based commands will be added
- Functions prior to the `@client.event` section are helper functions for the events being watched by the bot

### `data.txt`
This contains the different users in the Discord server. It's not being used anywhere at the moment, but it will be in the future.

### `polls.txt`
This is a log of the different polls that have been conducted on the server. It will be used a bit more in-depth eventually.

### `users.txt`
This is used to generate scoreboards. The content from this file should probably be merged with the content from `data.txt` at some point.
