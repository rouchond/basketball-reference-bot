import discord
from discord.ext import commands

class HelpCommand(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("helpcommand.py ready")

    @commands.command()
    async def help(self, ctx):
        help_embed = discord.Embed(title="Help", description="All commands for the bot", color=discord.Color.random())

        help_embed.set_author(name="Basketball Bot")
        help_embed.add_field(name="Clear", value="Deletes a specified amount of messages", inline=False)
        help_embed.set_footer(text=f"Requested by <@{ctx.author}>", icon_url=ctx.author.avatar)

        await ctx.send(embed=help_embed)

async def setup(client):
    await client.add_cog(HelpCommand(client))