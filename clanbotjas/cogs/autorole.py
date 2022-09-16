import discord
from discord import Option, Role, SlashCommandGroup
from discord.ext import commands
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
import models

from cogmanagermixin import commandlogger

import settings


class AutoRole(commands.Cog):
    autoRoleMap = {}
    logChannel = None

    def __init__(self, client):
        self.client = client

    async def getAutoRoles(self, guild):
        roles = set()
        async with self.client.db_session() as session:
            stmt = select(models.AutoRole).where(models.AutoRole.guild_id == guild.id)
            result = await session.execute(stmt)
            for autorole in result.scalars():
                roles.add(guild.get_role(autorole.role_id))
        return roles

    """
    When new member joins the server, cycle through the configured roles.
    Get the role ID of the roles by name.
    Add the role to the newly joined member.
    :return:
    """
    async def add_auto_roles(self, member: discord.Member):
        roles = self.autoRoleMap[member.guild]
        roleText = ", ".join([role.mention for role in roles])
        try:
            await member.add_roles(*tuple(roles))
            return f'Roles: {roleText} added for user {member.name}.'
        except discord.errors.Forbidden:
            return f'autorole cannot add the following roles:{roleText}.'

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Initialize the bot onready
        :return:
        """
        for guild in self.client.guilds:
            self.autoRoleMap[guild] = await self.getAutoRoles(guild)
        await self.client.get_channel(settings.DISCORD_LOG_CHANNEL).send(
            ':white_check_mark: Cog: "autorole" ready.'
        )

    @commands.Cog.listener()
    async def on_member_join(self, member):
        reponse = await self.add_auto_roles(member)
        await self.logChannel.send(f":ballot_box_with_check: {reponse}")

    @commands.user_command(
        name="add auto roles",
        description="add auto roles",
        default_permission=True,
    )
    @commands.has_permissions(manage_roles=True)
    @commandlogger
    async def add_auto_role_command(
            self, ctx: discord.ApplicationContext, member: discord.Member
    ):
        reponse = await self.add_auto_roles(member)
        await ctx.respond(content=reponse, ephemeral=True)

    autorole = SlashCommandGroup("autorole", "autorole related commands")

    @autorole.command(
        description="add autorole",
        default_permission=True,
    )
    @commands.has_permissions(manage_roles=True)
    @commandlogger
    async def add(self, ctx: discord.ApplicationContext, role: Option(Role)):
        bot_member = ctx.guild.get_member(self.client.user.id)
        if role.is_bot_managed():
            await ctx.respond(content=f'Autorole cannot add the bot role {role.mention} to users.')
            return
        if role >= bot_member.top_role:
            await ctx.respond(content=f'Autorole cannot assign the {role.mention} role to users.')
            return

        auto_role = models.AutoRole(role_id=role.id, guild_id=ctx.guild.id)
        async with self.client.db_session() as session:
            try:
                session.add(auto_role)
                await session.commit()
                added_role = True
            except IntegrityError:
                added_role = False
        if added_role:
            self.autoRoleMap[ctx.guild].add(role)
            await ctx.respond(content=f"Added the {role.mention} role to autorole.")
        else:
            await ctx.respond(content=f"Couldn't add the {role.mention} role to autorole.")

    @autorole.command(
        description="remove autorole",
        default_permission=True,
    )
    @commands.has_permissions(manage_roles=True)
    @commandlogger
    async def remove(self, ctx: discord.ApplicationContext, role: Option(Role)):
        async with self.client.db_session() as session:
            stmt = delete(models.AutoRole).where(models.AutoRole.role_id == role.id)
            result = await session.execute(stmt)
            await session.commit()
            deleted_role = result.rowcount > 0
        if deleted_role:
            self.autoRoleMap[ctx.guild].remove(role)
            await ctx.respond(content=f"Deleted {role.mention} from autorole.")
        else:
            await ctx.respond(content=f"{role.mention} not in autorole")

    @autorole.command(
        description="Synchronizes the autoroles and shows them in a list.",
        default_permission=True,
    )
    @commands.has_permissions(manage_roles=True)
    @commandlogger
    async def show(self, ctx: discord.ApplicationContext):
        roles = await self.getAutoRoles(ctx.guild)
        self.autoRoleMap[ctx.guild] = roles
        rolesText = ", ".join([role.mention for role in roles])
        await ctx.respond(content=f"current autoroles: {rolesText}")


def setup(client):
    client.add_cog(AutoRole(client))
