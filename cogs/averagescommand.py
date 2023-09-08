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

    def convert_name(self,plr, draft_order) -> str:
        if len(draft_order) == 1:
            draft_order = "0" + draft_order
        plr_li = plr.split(' ')
        if len(plr_li[1]) > 5:
            plr_str = plr_li[1][0:5].lower() + plr_li[0][0:2].lower() + draft_order + ".html"
        else:
             plr_str = plr_li[1].lower() + plr_li[0][0:2].lower() + draft_order + ".html"
        return plr_str
    
    async def get_page(self,session, url) -> str:
        async with session.get(url) as r:
            return await r.text()

    async def page_tasks(self,session, url) -> asyncio.Task:
        task = await asyncio.create_task(self.get_page(session, url))
        return task

    def parse(self, bbr, season) -> dict:
        soup = BeautifulSoup(bbr, "lxml")
        if season == "null":
            avgs_table = soup.find("div", id="all_per_game-playoffs_per_game")
            avgs_szn = avgs_table.find("tfoot")
            stats = {
            "PPG": avgs_szn.find("td", {"data-stat": "pts_per_g"}).text,
            "APG": avgs_szn.find("td",{"data-stat": "ast_per_g"}).text,
            "RPG": avgs_szn.find("td",{"data-stat": "trb_per_g"}).text,
            "SPG": avgs_szn.find("td",{"data-stat": "stl_per_g"}).text,
            "BPG": avgs_szn.find("td",{"data-stat": "blk_per_g"}).text,
            "TOPG": avgs_szn.find("td",{"data-stat": "tov_per_g"}).text,
            "MPG": avgs_szn.find("td",{"data-stat": "mp_per_g"}).text,
            "seasons_played": len(avgs_table.find("tbody").find_all("th", {"data-stat": "season"}))
            }
            return stats
        else:
            avgs_szn = soup.find("tr", id=f"per_game.{season.split('-')[1]}")
            stats = {
            "PPG": avgs_szn.find("td", {"data-stat": "pts_per_g"}).text,
            "APG": avgs_szn.find("td",{"data-stat": "ast_per_g"}).text,
            "RPG": avgs_szn.find("td",{"data-stat": "trb_per_g"}).text,
            "SPG": avgs_szn.find("td",{"data-stat": "stl_per_g"}).text,
            "BPG": avgs_szn.find("td",{"data-stat": "blk_per_g"}).text,
            "TOPG": avgs_szn.find("td",{"data-stat": "tov_per_g"}).text,
            "MPG": avgs_szn.find("td",{"data-stat": "mp_per_g"}).text
            }
            return stats

    def get_image(self, bbr) -> str:
        soup = BeautifulSoup(bbr, "lxml")
        image = soup.find("div", class_="media-item")
        return image.img["src"]
    
    def create_embed(self, data, stats, player, season) -> discord.Embed:
        if season == "null":
            title_str = f"{player.title()}'s Career Averages"
        else:
            title_str = f"{player.title()}'s {season} Averages"
        avg = discord.Embed(
            title=title_str,
            color = discord.Color.orange()
            )
        avg.set_thumbnail(url=self.get_image(data))
        avg.add_field(name="Points Per Game", value=stats["PPG"], inline=False)
        avg.add_field(name="Assists Per Game", value=stats["APG"], inline=False)
        avg.add_field(name="Rebounds Per Game", value=stats["RPG"], inline=False)
        avg.add_field(name="Steals Per Game", value=stats["SPG"], inline=False)
        avg.add_field(name="Blocks Per Game", value=stats["BPG"], inline=False)
        avg.add_field(name="Turnovers Per Game", value=stats["TOPG"], inline=False)
        avg.add_field(name="Minutes Per Game", value=stats["MPG"], inline=False)
        if season == "null":
            avg.set_footer(text=f"{player.title()} played {stats['seasons_played']} seasons")
        return avg

    @app_commands.command(name="averages", description="Returns a player's ppg.")
    async def averages(self, interaction: discord.Interaction, player: str, draft_order: str="01", season : str="null"):
        async with aiohttp.ClientSession() as session:
            plr_str = self.convert_name(player, draft_order)
            data = await self.page_tasks(session, f"https://basketball-reference.com/players/{plr_str[0]}/{plr_str}")
        stats = self.parse(data, season)
        embed = self.create_embed(data, stats, player, season)
        await interaction.response.send_message(embed=embed)

    @averages.error
    async def averages_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Error: Missing required arguments. You must pass in a player")
        else:
            await ctx.response.send_message("An error has occurred.")
        

async def setup(client):
    await client.add_cog(BbrefCommands(client))