#TODO ADD ROLE GIVING
#TODO ADD REACTION REMOVAL, ON PICKING A DIFFRENT ROLE
#TODO ADD CONFIGURABLE TIME TWEEN GIVING OUT POINTS/RANDOM
import os
import random

import discord
from discord.ext import tasks

from dotenv import load_dotenv
from tinydb import TinyDB, Query

db = TinyDB("Flot.json")
User = Query()

load_dotenv(".env")
TOKEN = os.getenv("TOKEN")
PREFIX = "F"
WIDTH = 14
HEIGHT = 14
HOURS_TWEEN_POINTS = 24

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

@tasks.loop(seconds=10)
async def give_out_points(guild: discord.Guild):
    print("Giving out points")
    #should only be called once there is a message saved in the db
    table = db.table(guild.name)
    serverTable = table.search(User.server == str(guild.name))[0]
    channel = guild.get_channel(serverTable["Message"]["channel"])
    message = await channel.fetch_message(serverTable["Message"]["id"])
    for player in _get_player_colors(message).keys():
        playerDict: dict = serverTable[player]
        playerDict.update({"points": (playerDict["points"]+1)})
        table.update({player: playerDict})

@client.event
async def on_ready():
    for guild in client.guilds:
        if str(guild.name) not in db.tables():
            #first time setup
            table = db.table(guild.name)
            table.insert({"server": f"{guild.name}"})
            field = []
            for i in range(WIDTH):
                for j in range(HEIGHT):
                    field.append(0)
                field.append("\n")
            table.update({"Field": field}, User.server == str(guild.name))
            table.update({"Configs": {"state": "preparing", "point_time": 600, "last_point_given": "Never",
                                      "helper_message": "None"}})
            table.update({"Message": {"id": "None", "channel": "None"}})
        #check game state
        #restart gameloop if game running
        table = db.table(guild.name)
        serverTable = table.search(User.server == str(guild.name))
        if serverTable[0]["Configs"]["state"] == "running":
            give_out_points.start(guild)



@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    table = db.table(message.guild.name)
    if table.search(User.server == message.guild.name)[0]["Message"]["id"] != "None" and \
            message.content.startswith("FField") or \
            message.content.startswith("Fchoose") or \
            message.content.startswith("Fstart"):

        print("Updating olb Msg")
        originalMessage = await message.channel.fetch_message(_get_game_message_id(message))
        await originalMessage.delete()

    if message.content.startswith("FField"):
        print("Executed FFIELD")
        table = db.table(message.guild.name)
        channel = message.channel
        newMessage = await channel.send(_get_field_printform(message))
        _update_message(newMessage)


    elif message.content.startswith("Fchoose"):
        print("Executed Fchoose")
        table = db.table(message.guild.name)
        channel = message.channel
        newMessage = await channel.send(content="Choose your player!")
        for color in gameColors:
            await newMessage.add_reaction(color)
        _update_message(newMessage)

    elif message.content.startswith("Fstart"):
        print("Executed Fstart")
        table = db.table(message.guild.name)
        ConfigsDict: dict = table.search(User.server == message.guild.name)[0]["Configs"]
        ConfigsDict.update({"state": "running"})
        table.update({"Configs": ConfigsDict})
        give_out_points.start(message.guild)

        #put all chosen players somewhere
        players = _get_player_colors(interaction=message)
        field = _get_field(message, table)
        for player in players.keys():
            foundPlace = False
            while foundPlace == False:
                pos = random.randint(1, WIDTH*HEIGHT)
                if field[(pos+(pos//WIDTH))-1] == 0:
                    field[(pos+(pos//WIDTH))-1] = _string_to_emoji(players[player])
                    foundPlace = True
        table.update({"Field": field}, User.server == str(message.guild.name))
        newMessage = await message.channel.send(_get_field_printform(message))
        _update_message(newMessage)
    await message.delete()




@client.event
async def on_reaction_add(reaction : discord.Reaction, user:discord.User):
    if user == client.user:
        return

    if reaction.message.content == "Choose your player!":
        CanPick, color = _player_choose_helper(reaction, user)
        if CanPick:
            positiveResponse = await reaction.message.channel.send(f"You picked player {color}!")
            await positiveResponse.delete(delay=10.0)
        else:
            negativeResponse = await reaction.message.channel.send("Someone else picked that color")
            await negativeResponse.delete(delay=5.0)


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
        if str(player.name) in serverDict:
            output.update({player.name: serverDict[player.name]["color"]})
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
    return table.search(User.server == str(message.guild.name))[0]["Message"]["id"]


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
    # is the user in the database?
    serverTable = table.search(User.server == reaction.message.guild.name)[0]
    if user.name not in serverTable:
        table.update({user.name: {"color": "none", "points": 0, "hearts": 3}})

    #is the chosen color valid?
    player_colors = _get_player_colors(reaction.message) #TODO Update this to the new format
    if _emoji_to_string(reaction.emoji) not in player_colors.values():
        playerDict:dict = table.search(User.server == reaction.message.guild.name)[0][user.name]
        playerDict.update({"color": _emoji_to_string(reaction.emoji)})
        table.update({user.name: playerDict})
        return True, _emoji_to_string(reaction.emoji)
    else:
        return False, _emoji_to_string(reaction.emoji)

def _string_to_emoji(string):
    if string == "orange": return orangeSquare
    if string == "yellow": return yellowSquare
    if string == "blue": return blueSquare
    if string == "brown": return brownSquare
    if string == "violet": return violetSquare
    if string == "green": return greenSquare
    if string == "red": return redSquare

def _update_message(message: discord.Message):
    table = db.table(message.guild.name)
    MessageDict: dict = table.search(User.server == message.guild.name)[0]["Message"]
    MessageDict.update({"id": message.id, "channel": message.channel.id})
    table.update({"Message": MessageDict})

client.run(TOKEN)
