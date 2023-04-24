import os
import discord

from dotenv import load_dotenv
from discord.ext import commands

from tinydb import TinyDB, Query
db = TinyDB("db.json")
User = Query()

load_dotenv(".env")
TOKEN = os.getenv("TOKEN")
PREFIX = "F"
WIDTH = 8
HEIGHT = 8

emptyField = "🔳"
blueSquare = "🟦"
brownSquare = "🟫"
greenSquare = "🟩"
violetSquare = "🟪"
orangeSquare = "🟧"
yellowSquare = "🟨"
redSquare = "🟥"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=f'{PREFIX}', intents=intents)

class choosePlayerFirstRow(discord.ui.View):
    @discord.ui.button(emoji=orangeSquare)
    async def orange(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("You choose ORANGE as your Player")
        db.update({str(interaction.user.id) : "orange"})
    @discord.ui.button(
                       emoji=brownSquare)
    async def brown(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("You choose BROWN as your player")

    @discord.ui.button(emoji=redSquare)
    async def red(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("You choose RED as your player")

    @discord.ui.button(emoji=violetSquare)
    async def violet(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("You choose VIOLET as your player")

    @discord.ui.button(emoji=greenSquare)
    async def green(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("You choose GREEN as your player")

class choosePlayerSecondRow(discord.ui.View):
    @discord.ui.button(emoji=yellowSquare)
    async def yellow(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("You choose YELLOW as your Player")

    @discord.ui.button(
        emoji=blueSquare)
    async def blue(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("You choose BLUE as your player")



@bot.command()
async def test(ctx):
    await ctx.send(view=choosePlayerFirstRow())
    await ctx.send(view=choosePlayerSecondRow())


def _get_field(ctx):
    return db.search(User.server == str(ctx.guild.id))[0]["field"]


async def on_ready():
    if "Field" not in db.keys():
        db.insert({"Server":bot.guilds,"Field": "None"})

@bot.command()
async def init(ctx: discord.Message):
    guild = ctx.guild
    if str(guild) not in db.tables():
        table = db.table(str(guild.name))
        field = [0 for i in range(WIDTH*HEIGHT)]
        table.insert({"Field": field})



@bot.command()
@commands.has_role("admin")
async def startNewGame(context):
    if _get_field(context) != "None":
        await context.send(f"There is already a game running! \n You can end the current game with {PREFIX}endGame")
        return
    field = []
    for i in range(WIDTH):
        for j in range(HEIGHT):
            field.append("🔳")
        field.append("\n")
    db.update({"field":field}, User.server == str(context.guild.id))
    await context.send("Choose your Player")




@bot.command()
async def Field(ctx):
    output= "".join(_get_field(ctx))
    await ctx.send(output)

@commands.has_role("admin")
@bot.command()
async def endGame(ctx):
    db.update({"field": "None"}, User.server == str(ctx.guild.id))



@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('Like Icarus you flew to high, and this is your Fall. *You do not have permission.*')
    if isinstance(error, commands.errors.UserInputError):
        await ctx.send("Wrong Usage of this command!")
    await ctx.send("Some Unknown Error ocurred!")

def _get_guild_table(ctx):
    for table in db.tables():
        table: db.table_class
        if table.name == ctx.guild.id:
            return table
    return None


bot.run(TOKEN)
