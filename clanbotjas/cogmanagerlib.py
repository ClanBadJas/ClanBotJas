import functools
from typing import TYPE_CHECKING, Callable, TypeVar

if TYPE_CHECKING:
    from cogmanager import ClanBotjasClient

import discord

from discord.ext import commands
from discord.ext.commands import MissingPermissions, MissingRole

import models

T = TypeVar("T")

class GuildSettings(object):
    def __init__(self, client: discord.Client, guild_settings: models.GuildSettings):
        self.client = client
        self.guild_settings = guild_settings

    def __str__(self):
        msg = f"Guild: {self.guild.name if self.guild else 'None'}\n"
        msg += f"Log channel: {self.log_channel.mention if self.log_channel else 'None'}\n"
        msg += f"Privileged command role: {self.privileged_command_role.mention if self.privileged_command_role else 'None'}\n"
        msg += f"Voice scalar category: {self.voice_scalar_category.mention if self.voice_scalar_category else 'None'}\n"
        msg += f"Voice scalar default name: {self.voice_scalar_default_name if self.voice_scalar_default_name else 'None'}\n"
        msg += f"Rolebot settings channel: {self.rolebot_settings_channel.mention if self.rolebot_settings_channel else 'None'}\n"
        msg += f"Auto roles: {self.auto_role_string()}"
        return msg

    @property
    def guild(self) -> discord.Guild:
        guild_id = self.guild_settings.guild_id
        guild = self.client.get_guild(guild_id)
        return guild

    @property
    def log_channel(self) -> discord.TextChannel:
        channel_id = self.guild_settings.log_channel_id
        return self.client.get_channel(channel_id)

    @property
    def privileged_command_role(self) -> discord.Role:
        role_id = self.guild_settings.privileged_command_role_id
        guild = self.guild
        return guild.get_role(role_id) if guild else None

    @property
    def voice_scalar_category(self) -> discord.CategoryChannel:
        channel_id = self.guild_settings.voice_scalar_category_id
        return self.client.get_channel(channel_id)

    @property
    def voice_scalar_default_name(self) -> str:
        return self.guild_settings.voice_scalar_default_name

    @property
    def rolebot_settings_channel(self) -> discord.TextChannel:
        channel_id = self.guild_settings.rolebot_settings_channel_id
        return self.client.get_channel(channel_id)

    @property
    def autoroles(self) -> list[discord.Role]:
        autoroles = []
        for autorole in self.guild_settings.autoroles:
            guild = self.guild
            if not guild:
                continue
            role = guild.get_role(autorole.role_id)
            if role:
                autoroles.append(role)
        return autoroles

    def auto_role_string(self) -> str:
        return f'[{", ".join([role.mention for role in self.autoroles])}]'


async def log_command(client: 'ClanBotjasClient', guild: discord.Guild, log_string: str):
    guild_settings = client.guild_settings.get(guild.id)

    if guild_settings and guild_settings.log_channel:
        await guild_settings.log_channel.send(log_string)
    else:
        print(log_string)


class LogSelect(discord.ui.Select):
    valueToLabel = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for option in self.options:
            self.valueToLabel[option.value] = option.label

    async def callback(self, interaction: discord.Interaction):
        opts = ", ".join([self.valueToLabel[value] for value in self.values])
        log_string = f":ballot_box_with_check: Options selected | {interaction.channel.mention} | {interaction.user} selected: ({opts})."
        await log_command(interaction.client, interaction.guild, log_string)


class LogButton(discord.ui.Button):
    async def callback(self, interaction: discord.Interaction):

        log_string = f":radio_button: Button clicked | {interaction.channel.mention} | {interaction.user} clicked ({self.label})."

        await log_command(interaction.client, interaction.guild, log_string)


def commandlogger(func):
    """
    Decorator that logs commands
    :param func: original function
    :return: wrapped function
    """

    @functools.wraps(func)
    async def wrapped(self: commands.Cog, ctx: discord.ApplicationContext, *args, **kwargs):
        await func(self, ctx, *args, **kwargs)
        log_string = f":arrow_forward: {type(ctx.command).__name__}:  "
        log_string += (
            ctx.channel.mention
            if isinstance(ctx.channel, discord.TextChannel)
            else "????"
        )
        log_string += f' | {ctx.author}, command=`{ctx.command}`'
        kwargs = ", ".join([f" {k}: {v}" for k, v in kwargs.items() if v is not None])
        if kwargs:
            log_string += f", kwargs=`{{{kwargs}}}`"

        await log_command(self.client, ctx.guild, log_string)

    return wrapped


def has_privileged_role() -> Callable[[T], T]:
    """A :func:`.check` that checks if the person invoking this command is Either
    administrator, or has the privilegd_command_role.
    """

    async def predicate(ctx: commands.Context) -> bool:
        guild_settings: GuildSettings = ctx.cog.client.guild_settings.get(ctx.guild.id)
        permissions = ctx.channel.permissions_for(ctx.author)
        if permissions.administrator:
            print("accepted, because admin")
            return True
        elif not guild_settings or not guild_settings.privileged_command_role:
            raise MissingPermissions(["administrator"])
        elif guild_settings.privileged_command_role in ctx.author.roles:
            return True
        else:
            raise MissingRole(guild_settings.privileged_command_role.id)

    return commands.check(predicate)
