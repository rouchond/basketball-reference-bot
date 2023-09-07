import discord
from discord.ext import commands

class HelpPages(discord.ui.View):
    current_page: int = 1
    sep: int = 5

    def create_embed(self, data: list) -> discord.Embed:
        embed = discord.Embed(title="Help Command")
        for key in data:
            embed.add_field(name=key, value=self.data[key], inline=False)
        return embed

    def update_buttons(self):
        if self.current_page == 1:
            self.first_page_button.disabled = True
            self.prev_button.disabled = True
        else:
            self.first_page_button.disabled = False
            self.prev_button.disabled = False

        if self.current_page == int(len(self.data) / self.sep) + 1:
            self.next_button.disabled = True
            self.last_page_button.disabled = True
        else:
            self.next_button.disabled = False
            self.last_page_button.disabled = False

    async def update_message(self, data: list):
        self.update_buttons()
        await self.message.edit(embed=self.create_embed(data), view=self)
  
    async def send(self, ctx):
        keys = list(self.data.keys())
        self.message = await ctx.send(view=self)
        await self.update_message(keys[:self.sep])

    def get_current_page_data(self) -> list:
        keys = list(self.data.keys())
        until_item = self.current_page * self.sep
        from_item = until_item - self.sep
        if self.current_page == 1:
            from_item = 0
            until_item = self.sep
        if self.current_page == int(len(self.data) / self.sep) + 1:
            from_item = self.current_page * self.sep - self.sep
            until_item = len(self.data)
        return keys[from_item:until_item]

    #Creating the Buttons

    @discord.ui.button(label="|", style=discord.ButtonStyle.primary)
    async def first_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page = 1
        
        await self.update_message(self.get_current_page_data())

    @discord.ui.button(label="<", style=discord.ButtonStyle.primary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page -= 1

        await self.update_message(self.get_current_page_data())
    
    @discord.ui.button(label=">", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page += 1

        await self.update_message(self.get_current_page_data())
        
    @discord.ui.button(label=">|", style=discord.ButtonStyle.primary)
    async def last_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page = int(len(self.data) / self.sep) + 1

        await self.update_message(self.get_current_page_data())

class HelpCommand(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("helpcommand.py ready")

    @commands.command()
    async def help(self, ctx):
        data = {
            "draft_order": "The draft order is which order the player was drafted in relation to others with the same name. Isaiah Thomas 01 is Detroit Isaiah, while Isaiah Thomas 02 is Celtics Isaiah",
            "/ppg": "{player name} {draft_order: default 01} {season: default career} Displays the averages of a player over the specified season/their career.  Stats include: PPG, APG, RPG, SPG, BPG, TOPG, and MPG.",
            "/averages": "explanation",
            "/accolades": "explanation",
            "/idk" : "explanation",
        }
        view = HelpPages()
        view.data = data
        await view.send(ctx)

async def setup(client):
    await client.add_cog(HelpCommand(client))