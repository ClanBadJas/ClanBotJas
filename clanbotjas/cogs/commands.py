from math import floor
import time

import discord
from discord import option
from discord.ext import commands

import settings
from cogManagerMixin import commandlogger


class Commands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.get_channel(settings.DISCORD_LOG_CHANNEL).send(
            ':white_check_mark: Cog: "commands" ready.'
        )

    @commands.command()
    @commands.has_role(settings.DISCORD_COMMAND_PERMISSION_ROLE)
    async def say(self, ctx):
        """
        The say command will echo the user's arguments and delete the original message
        :param ctx:
        :return:
        """
        if not ctx.guild:
            return await ctx.respond("Command only works in a guild.")

        if ctx.guild.id != settings.DISCORD_GUILD_ID:
            return await ctx.respond(
                f"{ctx.author.mention}, Bot is not set up for this guild.", hidden=True
            )

        if len(ctx.message.content) <= 4 or len(ctx.message.content[4:].strip()) == 0:
            return await ctx.respond(
                f"{ctx.author.mention}, Please provide a valid message!"
            )

        # Send arguments as message  and delete the original
        await ctx.send(ctx.message.content[5:])
        await ctx.message.delete()

        logChannel = self.client.get_channel(settings.DISCORD_LOG_CHANNEL)
        channel = (
            ctx.channel.mention
            if isinstance(ctx.channel, discord.TextChannel)
            else "????"
        )
        await logChannel.send(
            f":arrow_forward: Command:  {channel} | {ctx.author.mention}: {ctx.message.content}.",
        )

    @commands.slash_command(
        name="ping", description="send ping", guild_ids=settings.DISCORD_GUILD_IDS
    )
    @commandlogger
    async def ping(self, ctx: discord.ApplicationContext):
        """
        Simple ping command to get the latency of the bot
        :param ctx: object of the original command
        :return:
        """
        start = time.perf_counter()
        msg = await ctx.respond(f"ping?")
        latency = floor((time.perf_counter() - start) * 1000)
        await msg.edit_original_message(
            content=f"Pong! Latency is {latency} ms. API Latency is {floor(ctx.bot.latency * 1000)} ms."
        )

    @commands.slash_command(
        description="get your user ID", guild_ids=settings.DISCORD_GUILD_IDS
    )
    @commandlogger
    async def getid(self, ctx: discord.ApplicationContext):
        """
        Prints the User ID of the requester
        :param ctx: Object of the original command
        :return:
        """
        await ctx.respond(content=f"Your id is: {ctx.author.id}", ephemeral=True)

    @commands.slash_command(
        name="purge",
        description="purge messages",
        guild_ids=settings.DISCORD_GUILD_IDS,
        default_permission=False,
    )
    @commands.has_role(settings.DISCORD_COMMAND_PERMISSION_ROLE)
    @option(
        name="amount",
        description="Amount of messages to purge",
        required=True,
        min_value=1,
        max_value=100,
    )
    @commandlogger
    async def purge(self, ctx: discord.ApplicationContext, amount: int):
        await ctx.channel.purge(limit=amount)
        await ctx.respond(content=f"Purged the last {amount} message(s).")

    @commands.message_command(
        name="purge after",
        description="purge messages",
        guild_ids=settings.DISCORD_GUILD_IDS,
        default_permission=False,
    )
    @commands.has_role(settings.DISCORD_COMMAND_PERMISSION_ROLE)
    @commandlogger
    async def purge_after(
        self, ctx: discord.ApplicationContext, message: discord.Message
    ):
        reason = f"Purged the messages since {message.created_at}."
        await ctx.channel.purge(
            after=message.created_at,
            reason=reason,
        )
        await ctx.respond(content=reason)


def setup(client):
    client.add_cog(Commands(client))
