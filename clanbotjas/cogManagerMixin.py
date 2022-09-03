import functools

import discord

import settings


def slashcommandlogger(func):
    """
    Decorator that allows slash commands to be logged
    :param func: original function
    :return: wrapped function
    """

    @functools.wraps(func)
    async def wrapped(self, ctx, *args, **kwargs):
        # Some fancy foo stuff
        await func(self, ctx, *args, **kwargs)
        logChannel = self.client.get_channel(settings.DISCORD_LOG_CHANNEL)

        log_string = ":arrow_forward: Command:  "
        log_string += (
            ctx.channel.mention
            if isinstance(ctx.channel, discord.TextChannel)
            else "????"
        )
        log_string += f" | {ctx.author}: /{ctx.command} "

        for k, v in kwargs.items():
            log_string += f" {k}: {v}"
        await logChannel.send(log_string)

    return wrapped
