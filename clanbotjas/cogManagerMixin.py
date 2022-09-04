import functools

import discord

import settings


class LogSelect(discord.ui.Select):
    valueToLabel = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for option in self.options:
            self.valueToLabel[option.value] = option.label

    async def callback(self, interaction: discord.Interaction):
        logChannel = interaction.client.get_channel(settings.DISCORD_LOG_CHANNEL)
        opts = ", ".join([self.valueToLabel[value] for value in self.values])

        await logChannel.send(
            f":ballot_box_with_check: Options selected | {interaction.channel.mention} | {interaction.user} selected: ({opts})."
        )


class LogButton(discord.ui.Button):
    async def callback(self, interaction: discord.Interaction):
        logChannel = interaction.client.get_channel(settings.DISCORD_LOG_CHANNEL)
        await logChannel.send(
            f":radio_button: Button clicked | {interaction.channel.mention} | {interaction.user} clicked ({self.label})."
        )


def commandlogger(func):
    """
    Decorator that allows slash commands to be logged
    :param func: original function
    :return: wrapped function
    """

    def slashCommand(ctx, kwargs):
        log_string = ":arrow_forward: SlashCommand:  "
        log_string += (
            ctx.channel.mention
            if isinstance(ctx.channel, discord.TextChannel)
            else "????"
        )
        log_string += f" | {ctx.author}: /{ctx.command} "

        for k, v in kwargs.items():
            if v is not None:
                log_string += f" {k}: {v}"
        return log_string

    def messageCommand(ctx):
        log_string = ":arrow_forward: MessageCommand:  "
        log_string += (
            ctx.channel.mention
            if isinstance(ctx.channel, discord.TextChannel)
            else "????"
        )
        log_string += f' | {ctx.author}: "{ctx.command}"'
        return log_string

    def otherCommand(ctx):
        log_string = ":arrow_forward: OtherCommand:  "
        log_string += (
            ctx.channel.mention
            if isinstance(ctx.channel, discord.TextChannel)
            else "????"
        )
        log_string += f' | {ctx.author}: "{ctx.command}"'
        return log_string

    @functools.wraps(func)
    async def wrapped(self, ctx, *args, **kwargs):
        # Some fancy foo stuff
        await func(self, ctx, *args, **kwargs)
        if isinstance(ctx.command, discord.MessageCommand):
            msg = messageCommand(ctx)
        elif isinstance(ctx.command, (discord.SlashCommand, discord.SlashCommandGroup)):
            msg = slashCommand(ctx, kwargs)
        else:
            msg = otherCommand(ctx)
        logChannel = self.client.get_channel(settings.DISCORD_LOG_CHANNEL)
        await logChannel.send(msg)

    return wrapped
