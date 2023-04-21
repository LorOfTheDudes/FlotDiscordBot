import os
import discord

from dotenv import load_dotenv
from discord.ext import commands

from replit import db

load_dotenv(".env")
TOKEN = os.environ["TOKEN"]
PREFIX = "F"

intents = discord.Intents.default()
intents.message_content = True


bot = commands.Bot(command_prefix=f'{PREFIX}', intents=intents)


@commands.command()
async def on_member_join(member):
    print("someone joined")
    await member.create_dm()
    await member.dm_channel.send(
        f"Hi... \n"
        f"Your Name is {member.name}"
    )

@bot.command()
async def saveValue(context, *, args):
  print("THis got called")
  user_keys = db.prefix(f"{context.user}")
  if len(user_keys) == 0:
    db[f"{context.user}key"] = "0"
    db[f"{context.user}{db[f'{context.user}key']}"] = f"{args}"
  else:
    key = db[f"{context.user}key"]
    db[f"{context.user}key"] = f"{int(key)+1}"
    db[f"{context.user}{db[f'{context.user}key']}"] = f"{args}"
  print(db.keys)  


@bot.command()
@commands.has_role("admin")
async def startNewGame(context, *, args):
  #creating the field
  self.field = ""
  for i in range(8):
    self.field += "🔳" * 8 +"\n"


@bot.command()
async def Field(ctx):
  await ctx.send(self.field)
  


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('Like Icarus you flew to high, and this is your Fall. *You do not have permission.*')
    if isinstance(error, commands.errors.UserInputError):
        await ctx.send("Wrong Usage of this command!")


bot.run(TOKEN)
