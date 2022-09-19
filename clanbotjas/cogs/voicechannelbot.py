from email.policy import default
from typing import Union

import discord
from discord.ext import commands

from cogmanager import ClanBotjasClient


class VoiceChannelBot(commands.Cog):
    def __init__(self, client: ClanBotjasClient):
        self.client = client

    def get_voice_scalar_category(self, guild: discord.Guild) -> tuple[Union[discord.CategoryChannel, None], Union[str, None]]:
        guild_settings = self.client.guild_settings.get(guild.id)
        if guild_settings and guild_settings.voice_scalar_category:
            default_name = guild_settings.voice_scalar_default_name or "Voice channel"
            return guild_settings.voice_scalar_category, default_name
        else:
            return None, None

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Initialize the bot onready
        :return:
        """
        for guild_settings in self.client.guild_settings.values():
            category, default_name = self.get_voice_scalar_category(guild_settings.guild)

            if category:
                await self.autoscale(category, default_name)
                await self.sync_channel_names(category, default_name, set(category.voice_channels))
        await self.client.broadcast_log_message(':white_check_mark: Cog: "voicechannelbot" ready.')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member,
                                    before: discord.VoiceState,
                                    after: discord.VoiceState):
        """
        Autoscale the app when before and after channel are triggered.
        :param member: member that triggers the update
        :param before: before channel state
        :param after: after channel state
        :return:
        """
        voice_scalar_category, default_name = self.get_voice_scalar_category(member.guild)
        if not voice_scalar_category:
            return

        if before.channel != after.channel:
            await self.autoscale(voice_scalar_category, default_name)
        channels = set()
        if before and before.channel:
            channels.add(before.channel)
        if after and after.channel:
            channels.add(after.channel)

        await self.sync_channel_names(voice_scalar_category, default_name, set(channels))

    @commands.Cog.listener()
    async def on_presence_update(self, before: discord.Member, after: discord.Member):
        """
        check if the user is playing a different game.
        :return:
        """

        voice_scalar_category, default_name = self.get_voice_scalar_category(before.guild)
        if not voice_scalar_category:
            return
        
        channels = set()
        if before and before.voice and before.voice.channel:
            channels.add(before.voice.channel)
        if after and after.voice and after.voice.channel:
            channels.add(after.voice.channel)


        await self.sync_channel_names(voice_scalar_category, default_name, set(channels))

    async def sync_channel_names(self, category: discord.CategoryChannel,
                                 default_name: str, args: set[discord.VoiceChannel]):
        """
        Make sure all voice channels in the args have the correct voice channel names
        :return:
        """
        for voice_channel in args:
            if voice_channel.category != category:
                continue
            name = self.get_most_played_game(voice_channel) or default_name
            if voice_channel.name != name:
                await self.client.log_message(category.guild,
                                              f":twisted_rightwards_arrows: AutoRename:	"
                                              f"Changed {voice_channel.name} to {name}."
                                              )
                await voice_channel.edit(name=name)

    async def autoscale(self, category: discord.CategoryChannel, default_name: str):
        """
        Get all empty channels
        Delete empty channels if there is more than one
        If no empty channels exist, create one
        Manually create a channel if none exist
        :return:
        """
        voice_channels: list[discord.VoiceChannel] = category.voice_channels
        template: discord.VoiceChannel = voice_channels[-1] if voice_channels else None
        empty_channel: discord.VoiceChannel = None
        delete_channels: list[discord.VoiceChannel] = []

        # add empty voice channels to the delete list
        for voice_channel in voice_channels:
            if not voice_channel.members:
                if not empty_channel:
                    empty_channel = voice_channel
                else:
                    delete_channels.append(voice_channel)
        before_channel_count = len(category.voice_channels)
        # delete all empty channels, excluding the first empty channel
        for voice_channel in delete_channels:
            await voice_channel.delete()
        if delete_channels:
            delete_amount = len(delete_channels)
            await self.client.log_message(category.guild,
                ":arrows_clockwise: AutoScale:		"
                f"Deleting empty channels. Now managing {before_channel_count - delete_amount} channel(s)."
            )

        # If no empty channel exists, create a new one
        if empty_channel is None:
            if template:
                empty_channel = await template.clone(name=default_name)
            else:
                empty_channel = await category.create_voice_channel(name=default_name)
            await self.client.log_message(category.guild,
                f":arrows_clockwise: AutoScale:		New channel created. Now managing {before_channel_count + 1} channels."
            )

        # Make sure the empty channel is always last
        if category.voice_channels[-1] != empty_channel:
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
        highest_name = None
        for key, value in games.items():
            if value > highest_hitcount:
                highest_hitcount = value
                highest_name = key
        return highest_name


def setup(client):
    client.add_cog(VoiceChannelBot(client))
