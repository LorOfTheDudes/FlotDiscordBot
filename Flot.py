#TODO ADD ROLE GIVING
#TODO add greying out choosen roles
#TODO fix multi picking and non functioning check, if is already picked
import os

import discord
from discord.components import Button, ButtonStyle, ActionRow

from dotenv import load_dotenv

from tinydb import TinyDB, Query
db = TinyDB("Flot.json")
User = Query()

load_dotenv(".env")
TOKEN = os.getenv("TOKEN")
PREFIX = "F"
WIDTH = 8
HEIGHT = 8

blackSquare = "🔳"
blueSquare = "🟦"
brownSquare = "🟫"
greenSquare = "🟩"
violetSquare = "🟪"
orangeSquare = "🟧"
yellowSquare = "🟨"
redSquare = "🟥"
gameColors = ["🟦", "🟫", "🟩", "🟪", "🟧", "🟨", "🟥"]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return


    elif message.content.startswith("Finit"):
        channel = message.channel
        guild = message.guild
        if str(guild) not in db.tables():
            table = db.table(guild.name)
            table.insert({"server": f"{message.guild.name}"})
            field = []
            for i in range(WIDTH):
                for j in range(HEIGHT):
                    field.append(0)
                field.append("\n")
            table.update({"Field": field}, User.server == str(message.guild.name))
            new_message = await channel.send(_get_field_printform(message))
            table.update({"Message": new_message.id})
        await message.delete()
        return


    elif message.content.startswith("FField"):
        table = db.table(message.guild.name)
        channel = message.channel
        originalMessage = await channel.fetch_message(_get_game_message_id(message))
        await message.delete()
        await originalMessage.delete()
        newMessage = await channel.send(_get_field_printform(message))
        table.update({"Message": newMessage.id})


    elif message.content.startswith("Fchoose"):
        table = db.table(message.guild.name)
        channel = message.channel
        originalMessage = await channel.fetch_message(_get_game_message_id(message))
        await message.delete()
        await originalMessage.delete()
        newMessage = await channel.send(content="Choose your player!")
        for color in gameColors:
            await newMessage.add_reaction(color)
        table.update({"Message": newMessage.id})


@client.event
async def on_reaction_add(reaction : discord.Reaction, user:discord.User):
    if user == client.user:
        return

    if reaction.message.content == "Choose your player!":
        CanPick, color = _player_choose_helper(reaction, user)
        if CanPick:


            positiveResponse = await reaction.message.channel.send(f"You picked player {color}!")
            await positiveResponse.delete(delay=10.0)



@client.event
async def on_reaction_remove(reaction: discord.Reaction, user):
    if user == client.user:
        return
    table = db.table(reaction.message.guild.name)
    if reaction.message.content == "Choose your player!":
        #if the removed reaction equals the users color, then remove the color
        playerColors = _get_player_colors(reaction.message)
        if _emoji_to_string(reaction.emoji) == playerColors[user.name]:
            table.update({user.name: "none"})
            positiveResponse = await reaction.message.channel.send(f"You are no longer player {_emoji_to_string(reaction.emoji)}")
            await positiveResponse.delete(delay=10)

def _get_field(ctx, table):
    return table.search(User.server == str(ctx.guild.name))[0]["Field"]


def _get_player_colors(interaction):
    table = db.table(str(interaction.guild.name))
    output = {}
    for player in interaction.guild.members:
        serverDict = dict(table.search(User.server == str(interaction.guild.name))[0])
        print(player)
        if str(player.name) in serverDict:
            output.update({str(player.name): str(serverDict[f"{player.name}"])})
    print(output)
    return output


def _get_field_printform(message: discord.Message):
    table = db.table(str(message.guild.name))
    output = ""
    for field in _get_field(message, table):
        if field == 0:
            output += blackSquare
        else:
            output += str(field)
    return output


def _get_game_message_id(message: discord.Message):
    table = db.table(str(message.guild.name))
    return table.search(User.server == str(message.guild.name))[0]["Message"]


def _emoji_to_string(emoji):
    if emoji == greenSquare:
        return "green"
    elif emoji == redSquare:
        return "red"
    elif emoji == blueSquare:
        return "blue"
    elif emoji == yellowSquare:
        return "yellow"
    elif emoji == brownSquare:
        return "brown"
    elif emoji == violetSquare:
        return "violet"
    elif emoji == orangeSquare:
        return "orange"

def _player_choose_helper(reaction: discord.Reaction, user):
    table = db.table(reaction.message.guild.name)
    player_colors = _get_player_colors(reaction.message)
    if _emoji_to_string(reaction.emoji) not in player_colors.values():
        table.update({user.name: _emoji_to_string(reaction.emoji)})
        return True, _emoji_to_string(reaction.emoji)

def _string_to_emoji(string):
    if string == "orange": return orangeSquare
    if string == "yellow": return yellowSquare
    if string == "blue": return blueSquare
    if string == "brown": return brownSquare
    if string == "violet": return violetSquare
    if string == "green": return greenSquare
    if string == "red": return redSquare

client.run(TOKEN)
