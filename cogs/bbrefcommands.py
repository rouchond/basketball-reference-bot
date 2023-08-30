"""
WHEN USING VSCODE ON WINDOWS, MAKE SURE THAT THE MICROSOFT STORE PYTHON ENVIRONMENT IS SELECTED!!!
"""

import discord
from discord.ext import commands
from discord import app_commands

import requests
from bs4 import BeautifulSoup

import asyncio
import aiohttp

class BbrefCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("bbrefcommands.py ready")

    def convert_name(plr, draft_order):
        if len(draft_order) == 1:
            draft_order = "0" + draft_order
        plr_li = plr.split()
        if len(plr_li[1]) > 5:
            plr_str = plr_li[1][0:5].lower() + plr_li[0][0:2].lower() + draft_order + ".html"
        else:
             plr_str = plr_li[1].lower() + plr_li[0][0:2].lower() + draft_order + ".html"
        return plr_str
    
    async def recent_season(soup):
        pass

    @app_commands.command(name="ppg", description="Returns a player's ppg")
    async def pts_pg(self, interaction: discord.Interaction, player: str, draft_order: str, season="null"):
        plr_str = self.convert_name(player, draft_order)
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://basketball-reference.com/players/{plr_str[0]}/{plr_str}") as r:
                bbr = await r.text()
        soup2 = BeautifulSoup(bbr, "lxml")
        avgs_szn = soup2.find("tr", id=f"per_game.{season.split('-')[1]}")
        ppg = avgs_szn.find("td", {"data-stat": "pts_per_g"}).text
        await interaction.response.send_message(f"{' '.join(plr.split()).title()} averaged {ppg} ppg in the {szn} season.")

        

async def setup(client):
    await client.add_cog(BbrefCommands(client))