from math import floor

import discord
from discord.ext import commands
import settings


class Commands(commands.Cog):

    def __init__(self, client):
        self.client = client

    @staticmethod
    def has_role(member, role_id):
        for role in member.roles:
            if role.id == role_id:
                return True
        return False

    @commands.command()
    async def say(self, ctx):

        arg = ctx.message.content[4:].strip() if len(ctx.message.content) > 4 else ''

        if len(arg) == 0:
            await ctx.send(f"{ctx.author.mention}, Please provide a valid message!")
            return


        await ctx.send(ctx.message.content[5:])
        await ctx.message.delete()

    @commands.command()
    async def ping(selfself, ctx):
        msg = await ctx.send("Ping?")

        latency = msg.created_at - ctx.message.created_at
        await msg.edit(f"Pong! Latency is {floor(latency.total_seconds() * 1000)} ms. API Latency is {floor(ctx.bot.latency * 1000)} ms.")

def setup(client):
    client.add_cog(Commands(client))
