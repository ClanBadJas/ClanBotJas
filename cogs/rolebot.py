import json
import os

import discord
from discord.ext import commands
from discord_components import Button

import settings


class RoleBot(commands.Cog):
    guild = None
    menu = {}
    role_map = {}
    category_map = {}
    text_channel_map = {}
    log_channel = None

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Create all settings messages with the buttons attached.
        :return:
        """
        self.log_channel = self.client.get_channel(settings.LOG_CHANNEL)
        await self.log_channel.send("Discord button cog connected")
        self.guild = await self.client.fetch_guild(settings.GUILD_ID)
        channel_cache = await self.guild.fetch_channels()

        # Create maps
        await self.init_category_map(channel_cache)
        await self.init_text_channel_map(channel_cache)
        await self.init_role_map()

        try:
            f = open('menu.json', 'r')
        except IOError:
            return
        else:
            # create text settings text messages.
            for menujson in json.load(f):
                await self.get_message_from_title(menujson)
            f.close()
        await self.log_channel.send("Discord button cog ready")

    @commands.Cog.listener()
    async def on_button_click(self, interaction):
        await self.toggle_role(interaction, int(interaction.component.custom_id))

    async def init_category_map(self, channels):
        """
        Create a dictionary that maps the names of categories to the corresponding objects.
        :param channels: all channels
        :return:
        """
        for channel in channels:
            if channel.type == discord.ChannelType.category:
                self.category_map[channel.name] = channel

    async def init_role_map(self):
        """
        Create a dictionary that maps the names of roles to the corresponding objects.
        :return:
        """
        roles = await self.guild.fetch_roles()
        for role in roles:
            self.role_map[role.name] = role

    async def init_text_channel_map(self, channels):
        """
        Create a dictionary that maps the names of text channels to the corresponding objects.
        :param channels: channels
        :return:
        """
        for channel in channels:
            if channel.type == discord.ChannelType.text:
                self.text_channel_map[channel.name] = channel

    async def get_category(self, category_name):
        """
        Get a category by name
        :param category_name: category name
        :return:
        """
        if category_name in self.category_map:
            return self.category_map[category_name]
        else:
            return await self.guild.create_category_channel(category_name)

    async def get_role(self, role_name):
        """
        Get a role by name
        :param role_name: role name
        :return:
        """
        if role_name in self.role_map:
            return self.role_map[role_name]
        else:
            return await self.guild.create_role(name=role_name)

    async def get_or_create_text_channel(self, text_channel_name, category, role):
        """
        Function that returns the text channel by name if it exists.
        Otherwise, it gets created in the category and can only be viewed with the given role.

        :param text_channel_name: The name of the text channel te be created
        :param category: The category the channel will be posted in.
        :param role: The role required to view the channel
        :return:
        """
        if text_channel_name in self.text_channel_map:
            return self.text_channel_map[text_channel_name]
        else:
            overwrites = {
                self.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                role: discord.PermissionOverwrite(read_messages=True)
            }
            return await self.guild.create_text_channel(text_channel_name, category=category, overwrites=overwrites)

    async def create_channels(self, menujson):
        """
        Synchronize the menujson file with the discord channels.
        yield the role and channel name.

        :param menujson: Menu json
        :return:
        """

        category = await self.get_category(menujson["title"])

        for text_channel_json in menujson["channels"]:
            role = await self.get_role(text_channel_json["role"])
            await self.get_or_create_text_channel(text_channel_json["title"], category, role)

            yield role, "#" + text_channel_json["title"]

    async def get_message_from_title(self, menujson):
        """
        Create the message and post it in the configured settings channel
        :param menujson: The config file
        :return:
        """
        buttons = [[]]

        channel = self.client.get_channel(settings.DISCORD_ROLEBOT_SETTINGS_CHANNEL)
        title = "> " + menujson["title"]

        async for role, channel_name in self.create_channels(menujson):
            if len(buttons[-1]) > 4:
                buttons.append([])

            self.menu[role.id] = (role, channel_name,)
            buttons[-1].append(Button(label=channel_name, custom_id=role.id))

        if len(buttons[0]) == 0:
            buttons = []

        async for message in channel.history():
            if title in message.content:
                await message.edit(content=title, components=buttons)
                return

        await channel.send(content=title, components=buttons)

    async def toggle_role(self, interaction, role_id):
        """
        Toggle the role on the user and give feedback
        :param interaction: The button that was clicked
        :param role_id: ID of the toggled role
        :return:
        """
        member = await self.guild.fetch_member(interaction.user.id)
        role = self.menu[role_id][0]
        channel_name = self.menu[role_id][1]
        if role in member.roles:
            await member.remove_roles(role)
            await interaction.respond(content=f"{channel_name} is onzichtbaar")
        else:
            await member.add_roles(role)
            await interaction.respond(content=f"{channel_name} is zichtbaar")


def setup(client):
    client.add_cog(RoleBot(client))
