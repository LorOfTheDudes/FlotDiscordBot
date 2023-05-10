
import os
import time

import discord
from discord.ui import View

from dotenv import load_dotenv
from discord.ext import commands

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

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return


    if message.content.startswith("Ftest"):
        await message.author.send("Test", ephe)


    elif message.content.startswith("FField"):
        table = table = db.table(message.guild.name)
        channel = message.channel
        originalMessage = await channel.fetch_message(_get_game_message_id(message))
        originalMessageContent = originalMessage.content
        await message.delete()
        await originalMessage.delete()
        newMessage = await channel.send(originalMessage.content)
        table.update({"Message": newMessage.id})



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


    elif message.content.startswith("Fchoose"):
        view = View()
        button1 = discord.ui.Button(label="test")
        view.from_message()
        await message.channel.send(view=choosePlayerFirstRow())
        await message.channel.send(view=choosePlayerSecondRow())

    elif message.content.startswith("Fend"):
        # TODO Add Admin only access
        db.update({"field": "None"}, User.server == str(message.guild.id))


class choosePlayerFirstRow(discord.ui.View):
    @discord.ui.button(emoji=orangeSquare)
    async def orange(self, interaction: discord.Interaction, button: discord.ui.Button):
        table = db.table(str(interaction.guild.name))
        player_colors = _get_player_colors(interaction)
        if "orange" in player_colors.values():
            await interaction.response.send_message("That Color has already been picked", delete_after=10.0)
            return
        await interaction.response.send_message("You choose ORANGE as your Player")
        table.update({str(interaction.user): "orange"})
    @discord.ui.button(emoji=brownSquare)
    async def brown(self, interaction: discord.Interaction, button: discord.ui.Button):
        table = db.table(str(interaction.guild.name))
        if "brown" in _get_player_colors(interaction).values():
            await interaction.response.send_message("That Color has already been picked")
            return

        await interaction.response.send_message("You choose BROWN as your player")
        table.update({str(interaction.user): "brown"})

    @discord.ui.button(emoji=redSquare)
    async def red(self, interaction: discord.Interaction, button: discord.ui.Button):
        table = db.table(str(interaction.guild.name))
        if "red" in _get_player_colors(interaction).values():
            await interaction.response.send_message("That Color has already been picked")
            return

        await interaction.response.send_message("You choose RED as your player")
        table.update({str(interaction.user): "red"})

    @discord.ui.button(emoji=violetSquare)
    async def violet(self, interaction: discord.Interaction, button: discord.ui.Button):
        table = db.table(str(interaction.guild.name))
        if "violet" in _get_player_colors(interaction).values():
            await interaction.response.send_message("That Color has already been picked")
            return

        await interaction.response.send_message("You choose VIOLET as your player")
        table.update({str(interaction.user): "violet"})

    @discord.ui.button(emoji=greenSquare)
    async def green(self, interaction: discord.Interaction, button: discord.ui.Button):
        table = db.table(str(interaction.guild.name))
        if "red" in _get_player_colors(interaction).values():
            await interaction.response.send_message("That Color has already been picked")
            return

        await interaction.response.send_message("You choose GREEN as your player")
        table.update({str(interaction.user): "green"})


class choosePlayerSecondRow(discord.ui.View):
    @discord.ui.button(emoji=yellowSquare)
    async def yellow(self, interaction: discord.Interaction, button: discord.ui.Button):
        table = db.table(str(interaction.guild.name))
        if "yellow" in _get_player_colors(interaction).values():
            await interaction.response.send_message("That Color has already been picked")
            return

        await interaction.response.send_message("You choose YELLOW as your Player")
        table.update({str(interaction.user): "yellow"})

    @discord.ui.button(emoji=blueSquare)
    async def blue(self, interaction: discord.Interaction, button: discord.ui.Button):
        table = db.table(str(interaction.guild.name))
        if "blue" in _get_player_colors(interaction).values():
            await interaction.response.send_message("That Color has already been picked")
            return

        await interaction.response.send_message("You choose BLUE as your player")
        table.update({str(interaction.user): "blue"})


def _get_field(ctx, table):
    return table.search(User.server == str(ctx.guild.name))[0]["Field"]


def _get_player_colors(interaction):
    table = db.table(str(interaction.guild.name))
    output = {}
    for player in interaction.guild.members:
        serverDict = dict(table.search(User.server == str(interaction.guild.name))[0])
        if str(player) in serverDict:
            output.update({str(player): str(serverDict[f"{player.name}#{player.discriminator}"])})
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


client.run(TOKEN)
