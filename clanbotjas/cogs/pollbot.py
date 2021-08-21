import functools
import io

from PIL import Image, ImageDraw
from discord_slash.utils.manage_components import create_select, create_select_option, create_actionrow, create_button

import discord
import numpy as np
from discord.ext import commands
from discord_components import InteractionType
from discord_slash import SlashContext, cog_ext
from discord_slash.model import ButtonStyle

import cogmanager
import settings

from discord_slash.utils.manage_commands import create_option

options = [create_option(name="description", description="Poll description", option_type=3, required=True),
           create_option(name="max_values", description="Maximum amount of selected components", option_type=4,
                         required=True)]
for i in range(10):
    options.append(create_option(name=f"option{i}", description="option", option_type=3, required=False))

import threading

plotlock = threading.Lock()


def create_poll_image(heights, bars):
    bitmap = np.tile(settings.DISCORD_POLL_EMPTY, (heights.size, 1, 1))
    bar_height, bar_width, _ = settings.DISCORD_POLL_EMPTY.shape
    max = np.max(heights)

    for i, height in enumerate(heights):
        width = height * bar_width // 100
        bar = settings.DISCORD_POLL_WIN if height == max else settings.DISCORD_POLL_FULL
        bitmap[i * bar_height:(i + 1) * bar_height, :width] = bar[:, :width]

    image = Image.fromarray(bitmap)
    draw = ImageDraw.Draw(image)
    for i, height in enumerate(heights):
        if height == max:
            font, bar_y = settings.DISCORD_TTF_POLL_BOLD, bar_height // 2 + i * bar_height + 13
        else:
            font, bar_y = settings.DISCORD_TTF_POLL_NORMAL, bar_height // 2 + i * bar_height
        lbound, rbound = 25 * settings.DISCORD_TTF_SCALE_FACTOR, bar_width - 25 * settings.DISCORD_TTF_SCALE_FACTOR
        draw.text((lbound, bar_y), f"{bars[i]}", fill="white", anchor="lm", font=font)
        draw.text((rbound, bar_y), f"{height}%", fill="white", anchor="rm", font=font)
    return image


class PollEntry(object):
    def __init__(self, user, description, kwargs):
        self.description = description
        self.user = user
        self.user_options = {}
        self.bars = np.array(list(kwargs.values()))

    def update_user(self, user, values):
        self.user_options[user.id] = values

    def names(self):
        return "\n".join(self.bars)

    def values(self):
        height = np.zeros(len(self.bars), dtype=int)
        for indices in self.user_options.values():
            height[indices] += 1
        return"\n".join([str(i) for i in height])

    def create_embed(self):
        embed = discord.Embed(title=self.description)
        embed.set_author(name=self.user.name, icon_url=self.user.avatar_url)
        embed.add_field(name="Option", value=self.names(), inline=True)
        embed.add_field(name="Votes", value=self.values(), inline=True)
        return embed

    def results(self):
        height = np.zeros(len(self.bars), dtype=int)
        for indices in self.user_options.values():
            height[indices] += 1
        # height = height * 100 // len(self.user_options)
        height = height * 100 // np.sum(height)

        buf = io.BytesIO()
        image = create_poll_image(height, self.bars)
        image.save(buf, format='PNG')
        buf.seek(0)

        return discord.File(buf, filename="pollresult.png")

    def get_components(self, max_values):
        options = [create_select_option(label=name, value=str(i)) for i, name in enumerate(self.bars)]
        return create_actionrow(
            create_select(placeholder=f"select up to {max_values} values", max_values=max_values, options=options))


def slashcommandlogger(func):
    @functools.wraps(func)
    async def wrapped(self, ctx, *args, **kwargs):
        # Some fancy foo stuff
        await func(self, ctx, *args, **kwargs)
        logChannel = self.client.get_channel(settings.DISCORD_LOG_CHANNEL)
        await cogmanager.logCommand(logChannel, ctx, **kwargs)

    return wrapped


class PollBot(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.poll_map = {}

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.get_channel(settings.DISCORD_LOG_CHANNEL).send(":white_check_mark: Cog: \"pollbot\" ready.")

    @cog_ext.cog_slash(name="createpoll", description="Create a poll",
                       guild_ids=settings.DISCORD_GUILD_IDS, options=options)
    async def _createpoll(self, ctx: SlashContext, description, max_values, **kwargs):
        entry = PollEntry(ctx.author, description, kwargs)
        message = await ctx.send(embed=entry.create_embed(), components=[entry.get_components(max_values), create_actionrow(create_button(style=ButtonStyle.grey, label="plot results"))],hidden=False)
        # message = await ctx.send(content=entry.plot(),
        self.poll_map[message.id] = entry

    @commands.Cog.listener()
    async def on_select_option(self, interaction):
        indices = np.array([int(component.value) for component in interaction.component])
        entry = self.poll_map[interaction.message.id]
        entry.update_user(interaction.author, indices)

        await interaction.respond(type=InteractionType.UpdateMessage, embed=entry.create_embed())
        # await interaction.message.edit(file=entry.plot())

    @commands.Cog.listener()
    async def on_button_click(self, interaction):
        if interaction.message.id not in self.poll_map:
            return

        entry = self.poll_map[interaction.message.id]
        if entry.user != interaction.author:
            await interaction.respond("You did not create the poll")
            return

        components = interaction.message.components
        for interaction_row in components:
            for component in interaction_row:
                component.disabled = True
        file = entry.results()
        await interaction.message.reply(content="resulting poll", file=file)
        await interaction.respond(type=7, components=components)


def setup(client):
    client.add_cog(PollBot(client))
