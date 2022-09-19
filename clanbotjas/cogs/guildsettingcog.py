from typing import Optional

import discord
from discord import Option, Role, SlashCommandGroup, TextChannel, CategoryChannel
from discord.ext import commands
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import cogmanager
import cogmanagerlib
import models

from cogmanagerlib import commandlogger


class GuildSettingCog(commands.Cog):

    def __init__(self, client: cogmanager.ClanBotjasClient):
        self.client = client

    @staticmethod
    async def get_or_create_guild_settings(session: AsyncSession, guild: discord.Guild, **kwargs) -> models.GuildSettings:
        attributes = {}
        for k, v in kwargs.items():
            if isinstance(v, discord.abc.Snowflake):
                attributes[k + '_id'] = v.id
            else:
                attributes[k] = v

        stmt = select(models.GuildSettings).where(models.GuildSettings.guild_id == guild.id)
        result = await session.execute(stmt)
        row = result.first()
        guild_settings = row[0] if row else None
        if guild_settings:
            for k, v in attributes.items():
                setattr(guild_settings, k, v)
        else:
            guild_settings = models.GuildSettings(guild_id=guild.id, **attributes)
            session.add(guild_settings)

        return guild_settings

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Initialize the bot onready
        :return:
        """
        await self.client.broadcast_log_message(':white_check_mark: Cog: "guildsettings" ready.')

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        async with self.client.db_session() as session:
            guild_settings = await self.get_or_create_guild_settings(session, guild)
        self.client.guild_settings[guild.id] = cogmanagerlib.GuildSettings(self.client, guild_settings)

    settingsCommandGroup = SlashCommandGroup("settings", "Settings to configure this bot.")

    @settingsCommandGroup.command(
        description="Show configured settings",
    )
    @commands.has_permissions(administrator=True)
    @commandlogger
    async def show(self, ctx: discord.ApplicationContext):
        guild_settings = self.client.guild_settings.get(ctx.guild.id)
        if guild_settings:
            await ctx.respond(guild_settings.__str__())
        else:
            await ctx.respond("No settings have been configured in this guild.")

    @settingsCommandGroup.command(
        description="change log channel",
    )
    @commands.has_permissions(administrator=True)
    @commandlogger
    async def general(self, ctx: discord.ApplicationContext,
                      log_channel: Optional[TextChannel],
                      privileged_command_role: Optional[Role],
                      voice_scalar_category: Optional[CategoryChannel],
                      voice_scalar_default_name: Optional[str],
                      rolebot_settings_channel: Optional[TextChannel]):
        options = {
            "log_channel": log_channel,
            "privileged_command_role": privileged_command_role,
            "voice_scalar_category": voice_scalar_category,
            "voice_scalar_default_name": voice_scalar_default_name,
            "rolebot_settings_channel": rolebot_settings_channel,
        }
        # Filter out all options which are not getting set
        options = {k: v for k, v in options.items() if v is not None}

        async with self.client.db_session() as session:
            guild_settings = await self.get_or_create_guild_settings(session, ctx.guild, **options)
            await session.commit()

        if options:
            self.client.guild_settings[ctx.guild.id] = cogmanagerlib.GuildSettings(self.client, guild_settings)
            msg = "Configuring the following settings:\n"
            for k, v in options.items():
                msg += f'{k.replace("_", " ")}: {v.mention if hasattr(v, "mention") else v}\n'
            await ctx.respond(msg)
        else:
            await ctx.respond("You need to set at least one option", ephemeral=True)

    autorole = settingsCommandGroup.create_subgroup("autorole", "autorole related commands")

    @autorole.command(
        description="add autorole",
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

        async with self.client.db_session() as session:
            auto_role = models.AutoRole(role_id=role.id, guild_id=ctx.guild.id)
            guild_settings = await self.get_or_create_guild_settings(session, ctx.guild)
            if auto_role in guild_settings.autoroles:
                await ctx.respond(content=f"{role.mention} already included in auto roles.")
                return
            guild_settings.autoroles.append(auto_role)
            await session.commit()

        self.client.guild_settings[ctx.guild.id] = cogmanagerlib.GuildSettings(self.client, guild_settings)
        await ctx.respond(content=f"Added the {role.mention} role to autorole.")

    @autorole.command(
        description="remove autorole",
    )
    @commands.has_permissions(manage_roles=True)
    @commandlogger
    async def remove(self, ctx: discord.ApplicationContext, role: Option(Role)):
        async with self.client.db_session() as session:
            stmt = delete(models.AutoRole).where(models.AutoRole.role_id == role.id)
            result = await session.execute(stmt)
            guild_settings = await self.get_or_create_guild_settings(session, ctx.guild)
            await session.commit()
            deleted_role = result.rowcount > 0

        self.client.guild_settings[ctx.guild.id] = cogmanagerlib.GuildSettings(self.client, guild_settings)
        if deleted_role:
            await ctx.respond(content=f"Deleted {role.mention} from autorole.")
        else:
            await ctx.respond(content=f"{role.mention} not in autorole")