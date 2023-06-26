#TODO ADD ROLE GIVING
#TODO ADD REACTION REMOVAL, ON PICKING A DIFFRENT ROLE
#TODO ADD CONFIGURABLE TIME TWEEN GIVING OUT POINTS/RANDOM
#TODO ADD COLLISION TO MOVEMENT AND FIX MESSAGE DELETION FOR MOVING AROUND
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

upArrow = "\N{Up-Pointing Small Red Triangle}"
downArrow = "\N{Down-Pointing Small Red Triangle}"
leftArrow = "\N{Black Left-Pointing Triangle}"
rightArrow = "\N{Black Right-Pointing Triangle}"

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
    try:
        message = await channel.fetch_message(serverTable["Message"]["id"])
    except discord.NotFound:
        print("Cannot find original Message, skipping iteration")
        return

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
            table.update({"Message": {"id": 0, "channel": 0}})
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
    if not (message.content.startswith("FField") or \
            message.content.startswith("Fchoose") or \
            message.content.startswith("Fstart")):
        print("Message did not contain Bot Keyword, no action will be taken")
        return


    if message.content.startswith("FField"):
        print("Executed FFIELD")
        table = db.table(message.guild.name)
        channel = message.channel
        newMessage = await channel.send(_get_field_printform(message))


    elif message.content.startswith("Fchoose"):
        print("Executed Fchoose")
        table = db.table(message.guild.name)
        channel = message.channel
        newMessage = await channel.send(content="Choose your player!")
        for color in gameColors:
            await newMessage.add_reaction(color)

    elif message.content.startswith("Fstart"):
        print("Executed Fstart")
        if table.search(User.server == message.guild.name)[0]["Configs"]["state"] == "running":
            #game already running, returning
            response = await message.channel.send("Game already started, here is the field again:")
            await response.delete(delay=5)
            try:
                give_out_points.start(message.guild)
            except RuntimeError:
                print("Game was still running, Point-Coroutine did not get restarted")
        else:
            ConfigsDict: dict = table.search(User.server == message.guild.name)[0]["Configs"]
            ConfigsDict.update({"state": "running"})
            table.update({"Configs": ConfigsDict})

            #put all chosen players somewhere
            players = _get_player_colors(interaction=message)
            field = _get_field(message, table)
            print(players)
            for player in players.keys():
                while True:
                    pos = random.randint(0, WIDTH*HEIGHT)
                    if field[pos] == 0:
                        field[pos] = _string_to_emoji(players[player])
                        break
            table.update({"Field": field})
            print(field)
        newMessage = await message.channel.send(_get_field_printform(message))
        await newMessage.add_reaction(upArrow)
        await newMessage.add_reaction(downArrow)
        await newMessage.add_reaction(leftArrow)
        await newMessage.add_reaction(rightArrow)

    #handle the player sent, and the new Message:

    try:
        oldMessage = await message.channel.fetch_message(_get_game_message_id(message))
        await oldMessage.delete()
        print("deleted Old Message")
    except discord.errors.NotFound:
        print("Did not find last Bot Message, it was probably deleted")
    finally:
        MessageDict: dict = table.search(User.server == message.guild.name)[0]["Message"]
        MessageDict.update({"id": newMessage.id, "channel": newMessage.channel.id})
        table.update({"Message": MessageDict})
        await message.delete()
        print("deleted Player-sent Command")





@client.event
async def on_reaction_add(reaction : discord.Reaction, user:discord.User):
    if user == client.user:
        return

    table = db.table(reaction.message.guild.name)
    if reaction.message.content == "Choose your player!":
        CanPick, color = _player_choose_helper(reaction, user)
        if CanPick:
            positiveResponse = await reaction.message.channel.send(f"You picked player {color}!")
            await positiveResponse.delete(delay=10.0)
        else:
            negativeResponse = await reaction.message.channel.send("Someone else picked that color")
            await negativeResponse.delete(delay=5.0)
    if reaction.emoji in [upArrow, downArrow, leftArrow, rightArrow] and _get_game_state(reaction.message) == "running":
        field = _get_field(reaction.message, table)
        playerColors = _get_player_colors(reaction.message)
        playerEmoji = _string_to_emoji(playerColors[user.name])
        playerpos = field.index(playerEmoji)

        if reaction.emoji == leftArrow:
            if field[playerpos-1] != 0:
                response = await reaction.message.channel.send("You cannot move there")
                await response.delete(delay=5)
            else:
                field[playerpos-1] = playerEmoji
                field[playerpos] = 0
                table.update({"Field": field})
        elif reaction.emoji == rightArrow:
            if field[playerpos + 1] != 0:
                response = await reaction.message.channel.send("You cannot move there")
                await response.delete(delay=5)
            else:
                field[playerpos + 1] = playerEmoji
                field[playerpos] = 0
                table.update({"Field": field})
        elif reaction.emoji == upArrow:
            if field[playerpos - WIDTH-1] != 0:
                response = await reaction.message.channel.send("You cannot move there")
                await response.delete(delay=5)
            else:
                field[playerpos - WIDTH-1] = playerEmoji
                field[playerpos] = 0
                table.update({"Field": field})
        elif reaction.emoji == downArrow:
            if field[playerpos + WIDTH + 1] != 0:
                response = await reaction.message.channel.send("You cannot move there")
                await response.delete(delay=5)
            else:
                field[playerpos + WIDTH + 1] = playerEmoji
                field[playerpos] = 0
                table.update({"Field": field})
        message = reaction.message
        newMessage = await reaction.message.channel.send(_get_field_printform(reaction.message))

        try:
            if not table.search(User.server == str(message.guild.name))[0]["Message"]["id"] == 0:
                oldMessage = await message.channel.fetch_message(_get_game_message_id(message))
                await oldMessage.delete()
        except discord.errors.NotFound:
            print("Did not find last Bot Message, it was propably deleted")
        finally:
            MessageDict: dict = table.search(User.server == message.guild.name)[0]["Message"]
            MessageDict.update({"id": newMessage.id, "channel": newMessage.channel.id})
            table.update({"Message": MessageDict})
        await newMessage.add_reaction(upArrow)
        await newMessage.add_reaction(downArrow)
        await newMessage.add_reaction(leftArrow)
        await newMessage.add_reaction(rightArrow)



@client.event
async def on_reaction_remove(reaction: discord.Reaction, user):
    if user == client.user:
        return
    table = db.table(reaction.message.guild.name)
    if reaction.message.content == "Choose your player!":
        #if the removed reaction equals the users color, then remove the color
        playerColors = _get_player_colors(reaction.message)
        if _emoji_to_string(reaction.emoji) == playerColors[user.name]:
            table.update({user.name: {"color": "none", "points": 0, "hearts": 3}})
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

def _get_game_state(message:discord.Message):
    table = db.table(str(message.guild.name))
    return table.search(User.server == message.guild.name)[0]["Configs"]["state"]


client.run(TOKEN)
