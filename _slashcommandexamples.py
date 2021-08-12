import os

import discord
from discord_slash import SlashCommand  # Importing the newly installed library.

from discord_slash.utils.manage_commands import create_permission
from discord_slash.model import SlashCommandPermissionType
from discord_slash.utils.manage_commands import create_option
import settings

PERMISSION_ROLE_ID = 0

client = discord.Client(intents=discord.Intents.all())
slash = SlashCommand(client, sync_commands=True)  # Declares slash commands through the client.
guild_ids = [settings.GUILD_ID]  # Put your server ID in this array.


@client.event
async def on_ready():
    print("Ready!")


@slash.slash(name="getuser",
             description="get User ID",
             # permissions={
             #     GUILD_ID: [
             #         create_permission(PERMISSION_ROLE_ID, SlashCommandPermissionType.ROLE, True),
             #     ]
             # },
             guild_ids=guild_ids,
             options=[
                 create_option(
                     name="user",
                     description="Select User",
                     option_type=6,
                     required=True,
                 )
             ])
async def _getuser(ctx, user):
    await ctx.send(content=f"{user.id}")


@slash.slash(name="say",
             description="print message",
             permissions={
                 settings.GUILD_ID: [
                     create_permission(PERMISSION_ROLE_ID, SlashCommandPermissionType.ROLE, True),
                 ]
             },
             guild_ids=guild_ids,
             options=[
                 create_option(
                     name="channel",
                     description="Select Channel",
                     option_type=7,
                     required=True,
                 ),
                 create_option(
                     name="message",
                     description="Select User",
                     option_type=3,
                     required=True,
                 ),
             ])
async def _getuser(ctx, channel, message):
    await channel.send(content=message)
    await ctx.send(content="Printed stuff", hidden=True)


if __name__ == "__main__":
    client.run(settings.TOKEN)
