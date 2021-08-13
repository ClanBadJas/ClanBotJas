import discord

import os
from discord.ext import commands
from discord_components import DiscordComponents
from discord_slash import SlashCommand
from discord_slash.model import SlashCommandPermissionType
from discord_slash.utils.manage_commands import create_option, create_choice, create_permission

import settings

intents = discord.Intents.default()
intents.members = True
intents.typing = False
intents.presences = True
client = commands.Bot(command_prefix="!", intents=intents)
slash = SlashCommand(client, sync_commands=True, sync_on_cog_reload=True, override_type=True)


@slash.slash(name="load",
             description="load a cog",
             guild_ids=settings.DISCORD_GUILD_IDS,
             permissions=settings.DISCORD_COMMAND_PERMISSIONS,
             default_permission=False,
             options=[
                 create_option(name="cog", description="Select Cog", option_type=3, required=True, choices=settings.DISCORD_COGS)
             ])
async def _load(ctx, cog: str):
    cog, className = cog.lower(), cog
    try:
        client.load_extension(f"cogs.{cog}")
        await ctx.send(f"loaded \"{cog}\"", hidden=True)
    except commands.errors.ExtensionAlreadyLoaded:
        await ctx.send(f"\"{cog}\" already loaded", hidden=True)


@slash.slash(name="unload",
             description="unload a cog",
             guild_ids=settings.DISCORD_GUILD_IDS,
             permissions=settings.DISCORD_COMMAND_PERMISSIONS,
             default_permission=False,
             options=[
                 create_option(name="cog", description="Select Cog", option_type=3, required=True, choices=settings.DISCORD_COGS)
             ])
async def _unload(ctx, cog: str):
    cog, className = cog.lower(), cog
    try:
        client.unload_extension(f"cogs.{cog}")
        await ctx.send(f"unloaded \"{cog}\"", hidden=True)
    except commands.errors.ExtensionNotLoaded:
        await ctx.send(f"\"{cog}\" not  loaded", hidden=True)


@slash.slash(name="reload",
             description="reload a cog",
             guild_ids=settings.DISCORD_GUILD_IDS,
             permissions=settings.DISCORD_COMMAND_PERMISSIONS,
             default_permission=False,
             options=[
                 create_option(name="cog", description="Select Cog", option_type=3, required=True, choices=settings.DISCORD_COGS)
             ])
async def _reload(ctx, cog: str):
    cog, className = cog.lower(), cog
    try:
        client.unload_extension(f"cogs.{cog}")
    except commands.errors.ExtensionNotLoaded:
        pass

    client.load_extension(f"cogs.{cog}")
    bot = client.get_cog(className)
    await bot.on_ready()
    await ctx.send(f"reloaded \"{cog}\"", hidden=True)


if __name__ == "__main__":
    for filename in os.listdir('./cogs'):
        if filename.endswith(".py") and '__init__' not in filename:
            client.load_extension(f'cogs.{filename[:-3]}')

    DiscordComponents(client)
    client.run(settings.DISCORD_TOKEN)
