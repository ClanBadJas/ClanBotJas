import os

import discord
import asyncio

#from dotenv import load_dotenv

#load_dotenv()
#TOKEN = os.getenv('TOKEN')
#VOICE_CATEGORY_ID = int(os.getenv('VOICE_CATEGORY_ID'))
TOKEN = 'NzUwNDE3OTc1Mjc3OTEyMjI2.X06PMw.TwRCt-SWtvR4mQ_UEYX4Tq8q-DY'
VOICE_CATEGORY_ID =871320283531845694
MY_MEMBER_ID = 175592764149334016

class MyClient(discord.Client):
    async def on_ready(self):
            print('Ready!')
    # Dynamic channel creation bot
    async def on_voice_state_update(self, member,before, after):
        print("hoi")
        print(member)

        if member.id == MY_MEMBER_ID:
            print("Muted", member.voice.self_mute or member.voice.mute)
            print("Deafened", member.voice.self_deaf or member.voice.deaf)
            print("Streaming", member.voice.self_stream)
        # Make sure This is not an event within the same channel
      #  if before.channel == after.channel:
      #      print("no op")
      #      return
        
        # Delete a channel if it's empty
      #  if before.channel and before.channel.category_id== VOICE_CATEGORY_ID:
      #      print("case 1")
      #      if len(before.channel.members) == 0:
      #          print("deleting chhannel")
      #          await before.channel.delete()
      #  # Duplicate channel for other users
      #  if after.channel and after.channel.category_id== VOICE_CATEGORY_ID:
      #      print("case 2")
      #      if len(after.channel.members) == 1:
      #          await after.channel.clone()
      #      # Change the channel name to the current user is playing
      #      if member.activity and member.activity.type == discord.ActivityType.playing:
      #          await after.channel.edit(name=member.activity.name)

client = MyClient()

client.run(TOKEN)
