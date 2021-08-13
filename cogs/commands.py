import json
from math import floor

import discord
from discord.ext import commands
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option

import cogmanager
import settings


class Commands(commands.Cog):

    def __init__(self, client):
        self.client = client
    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.get_channel(settings.LOG_CHANNEL).send("Command cog connected and ready")


    @staticmethod
    def has_role(member, role_id):
        for role in member.roles:
            if role.id == role_id:
                return True
        return False

    @commands.command()
    async def say(self, ctx):
        logChannel = self.client.get_channel(settings.LOG_CHANNEL)
        if not ctx.guild:
            await ctx.send("Commando only works in a guild")
            return
        if ctx.guild.id != settings.GUILD_ID:
            return
        if not ctx.author.guild_permissions.administrator:
            await ctx.send(f"{ctx.author.mention}, You do not have permissions to use that command.", hidden=True)
            return

        if isinstance(ctx.channel, discord.TextChannel):
            await logChannel.send(
                f":arrow_forward: Command:  {ctx.channel.mention} | {ctx.author.mention}: {ctx.message.content}", )
        else:
            await logChannel.send(f":arrow_forward: Command:  ???? | {ctx.author.mention}: {ctx.message.content}", )

        arg = ctx.message.content[4:].strip() if len(ctx.message.content) > 4 else ''
        if len(arg) == 0:
            await ctx.send(f"{ctx.author.mention}, Please provide a valid message!")
            return

        await ctx.send(ctx.message.content[5:])
        await ctx.message.delete()

    @cog_ext.cog_slash(name="ping",
                       description="send ping",
                       guild_ids=cogmanager.guild_ids,
                       permissions=cogmanager.permissions,
                       default_permission=False, )
    async def ping(self, ctx: SlashContext):
        msg = await ctx.send("Ping?")

        latency = msg.created_at - ctx.created_at
        await msg.edit(
            content=f"Pong! Latency is {floor(latency.total_seconds() * 1000)} ms. API Latency is {floor(ctx.bot.latency * 1000)} ms.")

    @cog_ext.cog_slash(name="getid",
                       description="get your user ID",
                       guild_ids=cogmanager.guild_ids)
    async def _getid(self, ctx: SlashContext,):
        await ctx.send(content=f"Your id is: {ctx.author.id}", hidden=True)


    @staticmethod
    def openMenu():
        try:
            f = open('menu.json', 'r')
        except IOError:
            return
        else:
            menu = json.load(f)
            f.close()
            return menu

    @staticmethod
    def syncMenu(menu):
        with open('menu.json', 'w', encoding='utf-8') as f:
            json.dump(menu, f, ensure_ascii=True, indent=4)

    @staticmethod
    def get_or_create_category(menu, category_name: str):
        for category in menu:
            if category["title"] == category_name:
                return category

        category = {"title": category_name, "channels": []}
        menu.append(category)
        return category

    @staticmethod
    def get_or_creat_text_channel(category, channel_name, role_name):
        for channel in category["channels"]:
            if channel["title"] == channel_name:
                return False

        category["channels"].append({"title": channel_name, "role": role_name})
        return True

    @cog_ext.cog_subcommand(base="rolebot", name="add",
                            guild_ids=cogmanager.guild_ids,
                            base_default_permission=False,
                            base_permissions=cogmanager.permissions,
                            options=[
                                create_option(name="category_name", description="#stuff", option_type=3, required=True),
                                create_option(name="channel_name", description="#stuff", option_type=3, required=True),
                                create_option(name="role_name", description="#stuff", option_type=3, required=False),
                            ])
    async def add(self, ctx: SlashContext, category_name, channel_name, role_name=None):
        if not role_name:
            role_name = channel_name
        menu = self.openMenu()
        category =self.get_or_create_category(menu, category_name)
        modified = self.get_or_creat_text_channel(category, channel_name, role_name)
        if modified:
            self.syncMenu(menu)
            await ctx.send(f"created \"{channel_name}\"", hidden=True)
        else:
            await ctx.send(f"\"{channel_name}\" already exists", hidden=True)



    @cog_ext.cog_subcommand(base="rolebot", name="delete",
                            guild_ids=cogmanager.guild_ids,
                            base_default_permission=False,
                            base_permissions=cogmanager.permissions,
                            options=[
                                create_option(name="channel_name", description="#stuff", option_type=3, required=True)
                            ])
    async def delete(self, ctx: SlashContext, channel_name):
        modified = False
        menu = self.openMenu()

        for category in menu:
            channels = list(filter(lambda channel: channel['title'] != channel_name, category["channels"]))
            if len(channels) != len(category["channels"]):
                modified = True
                category["channels"] = channels

        if modified:
            self.syncMenu(menu)
            await ctx.send(f"deleted \"{channel_name}\"", hidden=True)
        else:
            await ctx.send(f"Could not find \"{channel_name}\"", hidden=True)

    @cog_ext.cog_subcommand(base="rolebot", name="show",
                            guild_ids=cogmanager.guild_ids,
                            base_default_permission=False,
                            base_permissions=cogmanager.permissions,)
    async def show(self, ctx: SlashContext):
        pretty_json = json.dumps(self.openMenu(), indent=4)
        await ctx.send(f"```{pretty_json}```", hidden=True)

def setup(client):
    client.add_cog(Commands(client))
