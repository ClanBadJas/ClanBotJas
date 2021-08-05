import json

#with open('menu.json') as json_file:
    #print(json.load(json_file))

import discord
import asyncio

import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID'))

def emoji_enumeration_generation():
    yield "1️⃣"
    yield "2️⃣"
    yield "3️⃣"
    yield "4️⃣"
    yield "5️⃣"
    yield "6️⃣"
    yield "7️⃣"
    yield "8️⃣"
    yield "9️⃣"
    yield "0️⃣"

class MyClient(discord.Client):
    guild = None
    menu = {}
    message_cache = {}
    
    '''This will create a conflict if you have multiple categories with the same name. 
    Fuck you.  
    Fix it yourself. 
    '''
    def create_category_map(self, channels):
        category_map = {}
        for channel in channels:
            if channel.type == discord.ChannelType.category:
                category_map[channel.name] = channel
        return category_map

    def create_role_map(self, roles):
        role_map = {}
        for role in roles:
            role_map[role.name] = role
        return role_map

    def create_text_channel_map(self, channels):
        text_channel_map = {}
        for channel in channels:
            if channel.type == discord.ChannelType.text:
                text_channel_map[channel.name] = channel
        return text_channel_map

    async def get_category(self,category_map, category_name):
        if category_name in category_map:
            return category_map[category_name]  
        else:
            return await self.guild.create_category_channel(category_name)

    async def get_role(self,role_map, role_name):
        if role_name in role_map:
            return role_map[role_name]  
        else:
            return await self.guild.create_role(name=role_name)
        
    async def get_text_channel(self,text_channel_map, text_channel_name, category, role):
        if text_channel_name in text_channel_map:
            return text_channel_map[text_channel_name]  
        else:
            overwrites = {
                self.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                role: discord.PermissionOverwrite(read_messages=True)
            }
            return await self.guild.create_text_channel(text_channel_name, category=category,overwrites=overwrites)
    async def create_channels(self,menujson,category_map,text_channel_map, role_map):
        generator = emoji_enumeration_generation()
        for category_json in menujson["categories"]:
            category = await self.get_category(category_map, category_json["title"])

            for text_channel_json in category_json["channels"]:
               role = await self.get_role(role_map, text_channel_json["role"])
               channel = await self.get_text_channel(text_channel_map, text_channel_json["title"], category, role)

               yield next(generator), role, text_channel_json["description"]

    async def get_message_from_title(self, channel, title):
        async for message in channel.history():

            if title in message.content:
                return message
            
        return await channel.send(content=title)

    async def on_ready(self):
        print('Connected!')
        self.guild = await self.fetch_guild(GUILD_ID)
        channel_cache = await self.guild.fetch_channels()

        category_map = self.create_category_map(channel_cache)
        text_channel_map = self.create_text_channel_map(channel_cache)
        role_map = self.create_role_map(await self.guild.fetch_roles())

        menujson = None
        with open('menu.json') as json_file:
            menujson = json.load(json_file)
        if menujson is None:
            return        

        channel = text_channel_map[menujson["channel_name"]]
        message = await self.get_message_from_title(channel,menujson["title"])
        self.message_cache[message.id] = message
        self.menu[message.id] = {}
        await message.clear_reactions()

        new_message_content = menujson["title"] + "\n"
        async for i, role, title in self.create_channels(menujson,category_map,text_channel_map,role_map):
            new_message_content += i + " " + title + "\n"
            self.menu[message.id][i] = role
            await message.add_reaction(i)

        await message.edit(content=new_message_content)


    async def on_raw_reaction_add(self, payload):
        message = self.message_cache[payload.message_id]
        if not message:
            return

        member = await self.guild.fetch_member(payload.user_id)
        if member == self.user:
            return
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
