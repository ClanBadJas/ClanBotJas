import discord
from discord.ext import commands
from discord import option
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

import settings
from cogmanagermixin import commandlogger
from models import AutoRole


class CogManager(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.get_channel(settings.DISCORD_LOG_CHANNEL).send(
            ':white_check_mark: Cog: "cogmanager" ready'
        )


    @commands.slash_command(
        description="load a cog",
        guild_ids=settings.DISCORD_GUILD_IDS,
        default_permission=False,
    )
    @commands.has_role(settings.DISCORD_COMMAND_PERMISSION_ROLE)
    @option(
        name="cog",
        description="Select Cog",
        required=True,
        choices=settings.DISCORD_COGS,
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
            await ctx.respond(f'Cog: "{cog}" loaded.')
        except discord.errors.ExtensionAlreadyLoaded:
            await ctx.respond(f'Cog: "{cog}" already loaded.')

    @commands.slash_command(
        description="unload a cog",
        guild_ids=settings.DISCORD_GUILD_IDS,
        default_permission=False,
    )
    @commands.has_role(settings.DISCORD_COMMAND_PERMISSION_ROLE)
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
            await ctx.respond(f'Cog: "{cog}" unloaded.')
            await self.client.get_channel(settings.DISCORD_LOG_CHANNEL).send(
                f':negative_squared_cross_mark: Cog: "{cog}" unloaded.'
            )
        except discord.errors.ExtensionNotLoaded:
            await ctx.respond(f'Cog: "{cog}" not loaded.')

    @commands.slash_command(
        description="reload a cog",
        guild_ids=settings.DISCORD_GUILD_IDS,
        default_permission=False,
    )
    @commands.has_role(settings.DISCORD_COMMAND_PERMISSION_ROLE)
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
            await self.client.get_channel(settings.DISCORD_LOG_CHANNEL).send(
                f':negative_squared_cross_mark: Cog: "{cog}" unloaded.'
            )
        except discord.errors.ExtensionNotLoaded:
            pass

        # Load the cog
        self.client.load_extension(f"cogs.{cog}")
        bot = self.client.get_cog(className)
        await bot.on_ready()
        await ctx.respond(f'Cog: "{cog}" reloaded.')


class ClanBotjasClient(discord.Bot):
    def __init__(self, db_session):
        super().__init__(
            command_prefix=commands.when_mentioned_or("!"), intents=settings.INTENTS
        )
        self.add_cog(CogManager(self))
        for cog in settings.DISCORD_COGS:
            self.load_extension(f"cogs.{cog.name}")
        self.db_session = db_session

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
        if isinstance(error, commands.errors.MissingPermissions):
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


def _build_async_db_uri(uri):
    if "+aiosqlite" not in uri:
        return '+aiosqlite:'.join(uri.split(":", 1))
    return uri


if __name__ == "__main__":
    engine = create_async_engine(
        _build_async_db_uri(settings.DISCORD_DB_LINK),
        echo=True,
    )
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    ClanBotjasClient(async_session).run(settings.DISCORD_TOKEN)
