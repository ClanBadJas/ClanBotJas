import discord
from discord.ext import commands
import settings


class Say(commands.Cog):

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
        print("say commands")
        if ctx.author.guild_permissions.administrator:
            await ctx.send(ctx.message.content[5:])
            await ctx.message.delete()


def setup(client):
    client.add_cog(Say(client))
