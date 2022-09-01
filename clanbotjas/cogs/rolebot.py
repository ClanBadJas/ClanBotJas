import json
import yaml

import discord

from discord import option, Permissions
from discord.ext import commands
from discord.commands import SlashCommandGroup
from discord.commands.options import OptionChoice

import settings
from cogs.commands import slashcommandlogger


class RoleButton(discord.ui.Button):
    def __init__(self, 
                 guild : discord.Guild, 
                 role : discord.Role,
                 channel_name : str):
        super().__init__(label=role.name)
        self.guild = guild
        self.role = role
        self.channel_name = channel_name

    async def callback(self, interaction: discord.Interaction):
        pass
        # Toggle the role on the member
        member = await self.guild.fetch_member(interaction.user.id)
        if self.role in member.roles:
            await member.remove_roles(self.role)
            message = f"{self.channel_name} is now invisible."
        else:
            await member.add_roles(self.role)
            message = f"{self.channel_name} is now visible."
        await interaction.response.send_message(content=message, ephemeral=True)


class RoleBot(commands.Cog):
    guild = None
    menu = {}
    role_map = {}
    category_map = {}
    text_channel_map = {}
    log_channel = None
    menujson = None

    def __init__(self, client):
        self.client = client

    rolebot = SlashCommandGroup("rolebot", "Rolebot related commands")

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Create all settings messages with the buttons attached.
        :return:
        """
        self.log_channel = self.client.get_channel(settings.DISCORD_LOG_CHANNEL)
        self.guild = await self.client.fetch_guild(settings.DISCORD_GUILD_ID)
        channel_cache = await self.guild.fetch_channels()

        # Create maps
        await self.init_category_map(channel_cache)
        await self.init_text_channel_map(channel_cache)
        await self.init_role_map()

        self.menujson = self.open_menu()
        if not self.menujson:
            await self.log_channel.send("Discord button cog failed: Couldn't read menu.json.")
            return
        # create text settings text messages.
        for menu in self.menujson:
            await self.create_rolebot_messages(menu)

        await self.log_channel.send(":white_check_mark: Cog: \"rolebot\" ready.")

    @staticmethod
    def open_menu():
        """
        Open the menu file that represent the roles
        :return:
        """
        try:
            f = open('data/menu.json', 'r')
        except IOError:
            return None
        else:
            menu = json.load(f)
            f.close()
            return menu

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

    async def get_or_create_category(self, category_name):
        """
        Get a category by name
        :param category_name: category name
        :return:
        """
        if category_name in self.category_map:
            return self.category_map[category_name]
        else:
            return await self.guild.create_category_channel(category_name)

    async def get_or_create_role(self, role_name):
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

        category = await self.get_or_create_category(menujson["title"])

        for text_channel_json in menujson["channels"]:
            role = await self.get_or_create_role(text_channel_json["role"])
            await self.get_or_create_text_channel(text_channel_json["title"], category, role)

            yield role, "#" + text_channel_json["title"]

    async def create_rolebot_messages(self, menujson):
        """
        Create the message and post it in the configured settings channel
        :param menujson: The config file
        :return:
        """
        view = discord.ui.View()
        channel = self.client.get_channel(settings.DISCORD_ROLEBOT_SETTINGS_CHANNEL)
        title = f"** {menujson['title']} **"

        # Create all of the button components
        async for role, channel_name in self.create_channels(menujson):
            view.add_item(RoleButton(self.guild, role, channel_name))
        
        # Replace an existing message
        async for message in channel.history():
            if title in message.content:
                await message.edit(content=title, view=view)
                return
        # Create a new message
        await channel.send(content=title, view=view)

    '''
    SECTION:
    All rolebot related commands
    '''

    @staticmethod
    def sync_menu(menu):
        """
        Write the menu to the menu.json file
        :param menu:
        :return:
        """
        with open('data/menu.json', 'w', encoding='utf-8') as f:
            json.dump(menu, f, ensure_ascii=True, indent=4)

    @staticmethod
    def get_or_create_category_menu(menu, category_name: str):
        """
        In the menu.json create or retrieve the category
        :param menu: original menu.json
        :param category_name: name of the category
        :return:
        """
        for category in menu:
            if category["title"] == category_name:
                return category

        category = {"title": category_name, "channels": []}
        menu.append(category)
        return category

    @staticmethod
    def get_or_create_text_channel_menu(category, channel_name, role_name):
        """
        Create a channel in the category, return success status
        :param category: category containing channels
        :param channel_name: name of the channel
        :param role_name: name of the rol
        :return:  True if Channel exists, False if channel was created
        """
        for channel in category["channels"]:
            if channel["title"] == channel_name:
                return False

        category["channels"].append({"title": channel_name, "role": role_name})
        return True

    @rolebot.command( name="add",
                      description="Add channel to role bot",
                      guild_ids=settings.DISCORD_GUILD_IDS,
                      default_permission=False)
    @commands.has_role(settings.DISCORD_COMMAND_PERMISSION_ROLE)
    @option("category_name", description="#stuff", required=True)
    @option("channel_name", description="#stuff", required=True)
    @option("role_name", description="#stuff", required=False)
    @slashcommandlogger
    async def rolebot_add(self, ctx: discord.ApplicationContext, category_name : str, channel_name : str, role_name : str):
        """
        Command for adding a new channel to the rolebot
        :param ctx: slash command context
        :param category_name: name of the category
        :param channel_name: name of the channel
        :param role_name: name of the role
        :return:
        """
        role_name = role_name if role_name else channel_name
        menu = self.open_menu()
        category = self.get_or_create_category_menu(menu, category_name)
        modified = self.get_or_create_text_channel_menu(category, channel_name, role_name)
        if modified:
            self.sync_menu(menu)
            await ctx.respond(f"created \"{channel_name}\".")
        else:
            await ctx.respond(f"\"{channel_name}\" already exists.")

    @rolebot.command( name="delete",
                      description="delete channel from role bot",
                      guild_ids=settings.DISCORD_GUILD_IDS,
                      default_permission=False)
    @commands.has_role(settings.DISCORD_COMMAND_PERMISSION_ROLE)
    @option("channel_name", description="#stuff", required=True)
    @slashcommandlogger
    async def rolebot_delete(self, ctx: discord.ApplicationContext, channel_name : str):
        """
        Command for deleting a channel from the rolebot
        :param ctx:
        :param channel_name:
        :return:
        """
        modified = False
        menu = self.open_menu()

        for category in menu:
            channels = list(filter(lambda channel: channel['title'] != channel_name, category["channels"]))
            if len(channels) != len(category["channels"]):
                modified = True
                category["channels"] = channels

        if modified:
            self.sync_menu(menu)
            await ctx.respond(f"deleted \"{channel_name}\".", ephemeral=True)
        else:
            await ctx.respond(f"Could not find \"{channel_name}\".", ephemeral=True)

    @rolebot.command( name="show",
                      description="show rolebot static/running config",
                      guild_ids=settings.DISCORD_GUILD_IDS,
                      default_permission=False)
    @commands.has_role(settings.DISCORD_COMMAND_PERMISSION_ROLE)
    @option(name="config_type", 
            description="Type of config", 
            required=False,
            choices=[ "running", "static" ],
            default="static",
    ) 
    @slashcommandlogger
    async def rolebot_show(self, ctx: discord.ApplicationContext, config_type: str):
        """
        Show the running/static config in yaml format (More compact than JSON)
        :param ctx: original commoand context
        :param config_type: static/running config
        :return:
        """
        menu = None
        if config_type == "running":
            menu = self.menujson
        elif config_type == "static":
            menu = self.open_menu()

        if menu:
            await ctx.respond(f"```{yaml.dump(menu)}```")
        else:
            message = f"{config_type} is an incorrect type"
            await ctx.respond(message, ephemeral=True)
            assert False, message
            


def setup(client):
    client.add_cog(RoleBot(client))
