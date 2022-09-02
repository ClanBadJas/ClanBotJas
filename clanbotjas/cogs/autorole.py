import discord
from discord.ext import commands
from discord.utils import get

import settings


class AutoRole(commands.Cog):
    guild= None
    roleMap = {}
    autoRoles = []
    logChannel = None

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Initialize the bot onready
        :return:
        """
        self.guild = await self.client.fetch_guild(settings.DISCORD_GUILD_ID)
        self.logChannel = self.client.get_channel(settings.DISCORD_LOG_CHANNEL)
        self.autoRoles = settings.DISCORD_AUTO_ROLES.split(",")

        """
        Create a dictionary that maps the names of roles.
        :return:
        """
        roles = await self.guild.fetch_roles()
        for role in roles:
            self.roleMap[role.name] = role

        """
        Verify that configured roles exist.
        :return:
        """
        for i in self.autoRoles:
            if i not in self.roleMap:
                await self.logChannel.send("Discord AutoRole cog failed: One or more configured roles are missing on the server.")
                return

        await self.logChannel.send(":white_check_mark: Cog: \"autorole\" ready.")

    """
    When new member joins the server, cycle through the configured roles.
    Get the role ID of the roles by name.
    Add the role to the newly joined member.
    :return:
    """
    @commands.Cog.listener()
    async def on_member_join(self, member):
        for i in self.autoRoles:
            role = get(self.guild.roles, name=i)
            await member.add_roles(role)
        roles = settings.DISCORD_AUTO_ROLES
        await self.logChannel.send(f":ballot_box_with_check: Roles: \"{roles}\" added for new user {member.name}.")

def setup(client):
    client.add_cog(AutoRole(client))
