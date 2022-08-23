import asyncio
import discord
from dotenv import load_dotenv
import os
import requests
from datetime import datetime

load_dotenv()

SERVER = os.getenv("SERVER")
UPDATE_FREQUENCY = os.getenv("UPDATE_FREQUENCY")
DECIMAL_PLACES = os.getenv("DECIMAL_PLACES")
TOKEN = os.getenv("TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

ICON_PATH = "src/icon.jpeg"
ICON = open(ICON_PATH, "rb")
ICON_BYTES = ICON.read()

client = discord.Client()


def fetch_info():
    res = requests.get(f"{SERVER}/admin/api.php")
    if res.status_code == 200:
        return res.json()


def build_embed(title, description, color=0x239dd1):
    embed = discord.Embed(title=title, description=description, color=color)

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    embed.set_footer(text=f"Pi-Hole Discord | {current_time}")

    return embed


async def help_command(channel_id):
    embed = build_embed("All Commands", "`!stats - Get All Stats`")
    await client.get_channel(channel_id).send(embed=embed)


async def show_stats(channel_id):
    info = fetch_info()
    domains_being_blocked = "{:,}".format(info.get("domains_being_blocked"))
    dns_queries_today = "{:,}".format(info.get("dns_queries_today"))
    ads_blocked_today = "{:,}".format(info.get("ads_blocked_today"))
    ads_percentage_today = "{:,.2f}".format(info.get("ads_percentage_today"))

    description = ""
    description += f"Total Queries: {dns_queries_today}\n"
    description += f"Queries Blocked: {ads_blocked_today}\n"
    description += f"Percentage Blocked: {ads_percentage_today}%\n"
    description += f"Domains on Adlists: {domains_being_blocked}\n"
    embed = build_embed(title="Stats", description=description)

    await client.get_channel(channel_id).send(embed=embed)


async def update_bot():
    info = fetch_info()
    ads_blocked_today = "{:,}".format(info.get("ads_blocked_today"))
    ads_percentage_today = "{:,.2f}".format(info.get("ads_percentage_today"))

    ads_blocked = f"Pi-Hole | {ads_blocked_today} ads blocked today."

    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=ads_blocked))
    await asyncio.sleep(int(UPDATE_FREQUENCY))


@client.event
async def on_message(message):
    commands = {
        "!help": help_command,
        "!stats": show_stats
    }

    content = message.content
    channel_id = message.channel.id

    if content in commands:
        await commands[content](channel_id)


@client.event
async def on_ready():
    print(f"Logged in as Username: {client.user.name}")
    print(f"User ID: {client.user.id}")
    print("-----------")
    await client.user.edit(avatar=ICON_BYTES)

    while True:
        await update_bot()

while True:
    client.run(TOKEN)
