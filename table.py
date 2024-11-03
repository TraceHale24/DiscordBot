import sqlite3

# Connect to SQLite database (creates a file if it doesn’t exist)
conn = sqlite3.connect("DiscordBot.db")
cursor = conn.cursor()

# Create the events table with specified columns
cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timeToSend DATETIME NOT NULL,
        sent BOOLEAN NOT NULL DEFAULT 0,
        message TEXT NOT NULL,
        tagEveryone BOOLEAN NOT NULL DEFAULT 0
    )
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Table 'events' created successfully.")
