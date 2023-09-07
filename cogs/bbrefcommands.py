"""
WHEN USING VSCODE ON WINDOWS, MAKE SURE THAT THE MICROSOFT STORE PYTHON ENVIRONMENT IS SELECTED!!!
"""

import discord
from discord.ext import commands
from discord import app_commands

from bs4 import BeautifulSoup

import asyncio
import aiohttp

class BbrefCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("bbrefcommands.py ready")

    def convert_name(self,plr, draft_order):
        if len(draft_order) == 1:
            draft_order = "0" + draft_order
        plr_li = plr.split(' ')
        if len(plr_li[1]) > 5:
            plr_str = plr_li[1][0:5].lower() + plr_li[0][0:2].lower() + draft_order + ".html"
        else:
             plr_str = plr_li[1].lower() + plr_li[0][0:2].lower() + draft_order + ".html"
        return plr_str
    
    async def get_page(self,session, url):
        async with session.get(url) as r:
            return await r.text()

    async def page_tasks(self,session, url):
        task = await asyncio.create_task(self.get_page(session, url))
        return task

    def parse(self, bbr, season):
        soup = BeautifulSoup(bbr, "lxml")
        if season == "null":
            avgs_table = soup.find("div", id="all_per_game-playoffs_per_game")
            avgs_szn = avgs_table.find("tfoot")
            ppg = avgs_szn.find("td", {"data-stat": "pts_per_g"}).text
            return f"Averaged {ppg} ppg over his career."
        else:
            avgs_szn = soup.find("tr", id=f"per_game.{season.split('-')[1]}")
            ppg = avgs_szn.find("td", {"data-stat": "pts_per_g"}).text
            return f"Averaged {ppg} ppg in the {season} season"

    def get_image(self, bbr):
        soup = BeautifulSoup(bbr, "lxml")
        image = soup.find("div", class_="media-item") 
        return image.img["src"]

    @app_commands.command(name="ppg", description="Returns a player's ppg.")
    async def pts_pg(self, interaction: discord.Interaction, player: str, draft_order: str="01", season : str="null"):
        async with aiohttp.ClientSession() as session:
            plr_str = self.convert_name(player, draft_order)
            data = await self.page_tasks(session, f"https://basketball-reference.com/players/{plr_str[0]}/{plr_str}")
        msg = self.parse(data, season)
        ppg = discord.Embed(
            title=player.title(),
            color = discord.Color.random()
            )
        ppg.set_thumbnail(url=self.get_image(data))
        ppg.add_field(name="PPG", value=msg)
        await interaction.response.send_message(embed=ppg)

        

async def setup(client):
    await client.add_cog(BbrefCommands(client))