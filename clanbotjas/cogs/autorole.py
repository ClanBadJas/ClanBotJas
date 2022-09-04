import discord
from discord.ext import commands
from discord.utils import get
from cogManagerMixin import commandlogger

import settings


class AutoRole(commands.Cog):
    guild = None
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
                await self.logChannel.send(
                    "Discord AutoRole cog failed: One or more configured roles are missing on the server."
                )
                return

        await self.logChannel.send(':white_check_mark: Cog: "autorole" ready.')

    """
    When new member joins the server, cycle through the configured roles.
    Get the role ID of the roles by name.
    Add the role to the newly joined member.
    :return:
    """

    async def add_auto_roles(self, member):
        for i in self.autoRoles:
            role = get(self.guild.roles, name=i)
            await member.add_roles(role)
        roles = settings.DISCORD_AUTO_ROLES
        return f'Roles: "{roles}" added for new user {member.name}.'

    @commands.Cog.listener()
    async def on_member_join(self, member):
        reponse = await self.add_auto_roles(member)
        await self.logChannel.send(f":ballot_box_with_check: {reponse}")

    @commands.user_command(
        name="add auto roles",
        description="add auto roles",
        guild_ids=settings.DISCORD_GUILD_IDS,
        default_permission=False,
    )
    @commands.has_role(settings.DISCORD_COMMAND_PERMISSION_ROLE)
    @commandlogger
    async def add_auto_role_command(
        self, ctx: discord.ApplicationContext, member: discord.Member
    ):
        reponse = await self.add_auto_roles(member)
        await ctx.respond(content=reponse, ephemeral=True)


def setup(client):
    client.add_cog(AutoRole(client))
