import discord

import os
from discord.ext import commands
from discord_components import DiscordComponents

import settings

client = commands.Bot(command_prefix="!")


@client.command()
async def load(ctx, extension: str):
    if ctx.author.guild_permissions.administrator:
        client.load_extension(f"cogs.{extension}")
        await ctx.send(f"loaded {extension}", hidden=True)


@client.command()
async def unload(ctx, extension: str):
    if ctx.author.guild_permissions.administrator:
        client.unload_extension(f"cogs.{extension}")
        await ctx.send(f"unloaded {extension}", hidden=True)


@client.command()
async def reload(ctx, extension: str):
    if ctx.author.guild_permissions.administrator:
        client.unload_extension(f"cogs.{extension}")
        client.load_extension(f"cogs.{extension}")
        await ctx.send(f"reloaded {extension}", hidden=True)

if __name__ == "__main__":
    for filename in os.listdir('./cogs'):
        if filename.endswith(".py") and '__init__' not in filename:
            client.load_extension(f'cogs.{filename[:-3]}')

    DiscordComponents(client)
    client.run(settings.TOKEN)
