import discord
from discord.ext import commands
import cogmanager

from cogmanagerlib import commandlogger


class AutoRole(commands.Cog):
    logChannel = None

    def __init__(self, client: cogmanager.ClanBotjasClient):
        self.client = client

    """
    When new member joins the server, cycle through the configured roles.
    Get the role ID of the roles by name.
    Add the role to the newly joined member.
    :return:
    """
    async def add_auto_roles(self, member: discord.Member):
        guild_settings = self.client.guild_settings.get(member.guild.id)
        if not guild_settings or not guild_settings.autoroles:
            return ":negative_squared_cross_mark: Auto roles not configured"
        roles = guild_settings.autoroles
        role_text = guild_settings.auto_role_string()
        try:
            await member.add_roles(*tuple(roles))
            return f':ballot_box_with_check: Roles: {role_text} added for user {member.name}.'
        except discord.errors.Forbidden:
            return f':negative_squared_cross_mark: autorole cannot add the following roles: {role_text}.'

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Initialize the bot on_ready
        :return:
        """
        await self.client.broadcast_log_message(':white_check_mark: Cog: "autorole" ready.')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        response = await self.add_auto_roles(member)
        await self.logChannel.send(response)

    @commands.user_command(
        name="add auto roles",
        description="add auto roles",
    )
    @commands.has_permissions(manage_roles=True)
    @commandlogger
    async def add_auto_role_command(
            self, ctx: discord.ApplicationContext, member: discord.Member
    ):
        response = await self.add_auto_roles(member)
        await ctx.respond(content=response, ephemeral=True)


def setup(client):
    client.add_cog(AutoRole(client))
