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

@client.event
async def on_ready():
  print(f"Logged in as Username: {client.user.name}")
  print(f"User ID: {client.user.id}")
  print("-----------")

  while True:
    await update_bot()

while True:
  client.run(TOKEN)