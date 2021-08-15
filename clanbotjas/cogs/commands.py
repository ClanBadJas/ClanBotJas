from math import floor

import discord
from discord.ext import commands
from discord_slash import SlashContext, cog_ext

import settings




class Commands(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.get_channel(settings.DISCORD_LOG_CHANNEL).send("Command cog ready")

    @commands.command()
    async def say(self, ctx):
        logChannel = self.client.get_channel(settings.DISCORD_LOG_CHANNEL)
        if not ctx.guild:
            await ctx.send("Commando only works in a guild")
            return
        if ctx.guild.id != settings.DISCORD_GUILD_ID:
            return
        if not ctx.author.guild_permissions.administrator:
            await ctx.send(f"{ctx.author.mention}, You do not have permissions to use that command.", hidden=True)
            return

        if isinstance(ctx.channel, discord.TextChannel):
            await logChannel.send(
                f":arrow_forward: Command:  {ctx.channel.mention} | {ctx.author.mention}: {ctx.message.content}", )
        else:
            await logChannel.send(f":arrow_forward: Command:  ???? | {ctx.author.mention}: {ctx.message.content}", )

        arg = ctx.message.content[4:].strip() if len(ctx.message.content) > 4 else ''
        if len(arg) == 0:
            await ctx.send(f"{ctx.author.mention}, Please provide a valid message!")
            return

        await ctx.send(ctx.message.content[5:])
        await ctx.message.delete()

    @cog_ext.cog_slash(name="ping",
                       description="send ping",
                       guild_ids=settings.DISCORD_GUILD_IDS,
                       permissions=settings.DISCORD_COMMAND_PERMISSIONS,
                       default_permission=False, )
    async def ping(self, ctx: SlashContext):
        msg = await ctx.send("Ping?")

        latency = msg.created_at - ctx.created_at
        await msg.edit(
            content=f"Pong! Latency is {floor(latency.total_seconds() * 1000)} ms. API Latency is {floor(ctx.bot.latency * 1000)} ms.")

    @cog_ext.cog_slash(name="getid",
                       description="get your user ID",
                       guild_ids=settings.DISCORD_GUILD_IDS)
    async def _getid(self, ctx: SlashContext):
        await ctx.send(content=f"Your id is: {ctx.author.id}", hidden=True)


def setup(client):
    client.add_cog(Commands(client))
