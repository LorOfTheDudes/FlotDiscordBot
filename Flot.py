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

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=f'{PREFIX}', intents=intents)

def _get_field(ctx):
    return db.search(User.server == str(ctx.guild.id))[0]["field"]


async def on_ready():
    if "Field" not in db.keys():
        db.insert({"Server":bot.guilds,"Field": "None"})
    emptyField = "🔳"
    blueSquare = "🟦"
    brownSquare = "🟫"
    greenSquare = "🟩"
    violetSquare = "🟪"
    orangeSquare = "🟧"
    yellowSquare = "🟨"


@bot.command()
async def init(ctx: discord.Message):
    if not db.search(User.server == f"{ctx.guild.id}"):
        db.insert({"server": str(ctx.guild.id), "field": "None"})
        await ctx.send("Initiated Flot!")
    else:
        await ctx.send("Already Initiated")



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


bot.run(TOKEN)
