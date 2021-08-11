import os

import discord
import asyncio
from basediscordbot import BaseDiscordBot
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')
VOICE_CATEGORY_ID = 873269868508635168


class MyClient(BaseDiscordBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category = None

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

        # delete all empty channels, excluding the first empty channel
        for voice_channel in delete_channels:
            await voice_channel.delete()
            await self.log(f":arrows_clockwise: AutoScale:		Deleting empty channels. Now managing {len(self.category.voice_channels)} channel(s).")

        # If no empty channel exists, create a new one
        if empty_channel is None:
            empty_channel = await template.clone(name="Voice Channel")
            await self.log(f":arrows_clockwise: AutoScale:		New channel created. Now managing {len(self.category.voice_channels)} channels.")

        # Make sure the empty channel is always last
        if self.category.voice_channels[-1] != empty_channel:
            await empty_channel.move(end=True)

    async def on_ready(self):
        await super().on_ready()
        print('connected')
        self.category = self.get_channel(VOICE_CATEGORY_ID)
        await self.autoscale()
        print('Ready!')

    # Dynamic channel creation bot
    async def on_voice_state_update(self, member, before, after):
        print("hoi")
        if before.channel != after.channel:
            await self.autoscale()
        await self.on_member_update()
        # Make sure This is not an event within the same channel

    def get_most_played_game(self, voice_channel):
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
    async def on_member_update(self, *args):
        for voice_channel in self.category.voice_channels:
            name = self.get_most_played_game(voice_channel)
            if voice_channel.name != name:
                await self.log(f":twisted_rightwards_arrows: AutoRename:	Changed {voice_channel.name} to {name}.")
                await voice_channel.edit(name=name)
                await MyClient.on_ready(self)



if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.presences = True
    intents.members = True
    client = MyClient(intents=intents)
    client.run(TOKEN)
