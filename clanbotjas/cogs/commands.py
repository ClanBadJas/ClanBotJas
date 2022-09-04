from math import floor
import time

import discord
from discord import option
from discord.ext import commands

import settings
from cogmanagermixin import commandlogger


class SayCommandModal(discord.ui.Modal):
    def __init__(self) -> None:
        super().__init__(title="Modal via Slash Command")
        self.add_item(
            discord.ui.InputText(
                label="Say command input",
                style=discord.InputTextStyle.long,
                max_length=2000,
            )
        )

    async def callback(self, interaction: discord.Interaction):
        text = self.children[0].value
        for channel in interaction.client.get_all_channels():
            channelName = "#" + channel.name
            if channelName in text:
                text = text.replace(channelName, channel.mention)
        for member in interaction.client.get_all_members():
            memberName = "@" + member.name
            if memberName in text:
                text = text.replace(memberName, member.mention)
        for role in await interaction.client.get_guild(
            settings.DISCORD_GUILD_ID
        ).fetch_roles():
            if role.name.startswith("@"):
                roleName = role.name
            else:
                roleName = "@" + role.name

            if roleName in text:
                text = text.replace(roleName, role.mention)

        await interaction.channel.send(text)
        await interaction.response.send_message("Message was sent.", ephemeral=True)


class Commands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.get_channel(settings.DISCORD_LOG_CHANNEL).send(
            ':white_check_mark: Cog: "commands" ready.'
        )

    @commands.slash_command(
        description="Make the bot say something.", guild_ids=settings.DISCORD_GUILD_IDS
    )
    @commands.has_role(settings.DISCORD_COMMAND_PERMISSION_ROLE)
    @commandlogger
    async def say(self, ctx: discord.ApplicationContext):
        await ctx.send_modal(SayCommandModal())

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
