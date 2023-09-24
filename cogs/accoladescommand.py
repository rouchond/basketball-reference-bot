import discord
from discord.ext import commands
from discord import app_commands

from bs4 import BeautifulSoup

import asyncio
import aiohttp

class Accolades(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("accolades.py ready")
          	
    def convert_name(self, plr: str, draft_order) -> str:
        if len(str(draft_order)) == 1:
            draft_order = "0" + str(draft_order)
        #Handling Apostrophes and - in names
        if "'" in plr:
            plr_index = plr.find("'")
            plr = plr[0:plr_index] + plr[plr_index + 1:]
        if "-" in plr:
            plr_index = plr.find("-")
            plr = plr[0:plr_index]

        plr_li = plr.split(' ')
        if len(plr_li[1]) > 5:
            plr_str = plr_li[1][0:5].lower() + plr_li[0][0:2].lower() + str(draft_order) + ".html"
        else:
                plr_str = plr_li[1].lower() + plr_li[0][0:2].lower() + str(draft_order) + ".html"
        return plr_str

    async def get_page(self,session, url) -> str:
        async with session.get(url) as r:
            return await r.text()

    async def page_tasks(self,session, url) -> asyncio.Task:
        task = await asyncio.create_task(self.get_page(session, url))
        return task

    def parse(self, bbr) -> dict:
        #id="leaderboard_pts_per_g"
        #class="first_place"
        soup = BeautifulSoup(bbr, "lxml")
        plr_accolades = {
            "MVPS": 0,
            "FMVPS": 0,
            "Championships": 0,
            "All-Star Apperances": 0,
            "All-Star MVPS": 0,
            "DPOYS": 0,
            "PPG Leader": 0,
            "APG Leader": 0,
            "RPG Leader": 0,
            "SPG Leader": 0,
            "BPG Leader": 0,
            "3PT FG Leader": 0,
            "Triple-Double Leader": 0
        }
        
        
        leaderboard_head = soup.find("div",id="all_leaderboard")
        #print(leaderboard_head)
        print(leaderboard_head.find_all("div", class_="data_grid_box"))
        print(soup.find("div", id="div_leaderboard"))
        leaderboard = leaderboard_head.find("div", id="data_grid")
        #Current Error: soup is not fetching all of the divs inside of leaderboard_head
        
        #Fetching PPG Leader Stats
        if leaderboard.find("div", id="leaderboard_pts_per_g"):
            ppg_table = leaderboard.find("div", id="leaderboard_pts_per_g")
            ppg_ranks = ppg_table.find_all("tr", class_="first_place")
            print(ppg_ranks)
            plr_accolades["PPG Leader"] = len(ppg_ranks)
        #Fetching APG Leader Stats
        if leaderboard.find("div", id="leaderboard_ast_per_g"):
            apg_table = leaderboard.find("div", id="leaderboard_ast_per_g")
            apg_ranks = apg_table.find_all("tr", class_="first_place")
            plr_accolades["APG Leader"] = len(apg_ranks)
        #Fetching RPG Leader Stats
        if leaderboard.find("div", id="leaderboard_trb"):
            rpg_table = leaderboard.find("div", id="leaderboard_trb")
            rpg_ranks = rpg_table.find_all("tr", class_="first_place")
            plr_accolades["RPG Leader"] = len(rpg_ranks)
        #Fetching SPG Leader Stats
        if leaderboard.find("div", id="leaderboard_stl_per_g"):
            spg_table = leaderboard.find("div", id="leaderboard_stl_per_g")
            spg_ranks = spg_table.find_all("tr", class_="first_place")
            plr_accolades["SPG Leader"] = len(spg_ranks)
        #Fetching BPG Leader Stats
        if leaderboard.find("div", id="leaderboard_blk_per_g"):
            bpg_table = leaderboard.find("div", id="leaderboard_blk_per_g")
            bpg_ranks = bpg_table.find_all("tr", class_="first_place")
            plr_accolades["BPG Leader"] = len(bpg_ranks)


        
        stats = {
            "NAME": soup.find("div", id="info").find("span").text
        }
        return plr_accolades

    def get_image(self, bbr) -> str:
        soup = BeautifulSoup(bbr, "lxml")
        image = soup.find("div", class_="media-item")
        return image.img["src"]

    def create_embed(self, data, stats) -> discord.Embed:
        title_str = f"{stats['NAME']}'s Career Averages"
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
        avg.set_footer(text=f"{stats['NAME']} played {stats['seasons_played']} seasons")
        return avg

    @app_commands.command(name="accolades", description="Returns a player's major career accolades.")
    async def accolades(self, interaction: discord.Interaction, player: str, draft_order: int=1):
        async with aiohttp.ClientSession() as session:
            plr_str = self.convert_name(player, draft_order)
            data = await self.page_tasks(session, f"https://basketball-reference.com/players/{plr_str[0]}/{plr_str}")
        stats = self.parse(data)
        await interaction.response.send_message(stats)
        #embed = self.create_embed(data, stats)
        #await interaction.response.send_message(embed=embed)
    """
    @accolades.error
    async def accolades_error(self, ctx, error):
        if "IndexError" in str(error):
            await ctx.response.send_message("Error: Player not found")
        elif "BadArgument" in str(error):
            await ctx.response.send_message("Error: Please enter a valid year")
        elif "NoneType" in str(error):
            await ctx.response.send_message("Error: DraftOrder/Season not found for player")
        else:
            await ctx.response.send_message(f"An error has occurred. {error}")
    """
async def setup(client):
    await client.add_cog(Accolades(client))