import discord
from discord.ext import commands
from discord import app_commands

import requests
import bs4
from bs4 import BeautifulSoup

import asyncio
import aiohttp

class BbrefCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("bbrefcommands.py ready")

    @app_commands.command(name="ppg", description="Returns a player's ppg")
    async def pts_pg(self, interaction: discord.Interaction, plr: str, szn: str):
        plr_li = plr.split()
        plr_str = plr_li[1].lower() + plr_li[0][0:2].lower() + "01.html"
        bbr = requests.get(f"https://basketball-reference.com/players/{plr_li[1][0]}/{plr_str}").text
        soup2 = BeautifulSoup(bbr, "lxml")
        avgs_szn = soup2.find("tr", id=f"per_game.{szn.split('-')[1]}")
        ppg = avgs_szn.find("td", {"data-stat": "pts_per_g"}).text
        #await interaction.response.send_message(f"{' '.join(plr.split()).title()} averaged {ppg} ppg in the {szn} season.")

        

async def setup(client):
    await client.add_cog(BbrefCommands(client))