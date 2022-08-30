import asyncio
import datetime
import discord
from dotenv import load_dotenv
import os
import requests

load_dotenv()

SERVER = os.getenv("SERVER")
UPDATE_FREQUENCY = os.getenv("UPDATE_FREQUENCY")
TOKEN = os.getenv("TOKEN")

DECIMAL_PLACES = 2

ICON_PATH = "src/icon.jpeg"
ICON = open(ICON_PATH, "rb")
ICON_BYTES = ICON.read()

intents = discord.Intents(guilds=True, messages=True, message_content=True)
client = discord.Client(intents=intents)


def fetch_info():
    res = requests.get(f"{SERVER}/admin/api.php")
    if res.status_code == 200:
        return res.json()


def build_embed(title="", description="", fields=[], color=0x239dd1):
    embed = discord.Embed(title=title, description=description, timestamp=datetime.datetime.now(), color=color)

    for field in fields:
        embed.add_field(name=field.get("name"), value=field.get("value"), inline=field.get("inline"))

    embed.set_footer(text=f"Pi-Hole Discord")

    return embed


async def help_command(channel_id):
    embed = build_embed("All Commands", "`!stats - Get All Stats`")
    await client.get_channel(channel_id).send(embed=embed)


async def show_stats(channel_id):
    info = fetch_info()
    domains_being_blocked = "`{:,}`".format(info.get("domains_being_blocked"))
    dns_queries_today = "`{:,}`".format(info.get("dns_queries_today"))
    ads_blocked_today = "`{:,}`".format(info.get("ads_blocked_today"))
    ads_percentage_today = "`{:,.2f}%`".format(info.get("ads_percentage_today"))

    fields = [
        {"name": "Total Queries", "value": dns_queries_today, "inline": False},
        {"name": "Queries Blocked", "value": ads_blocked_today, "inline": False},
        {"name": "Percentage Blocked", "value": ads_percentage_today, "inline": False},
        {"name": "Domains on Adlists", "value": domains_being_blocked, "inline": False},
    ]

    embed = build_embed(title="Stats", fields=fields)

    await client.get_channel(channel_id).send(embed=embed)


async def update_bot():
    info = fetch_info()
    ads_blocked_today = "{:,}".format(info.get("ads_blocked_today"))

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

    while True:
        await update_bot()

while True:
    client.run(TOKEN)
    client.user.edit(avatar=ICON_BYTES)
