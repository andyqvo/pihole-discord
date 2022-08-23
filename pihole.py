import asyncio
import discord
from dotenv import load_dotenv
import os
import requests

load_dotenv()

SERVER = os.getenv("SERVER")
UPDATE_FREQUENCY = os.getenv("UPDATE_FREQUENCY")
DECIMAL_PLACES = os.getenv("DECIMAL_PLACES")
TOKEN = os.getenv("TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

client = discord.Client()

def fetch_info():
  res = requests.get(f"{SERVER}/admin/api.php")
  if res.status_code == 200:
    return res.json()

async def update_bot():
  info = fetch_info()
  ads_blocked_today = info.get("ads_blocked_today")
  ads_percentage_today = info.get("ads_percentage_today")

  bot_name_ads_blocked = f"{ads_blocked_today} ads blocked."
  bot_status_ads_percentage = f"Pi-Hole | {round(ads_percentage_today, int(DECIMAL_PLACES))}% ads today."

  await client.get_guild(int(GUILD_ID)).me.edit(nick=bot_name_ads_blocked)
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=bot_status_ads_percentage))
  await asyncio.sleep(int(UPDATE_FREQUENCY))

async def help_command(channel_id):
  embed = discord.Embed(title="All Commands", description="`!stats - Get All Stats`", color=0x239dd1)
  await client.get_channel(channel_id).send(embed=embed)

async def show_stats(channel_id):
  info = fetch_info()
  domains_being_blocked = info.get("domains_being_blocked")
  dns_queries_today = info.get("dns_queries_today")
  ads_blocked_today = info.get("ads_blocked_today")
  ads_percentage_today = round(info.get("ads_percentage_today"), int(DECIMAL_PLACES))

  description = ""
  description += f"Domains being blocked: {domains_being_blocked}\n"
  description += f"DNS queries today: {dns_queries_today}\n"
  description += f"Ads blocked today: {ads_blocked_today}\n"
  description += f"Ads percentage today: {ads_percentage_today}\n"
  embed = discord.Embed(title="Stats", description=description, color=0x239dd1)

  await client.get_channel(channel_id).send(embed=embed)

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