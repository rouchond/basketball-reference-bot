import discord
from discord.ext import commands, tasks
import os
import json
import asyncio
from itertools import cycle

#Load server prefixes
def get_server_prefix(client, message):
  with open("./cogs/jsonfiles/prefixes.json", "r") as f:
    prefix = json.load(f)

  return prefix[str(message.guild.id)]

client = commands.Bot(command_prefix=get_server_prefix, intents=discord.Intents.all())

client.remove_command("help")

#Start the bot
@client.event
async def on_ready():
  await client.tree.sync()
  await client.change_presence(activity=discord.Game("type in '$help' for help"))
  print("Success: Bot is connected to Discord!")

#Save Server Prefixes
@client.event
async def on_guild_join(guild):
  with open("./cogs/jsonfiles/prefixes.json", "r") as f:
    prefix = json.load(f)

  prefix[str(guild.id)] = "$"

  with open("./cogs/jsonfiles/prefixes.json", "w") as f:
    json.dump(prefix, f, indent=4)

#Delete Server Prefixes
@client.event
async def on_guild_remove(guild):
  with open("./cogs/jsonfiles/prefixes.json", "r") as f:
    prefix = json.load(f)

  prefix.pop(str(guild.id))

  with open("./cogs/jsonfiles/prefixes.json", "w") as f:
    json.dump(prefix, f, indent=4)

#Set Prefix
@client.command()
async def set_prefix(ctx, *, newprefix: str):
  with open("./cogs/jsonfiles/prefixes.json", "r") as f:
    prefix = json.load(f)

  prefix[str(ctx.guild.id)] = newprefix

  with open("./cogs/jsonfiles/prefixes.json", "w") as f:
    json.dump(prefix, f, indent=4)

#Load in cogs
async def load():
  for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
      await client.load_extension(f"cogs.{filename[:-3]}")
      print(f"{filename[:-3]} is loaded")

#Start Discord Bot
async def main():
  async with client:
    await load()

    with open("api_key.txt", "r") as f:
      await client.start(f.read())

asyncio.run(main())