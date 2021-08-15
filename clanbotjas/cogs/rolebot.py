import json

import discord
from discord.ext import commands
from discord_components import Button
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice

import settings


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
            await self.log_channel.send("Discord button cog failed: Couldn't read menu.json")
            return
        # create text settings text messages.
        for menu in self.menujson:
            await self.create_rolebot_messages(menu)

        await self.log_channel.send("Discord button cog ready")

    @commands.Cog.listener()
    async def on_button_click(self, interaction):
        role_id = int(interaction.component.custom_id)
        member = await self.guild.fetch_member(interaction.user.id)
        role, channel_name = self.menu[role_id]
        if role in member.roles:
            await member.remove_roles(role)
            await interaction.respond(content=f"{channel_name} is onzichtbaar")
        else:
            await member.add_roles(role)
            await interaction.respond(content=f"{channel_name} is zichtbaar")

    @staticmethod
    def open_menu():
        try:
            f = open('settings/menu.json', 'r')
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
        buttons = [[]]

        channel = self.client.get_channel(settings.DISCORD_ROLEBOT_SETTINGS_CHANNEL)
        title = f"** {menujson['title']} **"

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

    '''
    SECTION:
    All rolebot related commands
    '''

    @staticmethod
    def sync_menu(menu):
        with open('settings/menu.json', 'w', encoding='utf-8') as f:
            json.dump(menu, f, ensure_ascii=True, indent=4)

    @staticmethod
    def get_or_create_category_menu(menu, category_name: str):
        for category in menu:
            if category["title"] == category_name:
                return category

        category = {"title": category_name, "channels": []}
        menu.append(category)
        return category

    @staticmethod
    def get_or_create_text_channel_menu(category, channel_name, role_name):
        for channel in category["channels"]:
            if channel["title"] == channel_name:
                return False

        category["channels"].append({"title": channel_name, "role": role_name})
        return True

    @cog_ext.cog_subcommand(base="rolebot", name="add",
                            description="Add channel to role bot",
                            guild_ids=settings.DISCORD_GUILD_IDS,
                            base_default_permission=False,
                            base_permissions=settings.DISCORD_COMMAND_PERMISSIONS,
                            options=[
                                create_option(name="category_name", description="#stuff", option_type=3, required=True),
                                create_option(name="channel_name", description="#stuff", option_type=3, required=True),
                                create_option(name="role_name", description="#stuff", option_type=3, required=False),
                            ])
    async def rolebot_add(self, ctx: SlashContext, category_name, channel_name, role_name=None):
        if not role_name:
            role_name = channel_name
        menu = self.open_menu()
        category = self.get_or_create_category_menu(menu, category_name)
        modified = self.get_or_create_text_channel_menu(category, channel_name, role_name)
        if modified:
            self.sync_menu(menu)
            await ctx.send(f"created \"{channel_name}\"", hidden=True)
        else:
            await ctx.send(f"\"{channel_name}\" already exists", hidden=True)

    @cog_ext.cog_subcommand(base="rolebot", name="delete",
                            description="delete channel from role bot",
                            guild_ids=settings.DISCORD_GUILD_IDS,
                            base_default_permission=False,
                            base_permissions=settings.DISCORD_COMMAND_PERMISSIONS,
                            options=[
                                create_option(name="channel_name", description="#stuff", option_type=3, required=True)
                            ])
    async def rolebot_delete(self, ctx: SlashContext, channel_name):
        modified = False
        menu = self.open_menu()

        for category in menu:
            channels = list(filter(lambda channel: channel['title'] != channel_name, category["channels"]))
            if len(channels) != len(category["channels"]):
                modified = True
                category["channels"] = channels

        if modified:
            self.sync_menu(menu)
            await ctx.send(f"deleted \"{channel_name}\"", hidden=True)
        else:
            await ctx.send(f"Could not find \"{channel_name}\"", hidden=True)

    @cog_ext.cog_subcommand(base="rolebot", name="show",
                            description="show rolebot static/running config",
                            guild_ids=settings.DISCORD_GUILD_IDS,
                            base_default_permission=False,
                            base_permissions=settings.DISCORD_COMMAND_PERMISSIONS,
                            options=[
                                create_option(name="config_type", description="Type of config", option_type=3,
                                              required=False,
                                              choices=[
                                                  create_choice(name="running", value="running"),
                                                  create_choice(name="static", value="static"),
                                              ])
                            ])
    async def rolebot_show(self, ctx: SlashContext, config_type: str = "static"):
        menu = None
        if config_type == "running":
            menu = self.menujson
        if config_type == "static":
            menu = self.open_menu()

        if menu:
            pretty_json = json.dumps(menu, indent=4)
            await ctx.send(f"```{pretty_json}```", hidden=True)
        else:
            await ctx.send("Incorrect type", hidden=True)


def setup(client):
    client.add_cog(RoleBot(client))
