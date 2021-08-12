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

@client.check
async def check_commands(ctx):
    logChannel = client.get_channel(settings.LOG_CHANNEL)
    if not ctx.guild:
        await ctx.send("Commando only works in a guild")
        return False
    if ctx.guild.id != settings.GUILD_ID:
        return False
    if not ctx.author.guild_permissions.administrator:
        await ctx.send(f"{ctx.author.mention}, You do not have permissions to use that command.", hidden=True)
        return False

    if isinstance(ctx.channel, discord.TextChannel):
        await logChannel.send(f":arrow_forward: Command:  {ctx.channel.mention} | {ctx.author.mention}: {ctx.message.content}", )
    else:
        await logChannel.send(f":arrow_forward: Command:  ???? | {ctx.author.mention}: {ctx.message.content}", )

    return True

@client.event
async def on_command_error(ctx, error):
    if not isinstance(error, commands.errors.CheckFailure):
        raise error


if __name__ == "__main__":
    for filename in os.listdir('./cogs'):
        if filename.endswith(".py") and '__init__' not in filename:
            client.load_extension(f'cogs.{filename[:-3]}')

    DiscordComponents(client)
    client.run(settings.TOKEN)
