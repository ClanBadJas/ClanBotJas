import discord
from discord.ext import commands

import settings


class VoiceChannelBot(commands.Cog):
    category = None
    logChannel = None
    initialized = False

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Initialize the bot onready
        :return:
        """
        self.logChannel = self.client.get_channel(settings.DISCORD_LOG_CHANNEL)
        self.category = self.client.get_channel(settings.DISCORD_VOICE_CHANNEL_CATEGORY)
        await self.autoscale()
        await self.logChannel.send(":white_check_mark: Cog: \"voicechannelbot\" ready.")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """
        Autoscale the app when before and after channel are triggered.
        :param member: Not used
        :param before: before channel state
        :param after: after channel state
        :return:
        """

        # await self.autoscale()
        await self.on_member_update(None, None)
        # Make sure This is not an event within the same channel

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """
        check if the user is playing a different game.
        :param after:
        :param before:
        :return:
        """

        if before and after and before.activities == after.activities:
            return

        for voice_channel in {before.voice.channel, after.voice.channel}:
            name = self.get_most_played_game(voice_channel)
            if voice_channel.name != name:
                await self.logChannel.send(
                    f":twisted_rightwards_arrows: AutoRename:	Changed {voice_channel.name} to {name}.")
                await voice_channel.edit(name=name)

    async def autoscale(self):
        """
        Get all empty channels.
        Delete  empty channels if there is more than one.
        If no empty channels exist, create one
        Manually create a channel if none exist
        :return:
        """
        voice_channels = self.category.voice_channels
        template = voice_channels[-1]
        empty_channel = None
        delete_channels = []

        # if all empty channels
        for voice_channel in voice_channels:
            if not voice_channel.members:
                if not empty_channel:
                    empty_channel = voice_channel
                else:
                    delete_channels.append(voice_channel)
        before_channel_count = len(self.category.voice_channels)
        # delete all empty channels, excluding the first empty channel
        for voice_channel in delete_channels:
            await voice_channel.delete()
        if delete_channels:
            delete_amount = len(delete_channels)
            await self.logChannel.send(
                f":arrows_clockwise: AutoScale:		Deleting empty channels. Now managing {before_channel_count - delete_amount} channel(s).")

        # If no empty channel exists, create a new one
        if empty_channel is None:
            empty_channel = await template.clone(name=settings.DISCORD_VOICE_CHANNEL_DEFAULT_NAME)
            await self.logChannel.send(
                f":arrows_clockwise: AutoScale:		New channel created. Now managing {before_channel_count + 1} channels.")

        # Make sure the empty channel is always last
        if self.category.voice_channels[-1] != empty_channel:
            await empty_channel.move(end=True)

    @staticmethod
    def get_most_played_game(voice_channel):
        """
        Get the most played game in a channel and return its name
        :param voice_channel: Voice channel
        :return:
        """
        games = {}
        for member in voice_channel.members:
            for activity in member.activities:
                if activity.type == discord.ActivityType.playing:
                    if activity.name not in games:
                        games[activity.name] = 1
                    else:
                        games[activity.name] += 1
        highest_hitcount = 0
        highest_name = settings.DISCORD_VOICE_CHANNEL_DEFAULT_NAME
        for key, value in games.items():
            if value > highest_hitcount:
                highest_hitcount = value
                highest_name = key
        return highest_name


def setup(client):
    client.add_cog(VoiceChannelBot(client))
