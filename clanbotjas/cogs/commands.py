from math import floor
import re
import time

import discord
from discord import option
from discord.ext import commands

from cogmanager import ClanBotjasClient
from cogmanagerlib import commandlogger, has_privileged_role


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
        textToObjects = {}
        for channel in interaction.client.get_all_channels():
            textToObjects[f"#{channel.name}"] = channel.mention
        for member in interaction.client.get_all_members():
            textToObjects[f"@{member.name}"] = member.mention
        for emoji in interaction.client.emojis:
            textToObjects[f":{emoji.name}:"] = f"<:{emoji.name}:{emoji.id}>"
        roles = await interaction.guild.fetch_roles()
        for role in roles:
            if role.name.startswith("@"):
                roleName = role.name
            else:
                roleName = "@" + role.name
            textToObjects[roleName] = role.mention

        names = sorted(textToObjects.keys(), key=lambda x: len(x), reverse=True)
        regex = re.compile("(" + "|".join(names) + ")")

        def stringToMention(match):
            return textToObjects[match[0]]

        text = re.sub(regex, stringToMention, self.children[0].value)
        await interaction.channel.send(text)
        await interaction.response.send_message("Message was sent.", ephemeral=True)


class Commands(commands.Cog):
    def __init__(self, client: ClanBotjasClient):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.broadcast_log_message(':white_check_mark: Cog: "commands" ready.')

    @commands.slash_command(
        description="Make the bot say something."
    )
    @has_privileged_role()
    @commandlogger
    async def say(self, ctx: discord.ApplicationContext):
        await ctx.send_modal(SayCommandModal())

    @commands.slash_command(
        name="ping", description="send ping"
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
        name="purge",
        description="purge messages",
        default_permission=False,
    )
    @has_privileged_role()
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
        default_permission=False,
    )
    @has_privileged_role()
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
