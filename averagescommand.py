import discord
from discord.ext import commands

class AveragesCommand(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.Cog.listener()
	async def on_ready(self):
		print("averagescommand.py ready")

async def setup(client):
	await client.add_cog(AveragesCommand(client))