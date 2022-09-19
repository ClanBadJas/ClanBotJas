import asyncio

import discord
from discord.ext import commands
from discord import option
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

import cogmanagerlib
import cogs
import models
import settings
from cogmanagerlib import commandlogger


class CogManager(commands.Cog):
    def __init__(self, client: 'ClanBotjasClient'):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.broadcast_log_message(':white_check_mark: Cog: "cogmanager" ready')

    @commands.slash_command(
        description="load a cog",
        default_permission=False,
    )
    @commands.is_owner()
    @option(
        name="cog",
        description="Select Cog",
        required=True,
    )
    @commandlogger
    async def load(self, ctx: discord.ApplicationContext, cog: str):
        """
        Load a cog
        :param ctx: Original slash command context
        :param cog: Name of the cog to load
        :return:
        """
        cog, className = cog.lower(), cog
        try:
            self.client.load_extension(f"cogs.{cog}")
            bot = self.client.get_cog(className)
            await bot.on_ready()
            await ctx.respond(f':white_check_mark: Cog: "{cog}" loaded.')
        except discord.errors.ExtensionAlreadyLoaded:
            await ctx.respond(f'Cog: "{cog}" already loaded.')

    @commands.slash_command(
        description="unload a cog",
        default_permission=False,
    )
    @commands.is_owner()
    @option(
        name="cog",
        description="Select Cog",
        required=True,
        choices=settings.DISCORD_COGS,
    )
    @commandlogger
    async def unload(self, ctx: discord.ApplicationContext, cog: str):
        """
        Unload a cog
        :param ctx: Original slash command context
        :param cog: Name of the cog to unload
        :return:
        """
        cog = cog.lower()
        try:
            self.client.unload_extension(f"cogs.{cog}")
            message = f':negative_squared_cross_mark: Cog: "{cog}" unloaded.'
            await ctx.respond(message)
            await self.client.broadcast_log_message(message)
        except discord.errors.ExtensionNotLoaded:
            await ctx.respond(f'Cog: "{cog}" not loaded.')

    @commands.slash_command(
        description="reload a cog",
        default_permission=False,
    )
    @commands.is_owner()
    @option(
        name="cog",
        description="Select Cog",
        required=True,
        choices=settings.DISCORD_COGS,
    )
    @commandlogger
    async def reload(self, ctx: discord.ApplicationContext, cog: str):
        """
        Reload a cog
        :param ctx: Original slash command context
        :param cog: Name of the cog to reload
        :return:
        """
        # Attempt to unload
        cog, className = cog.lower(), cog
        try:
            self.client.unload_extension(f"cogs.{cog}")
            await self.client.broadcast_log_message(f':negative_squared_cross_mark: Cog: "{cog}" unloaded.')
        except discord.errors.ExtensionNotLoaded:
            pass

        # Load the cog
        self.client.load_extension(f"cogs.{cog}")
        bot = self.client.get_cog(className)
        await bot.on_ready()
        await ctx.respond(f':repeat: Cog: "{cog}" reloaded.')


class ClanBotjasClient(discord.Bot):
    guild_settings: dict[int, cogmanagerlib.GuildSettings] = {}

    async def initialize_guild_settings(self, db_session: sessionmaker):
        async with db_session() as session:
            stmt = select(models.GuildSettings)
            result = await session.execute(stmt)
            for (guild_settings,) in result.unique().all():
                self.guild_settings[guild_settings.guild_id] = cogmanagerlib.GuildSettings(self, guild_settings)

    def __init__(self, db_session):
        super().__init__(
            command_prefix=commands.when_mentioned_or("!"), intents=settings.INTENTS
        )
        self.db_session = db_session
        asyncio.run(self.initialize_guild_settings(db_session))

        self.add_cog(CogManager(self))
        self.add_cog(cogs.GuildSettingCog(self))
        for cog in settings.DISCORD_COGS:
            self.load_extension(f"cogs.{cog.name}")

    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        """
        Give feedback to the user when user has no perms to use the command
        :param ctx: Original command context
        :param error: Error
        :return:
        """

        if isinstance(error, commands.errors.MissingRole):
            await ctx.response.send_message(
                f"{ctx.author.mention}, You do not have permissions to use that command.",
                ephemeral=True,
            )
        elif isinstance(error, commands.errors.MissingPermissions):
            await ctx.response.send_message(
                f"{ctx.author.mention}, {error.args[0]}",
                ephemeral=True,
            )

        else:
            raise error

    async def on_application_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        """
        Give feedback to the user when user has no perms to use the command
        :param ctx: Original command context
        :param error: Error
        :return:
        """
        await self.on_command_error(ctx, error)

    async def broadcast_log_message(self, message: str):
        for guild_settings in self.guild_settings.values():
            if guild_settings.log_channel:
               await guild_settings.log_channel.send(message)
        print(message)

    async def log_message(self, guild: discord.Guild, message: str):
        guild_settings = self.guild_settings.get(guild.id)
        if not guild_settings or not guild_settings.log_channel:
            print(f"{guild.name}: {message}")
        else:
            await guild_settings.log_channel.send(message)


if __name__ == "__main__":
    engine = create_async_engine(settings.DISCORD_DB_LINK, echo=True)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    ClanBotjasClient(async_session).run(settings.DISCORD_TOKEN)
