import functools
from math import floor

import discord
from discord.ext import commands
from discord_slash import SlashContext, cog_ext

import cogmanager
import settings


def slashcommandlogger(func):
    """
    Decorator that allows slash commands to be logged
    :param func: original function
    :return: wrapped function
    """
    @functools.wraps(func)
    async def wrapped(self, ctx, *args, **kwargs):
        # Some fancy foo stuff
        await func(self, ctx, *args, **kwargs)
        logChannel = self.client.get_channel(settings.DISCORD_LOG_CHANNEL)
        await cogmanager.logCommand(logChannel, ctx, **kwargs)
    return wrapped


class Commands(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.get_channel(settings.DISCORD_LOG_CHANNEL).send(":white_check_mark: Cog: \"commands\" ready.")

    @commands.command()
    @commands.has_role(settings.DISCORD_COMMAND_PERMISSION_ROLE)
    async def say(self, ctx):
        """
        The say command will echo the user's arguments and delete the original message
        :param ctx:
        :return:
        """
        if not ctx.guild:
            return await ctx.send("Command only works in a guild.")

        if ctx.guild.id != settings.DISCORD_GUILD_ID:
            return await ctx.send(f"{ctx.author.mention}, Bot is not set up for this guild.", hidden=True)

        if len(ctx.message.content) <= 4 or len(ctx.message.content[4:].strip()) == 0:
            return await ctx.send(f"{ctx.author.mention}, Please provide a valid message!")

        # Send arguments as message  and delete the original
        await ctx.send(ctx.message.content[5:])
        await ctx.message.delete()

        logChannel = self.client.get_channel(settings.DISCORD_LOG_CHANNEL)
        channel = ctx.channel.mention if isinstance(ctx.channel, discord.TextChannel) else "????"
        await logChannel.send(f":arrow_forward: Command:  {channel} | {ctx.author.mention}: {ctx.message.content}.", )

    @cog_ext.cog_slash(name="ping",
                       description="send ping",
                       guild_ids=settings.DISCORD_GUILD_IDS,
                       permissions=settings.DISCORD_COMMAND_PERMISSIONS,
                       default_permission=False, )
    @slashcommandlogger
    async def ping(self, ctx: SlashContext):
        """
        Simple ping command to get the latency of the bot
        :param ctx: object of the original command
        :return:
        """
        msg = await ctx.send("Ping?")

        latency = floor((msg.created_at - ctx.created_at).total_seconds() * 1000)
        await msg.edit(content=f"Pong! Latency is {latency} ms. API Latency is {floor(ctx.bot.latency * 1000)} ms.")

    @cog_ext.cog_slash(name="getid",
                       description="get your user ID",
                       guild_ids=settings.DISCORD_GUILD_IDS)
    @slashcommandlogger
    async def _getid(self, ctx: SlashContext):
        """
        Give the user its ID.
        :param ctx: Object of the original command
        :return:
        """
        await ctx.send(content=f"Your id is: {ctx.author.id}", hidden=True)


def setup(client):
    client.add_cog(Commands(client))
