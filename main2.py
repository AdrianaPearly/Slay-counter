import discord
import os
import json

# Load config
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

token = config.get("TOKEN")
if not token:
    raise ValueError("⚠️ No TOKEN found in config.json")

# Discord intents
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True

client = discord.Client(intents=intents)

# Sticker stats database
DB_FILE = 'sticker_counts.json'
sticker_counts = {}

def load_counts():
    global sticker_counts
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            sticker_counts = json.load(f)
        print(f"Loaded {len(sticker_counts)} sticker counts.")
    else:
        sticker_counts = {}

def save_counts():
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(sticker_counts, f, indent=2, ensure_ascii=False)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    load_counts()
    print(f"Connected to {len(client.guilds)} guilds.")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Count stickers
    if message.stickers:
        for sticker in message.stickers:
            sticker_id = str(sticker.id)
            sticker_counts[sticker_id] = sticker_counts.get(sticker_id, 0) + 1
            save_counts()
            print(f"Sticker {sticker.name} ({sticker_id}) used {sticker_counts[sticker_id]} times.")

    # Stats command
    if message.content.startswith('!slaystats'):
        if not sticker_counts:
            await message.channel.send("No stickers have been used yet.")
            return

        stats_message = "🫦 **Emote/Sticker Stats:**\n"
        for sticker_id, count in sorted(sticker_counts.items(), key=lambda x: x[1], reverse=True):
            sticker_obj = client.get_sticker(int(sticker_id))
            name = sticker_obj.name if sticker_obj else f"ID {sticker_id}"
            stats_message += f"> **{name}**: {count} uses\n"

        await message.channel.send(stats_message)

client.run(token)
