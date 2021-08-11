import discord

LOG_CHANNEL = 875104706647699496


class BaseDiscordBot(discord.Client):
    logChannel = None

    async def on_ready(self):
        self.logChannel = self.get_channel(LOG_CHANNEL)

    async def log(self, message):
        await self.logChannel.send(message)
