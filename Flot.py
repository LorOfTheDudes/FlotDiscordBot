import os
import discord

from dotenv import load_dotenv
from discord.ext import commands

from replit import db

load_dotenv(".env")
TOKEN = os.environ["TOKEN"]
PREFIX = "F"
WIDTH = 8
HEIGHT = 8

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=f'{PREFIX}', intents=intents)


async def on_ready():
    if "Field" not in db.keys():
        db["Field"] == "None"
    blueSquare = "🔳"
    brownSquare = "🟫"
    greenSquare = "🟩"
    violetSquare = "🟪"
    orangeSquare = "🟧"
    yellowSquare = 🟨

    @commands.command()
    async def on_member_join(member):
        print("someone joined")
        await member.create_dm()
        await member.dm_channel.send(
            f"Hi... \n"
            f"Your Name is {member.name}"
        )

    @bot.command()
    @commands.has_role("admin")
    async def startNewGame(context):
        if db["Field"] != "None":
            await context.send(f"There is already a game running! \n You can end the current game with {PREFIX}endGame")
            return

        field = []
        for i in range(WIDTH * HEIGHT):
            field.append("🔳")

    @bot.command()
    async def Field(ctx):
        printField(ctx)

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.send('Like Icarus you flew to high, and this is your Fall. *You do not have permission.*')
        if isinstance(error, commands.errors.UserInputError):
            await ctx.send("Wrong Usage of this command!")

    async def printField(context):
        await contex.send(db["Field"])

    bot.run(TOKEN)

    @bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('Like Icarus you flew to high, and this is your Fall. *You do not have permission.*')
    if isinstance(error, commands.errors.UserInputError):
        await ctx.send("Wrong Usage of this command!")


bot.run(TOKEN)
