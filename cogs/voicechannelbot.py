import discord
from discord.ext import commands

import settings


class VoiceChannelBot(commands.Cog):
    category = None
    logChannel = None
    initialized = False

    def __init__(self, client):
        self.client = client

    async def initialize(self):
        self.logChannel = self.client.get_channel(settings.LOG_CHANNEL)

        await self.logChannel.send("Voice channel cog connected")
        self.category = self.client.get_channel(settings.VOICE_CATEGORY_ID)
        await self.autoscale()
        await self.logChannel.send("Voice channel cog ready")

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.initialized:
            await self.initialize()

    @commands.Cog.listener()
    async def on_command_completion(self, *args, **kwargs):
        if not self.initialized:
            await self.initialize()

    async def autoscale(self):
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
            await self.logChannel.send(
                f":arrows_clockwise: AutoScale:		Deleting empty channels. Now managing {before_channel_count - 1} channel(s).")

        # If no empty channel exists, create a new one
        if empty_channel is None:
            empty_channel = await template.clone(name="Voice Channel")
            await self.logChannel.send(
                f":arrows_clockwise: AutoScale:		New channel created. Now managing {before_channel_count + 1} channels.")

        # Make sure the empty channel is always last
        if self.category.voice_channels[-1] != empty_channel:
            await empty_channel.move(end=True)

    # Dynamic channel creation bot
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        print("hoi")
        if before.channel != after.channel:
            await self.autoscale()
        await self.on_member_update()
        # Make sure This is not an event within the same channel

    @staticmethod
    def get_most_played_game(voice_channel):
        games = {}
        for member in voice_channel.members:
            for activity in member.activities:
                if activity.type == discord.ActivityType.playing:
                    if activity.name not in games:
                        games[activity.name] = 1
                    else:
                        games[activity.name] += 1
        highest_hitcount = 0
        highest_name = "Voice Channel"
        for key, value in games.items():
            if value > highest_hitcount:
                highest_hitcount = value
                highest_name = key
        return highest_name

    @commands.Cog.listener()
    async def on_member_update(self, *args):
        for voice_channel in self.category.voice_channels:
            name = self.get_most_played_game(voice_channel)
            if voice_channel.name != name:
                await self.logChannel.send(
                    f":twisted_rightwards_arrows: AutoRename:	Changed {voice_channel.name} to {name}.")
                await voice_channel.edit(name=name)


def setup(client):
    client.add_cog(VoiceChannelBot(client))
