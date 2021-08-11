
import discord

from discord_components import DiscordComponents, Button
import os
import json
from dotenv import load_dotenv
from basediscordbot import BaseDiscordBot

load_dotenv()
TOKEN = os.getenv('TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID'))


class MyClient(BaseDiscordBot):
    guild = None
    menu = {}
    role_map = {}
    category_map = {}
    text_channel_map = {}
    
    '''This will create a conflict if you have multiple categories with the same name. 
    '''
    async def init_category_map(self, channels):
        for channel in channels:
            if channel.type == discord.ChannelType.category:
                self.category_map[channel.name] = channel

    async def init_role_map(self):
        roles = await self.guild.fetch_roles()
        for role in roles:
            self.role_map[role.name] = role

    async def init_text_channel_map(self, channels):
        for channel in channels:
            if channel.type == discord.ChannelType.text:
                self.text_channel_map[channel.name] = channel

    async def get_category(self, category_name):
        if category_name in self.category_map:
            return self.category_map[category_name]  
        else:
            return await self.guild.create_category_channel(category_name)

    async def get_role(self, role_name):
        if role_name in self.role_map:
            return self.role_map[role_name]  
        else:
            return await self.guild.create_role(name=role_name)
        
    async def get_text_channel(self, text_channel_name, category, role):
        if text_channel_name in self.text_channel_map:
            return self.text_channel_map[text_channel_name]  
        else:
            overwrites = {
                self.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                role: discord.PermissionOverwrite(read_messages=True)
            }
            return await self.guild.create_text_channel(text_channel_name, category=category,overwrites=overwrites)

    async def create_channels(self,menujson):
        for category_json in menujson["categories"]:
            category = await self.get_category(category_json["title"])

            for text_channel_json in category_json["channels"]:
               role = await self.get_role(text_channel_json["role"])
               await self.get_text_channel(text_channel_json["title"], category, role)

               yield role, "#" + text_channel_json["title"]

    async def get_message_from_title(self, channel, menujson):
        buttons = []
        i = 0
        new_message_content = menujson["title"] + "\n"
        async for role, channel_name in self.create_channels(menujson):
            if i % 5 == 0:
                buttons.append([])

            self.menu[role.id] = (role,channel_name,)
            buttons[i//5].append(Button(label=channel_name, custom_id=role.id))
            i+=1

        async for message in channel.history():
            if menujson["title"] in message.content:
                await message.edit(content=new_message_content, components=buttons)
                return
            
        await channel.send(content=menujson["title"], components=buttons)

    async def on_ready(self):
        await super().on_ready()
        await self.log("Discord button bot is connected")
        self.guild = await self.fetch_guild(GUILD_ID)
        channel_cache = await self.guild.fetch_channels()

        await self.init_category_map(channel_cache)
        await self.init_text_channel_map(channel_cache)
        await self.init_role_map()

        try: 
            f = open('menu.json', 'r')
        except IOError:
            return 
        else:
            for menujson in json.load(f):
                channel = self.text_channel_map[menujson["channel_name"]]
                await self.get_message_from_title(channel, menujson)
            f.close()
        await self.log("Discord button bot is ready")

    async def on_button_click(self, interaction):
        await self.toggle_role(interaction,  int(interaction.component.custom_id))

    async def toggle_role(self, interaction, role_id):
        member = await self.guild.fetch_member(interaction.user.id)
        role = self.menu[role_id][0]
        channel_name = self.menu[role_id][1]
        if role in member.roles:
            await member.remove_roles(role)
            await interaction.respond(content=f"{channel_name} is onzichtbaar")
        else:
            await member.add_roles(role)
            await interaction.respond(content=f"{channel_name} is zichtbaar")



if __name__ == "__main__":
    client = MyClient()
    DiscordComponents(client)
    client.run(TOKEN)
