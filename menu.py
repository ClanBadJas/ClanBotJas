import json

with open('menu.json') as json_file:
    print(json.load(json_file))

import discord
import asyncio

import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID'))

class MyClient(discord.Client):
    guild = None
    menu = {}
    message_cache = {}
    async def on_ready(self):
        print('Connected!')
        self.guild = await self.fetch_guild(GUILD_ID)


        menujson = None

        with open('menu.json') as json_file:
            menujson = json.load(json_file)
        if menujson is None:
            return

        print(menujson["channel_id"])
        channel = self.get_channel(751831081795190955)
        #channel = guild.get_channel(menujson["channel_id"])
        message_object = await channel.fetch_message(menujson['message_id'])
        self.menu[menujson["message_id"]] = {}

        message = "> " + menujson["title"]
        for menu_item in menujson["content"]:
            self.menu[menujson["message_id"]][menu_item["emoji"]] = self.guild.get_role(menu_item["role"])
            message = message + "\n" + menu_item["emoji"] + " " + menu_item["title"]
            print(menu_item["emoji"])
            await message_object.add_reaction(menu_item["emoji"])
        await message_object.edit(content=message)
        self.message_cache[message_object.id] = message_object
        
      #  for emoji in self.menu[menujson["message_id"]]:
      #      print(emoji)



        print(self.menu)
#        print(self.guilds)
#        print('Username: {0.name}\nID: {0.id}'.format(self.user))

    async def on_raw_reaction_add(self, payload):
            message = self.message_cache[payload.message_id]
            if not message:
                return
            
            member = await self.guild.fetch_member(payload.user_id)
            #member = self.guild.get_member(payload.user_id)
            emoji = payload.emoji
            
            remove_reaction = message.remove_reaction(emoji,member)
            role = self.menu[payload.message_id][emoji.name]
            if role in member.roles:
                await member.remove_roles(role)
            else:
                await member.add_roles(role)

            await remove_reaction
             


client = MyClient()

client.run(TOKEN)
