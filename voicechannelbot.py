import os

import discord
import asyncio

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')
VOICE_CATEGORY_ID = 873269868508635168
class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category = None

    async def create_delete_channels(self):
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

        # If no empty channel exists, create a new one
        if empty_channel is None:
            empty_channel = await template.clone(name="Voice Channel")

        # Make sure the empty channel is always last
        if self.category.voice_channels[-1] != empty_channel:
            await empty_channel.move(end=True)

    async def on_ready(self):
        print('connected')
        self.category = self.get_channel(VOICE_CATEGORY_ID)
        await self.create_delete_channels()
        print('Ready!')

    # Dynamic channel creation bot
    async def on_voice_state_update(self, member, before, after):
        print("hoi")
        if before.channel != after.channel:
            await self.create_delete_channels()
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
                await voice_channel.edit(name=name)


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.presences = True
    intents.members = True
    client = MyClient(intents=intents)
    client.run(TOKEN)
