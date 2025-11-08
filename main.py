import discord
import json
import os

from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():Okq
    return "I'm alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

client = discord.Client(intents=intents)

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
    print(f'We have logged in as {client.user}')
    load_counts()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.stickers:
        for sticker in message.stickers:
            sticker_id = str(sticker.id)
            sticker_counts[sticker_id] = sticker_counts.get(sticker_id, 0) + 1
            save_counts()  # save after each update
            print(f"Sticker {sticker.name} ({sticker_id}) count: {sticker_counts[sticker_id]}")

    if message.content.startswith('!slaystats'):
        if not sticker_counts:
            await message.channel.send("No emotes/stickers have been used yet.")
            return

        stats_message = "🫦 **Emote/Sticker Slays:**\n"
        for sticker_id, count in sorted(sticker_counts.items(), key=lambda item: item[1], reverse=True):
            sticker_obj = client.get_sticker(int(sticker_id))
            sticker_name = sticker_obj.name if sticker_obj else f"Sticker ID {sticker_id}"
            stats_message += f"> **{sticker_name}**: {count} uses\n"
        await message.channel.send(stats_message)

token = os.getenv("TOKEN")

if not token:
    raise ValueError("⚠️ No token found! Please check your .env file or environment variables.")

keep_alive()
client.run(token)



