import functools
from dotenv import load_dotenv

import discord
from discord.ext import commands
from discord import option, Permissions

import settings


async def logCommand(channel, ctx, *args, **kwargs):
    log_string = ":arrow_forward: Command:  "
    log_string += ctx.channel.mention if isinstance(ctx.channel, discord.TextChannel) else "????"
    log_string += f" | {ctx.author}: /{ctx.command} "
 
    for k, v in kwargs.items():
        log_string += f" {k}: {v}"
    await channel.send(log_string)


client = commands.Bot(command_prefix=commands.when_mentioned_or("!"), intents=settings.INTENTS)
@client.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    """
    Give feedback to the user when he has no rights to use the command
    :param ctx: original command context
    :param error: Eroor
    :return:
    """

    if isinstance(error, commands.errors.MissingRole):
        await ctx.response.send_message(f"{ctx.author.mention}, You do not have permissions to use that command.", ephemeral=True)
    else:
        raise error

@client.event
async def on_application_command_error(ctx: commands.Context, error: commands.CommandError):
    """
    Give feedback to the user when he has no rights to use the command
    :param ctx: original command context
    :param error: Eroor
    :return:
    """
    await on_command_error(ctx, error)

def slashcommandlogger(func):
    """
    Decorator to log slash commands
    :param func: wrapped function
    :return:
    """
    @functools.wraps(func)
    async def wrapped(ctx, cog: str):
        # Some fancy foo stuff
        await logCommand(client.get_channel(settings.DISCORD_LOG_CHANNEL), ctx, cog=cog.lower())
        await func(ctx, cog)

    return wrapped

@client.slash_command(description="load a cog",
                      guild_ids=settings.DISCORD_GUILD_IDS,
                      default_permission=False)
@commands.has_role(settings.DISCORD_COMMAND_PERMISSION_ROLE)
@option(name="cog", 
        description="Select Cog", 
        required=True,
        choices=settings.DISCORD_COGS
)
@slashcommandlogger
async def load(ctx: discord.ApplicationContext, cog: str):
    """
    Load a cog
    :param ctx:  slash command context
    :param cog: name of the cog
    :return:
    """
    cog, className = cog.lower(), cog
    try:
        client.load_extension(f"cogs.{cog}")
        bot = client.get_cog(className)
        await bot.on_ready()
        await ctx.respond(f"Cog: \"{cog}\" loaded.")
    except discord.errors.ExtensionAlreadyLoaded:
        await ctx.respond(f"Cog: \"{cog}\" already loaded.")

@client.slash_command(description="unload a cog",
                      guild_ids=settings.DISCORD_GUILD_IDS,
                      default_permission=False)
@commands.has_role(settings.DISCORD_COMMAND_PERMISSION_ROLE)
@option(name="cog", 
        description="Select Cog", 
        required=True,
        choices=settings.DISCORD_COGS
)
@slashcommandlogger
async def unload(ctx, cog: str):
    """
    Unload a cog
    :param ctx: Original slash command context
    :param cog: Name of the cog to unload
    :return:
    """
    cog = cog.lower()
    try:
        client.unload_extension(f"cogs.{cog}")
        await ctx.respond(f"Cog: \"{cog}\" unloaded.")
        await client.get_channel(settings.DISCORD_LOG_CHANNEL).send(f":negative_squared_cross_mark: Cog: \"{cog}\" unloaded.")
    except discord.errors.ExtensionNotLoaded:
        await ctx.respond(f"Cog: \"{cog}\" not loaded.")

@client.slash_command(description="reload a cog",
                      guild_ids=settings.DISCORD_GUILD_IDS,
                      default_permission=False)
@commands.has_role(settings.DISCORD_COMMAND_PERMISSION_ROLE)
@option(name="cog", 
        description="Select Cog", 
        required=True,
        choices=settings.DISCORD_COGS
)
@slashcommandlogger
async def reload(ctx, cog: str):
    """
    Reload a cog
    :param ctx:  original slash command context
    :param cog: Name of the cog to reload
    :return:
    """
    # Attempt to unload
    cog, className = cog.lower(), cog
    try:
        client.unload_extension(f"cogs.{cog}")
        await client.get_channel(settings.DISCORD_LOG_CHANNEL).send(f":negative_squared_cross_mark: Cog: \"{cog}\" unloaded.")
    except discord.errors.ExtensionNotLoaded:
        pass

    # Load the cog
    client.load_extension(f"cogs.{cog}")
    bot = client.get_cog(className)
    await bot.on_ready()
    await ctx.send(f"Cog: \"{cog}\" reloaded.")


if __name__ == "__main__":
    # Load all cogs
    for cog in settings.DISCORD_COGS:
        client.load_extension(f'cogs.{cog.name}')

    client.run(settings.DISCORD_TOKEN)
