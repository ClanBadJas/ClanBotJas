import functools

import discord
from discord.ext import commands
from discord_components import DiscordComponents
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option

import settings


async def logCommand(channel, ctx, *args, **kwargs):
    log_string = ":arrow_forward: Command:  "
    log_string += ctx.channel.mention if isinstance(ctx.channel, discord.TextChannel) else "????"
    log_string += f" | {ctx.author.mention}: /{ctx.command} "
    if ctx.subcommand_name:
        log_string += ctx.subcommand_name

    for k, v in kwargs.items():
        log_string += f" {k}: {v}"
    log_string += "."
    await channel.send(log_string)


client = commands.Bot(command_prefix="!", intents=settings.INTENTS)
slash = SlashCommand(client, sync_commands=True, sync_on_cog_reload=True, override_type=True)


def slashcommandlogger(func):
    @functools.wraps(func)
    async def wrapped(ctx, cog: str):
        # Some fancy foo stuff
        await logCommand(client.get_channel(settings.DISCORD_LOG_CHANNEL), ctx, cog=cog.lower())
        await func(ctx, cog)

    return wrapped


@slash.slash(name="load",
             description="load a cog",
             guild_ids=settings.DISCORD_GUILD_IDS,
             permissions=settings.DISCORD_COMMAND_PERMISSIONS,
             default_permission=False,
             options=[
                 create_option(name="cog", description="Select Cog", option_type=3, required=True,
                               choices=settings.DISCORD_COGS)
             ])
@slashcommandlogger
async def _load(ctx, cog: str):
    cog, className = cog.lower(), cog
    try:
        client.load_extension(f"cogs.{cog}")
        bot = client.get_cog(className)
        await bot.on_ready()
        await ctx.send(f"Cog: \"{cog}\" loaded.", hidden=True)
    except commands.errors.ExtensionAlreadyLoaded:
        await ctx.send(f"Cog: \"{cog}\" already loaded.", hidden=True)


@slash.slash(name="unload",
             description="unload a cog",
             guild_ids=settings.DISCORD_GUILD_IDS,
             permissions=settings.DISCORD_COMMAND_PERMISSIONS,
             default_permission=False,
             options=[
                 create_option(name="cog", description="Select Cog", option_type=3, required=True,
                               choices=settings.DISCORD_COGS)
             ])
@slashcommandlogger
async def _unload(ctx, cog: str):
    cog, className = cog.lower(), cog
    try:
        client.unload_extension(f"cogs.{cog}")
        await ctx.send(f"Cog: \"{cog}\" unloaded.", hidden=True)
        await client.get_channel(settings.DISCORD_LOG_CHANNEL).send(f":negative_squared_cross_mark: Cog: \"{cog}\" unloaded.")
    except commands.errors.ExtensionNotLoaded:
        await ctx.send(f"Cog: \"{cog}\" not loaded.", hidden=True)


@slash.slash(name="reload",
             description="reload a cog",
             guild_ids=settings.DISCORD_GUILD_IDS,
             permissions=settings.DISCORD_COMMAND_PERMISSIONS,
             default_permission=False,
             options=[
                 create_option(name="cog", description="Select Cog", option_type=3, required=True,
                               choices=settings.DISCORD_COGS)
             ])
@slashcommandlogger
async def _reload(ctx, cog: str):
    cog, className = cog.lower(), cog
    try:
        client.unload_extension(f"cogs.{cog}")
        await client.get_channel(settings.DISCORD_LOG_CHANNEL).send(f":negative_squared_cross_mark: Cog: \"{cog}\" unloaded.")
    except commands.errors.ExtensionNotLoaded:
        pass

    client.load_extension(f"cogs.{cog}")
    bot = client.get_cog(className)
    await bot.on_ready()
    await ctx.send(f"Cog: \"{cog}\" reloaded.", hidden=True)


if __name__ == "__main__":
    for cog in settings.DISCORD_COGS:
        client.load_extension(f'cogs.{cog["name"]}')

    DiscordComponents(client)
    client.run(settings.DISCORD_TOKEN)
