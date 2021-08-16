import functools
from math import floor
import io

from discord_slash.utils.manage_components import create_select, create_select_option, create_actionrow, create_button

import discord
import numpy as np
from discord.ext import commands
from discord_components import Select, SelectOption, InteractionType
from discord_slash import SlashContext, cog_ext
from discord_slash.model import ButtonStyle
from matplotlib import pyplot as plt

import cogmanager
import settings

from discord_slash.utils.manage_commands import create_option, create_choice

options = [create_option(name="description", description="Poll description", option_type=3, required=True),
           create_option(name="max_values", description="Maximum amount of selected components", option_type=4,
                         required=True)]
for i in range(10):
    options.append(create_option(name=f"option{i}", description="option", option_type=3, required=False))

import threading

plotlock = threading.Lock()




def generate_image(height, bars):
    buf = io.BytesIO()
    y_pos = np.arange(len(bars))

    plotlock.acquire()
    fig, ax = plt.subplots()
    ax.barh(y_pos, height, align='center')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(bars)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel('Performance')
    ax.set_title('How fast do you want to go today?')
    plt.savefig(buf)
    plt.rcdefaults()

    plotlock.release()

    buf.seek(0)
    return buf


class PollEntry(object):
    def __init__(self, user, description, kwargs):
        self.description = description
        self.user = user
        self.user_options = {}
        self.bars = np.array(list(kwargs.values()))

    def update_user(self, user, values):
        self.user_options[user.id] = values

    def plot(self):
        height = np.zeros(len(self.bars), dtype=int)
        for indices in self.user_options.values():
            height[indices] += 1
        argsorted = np.argsort(height)[::-1]
        string_builder = [f"{self.bars[i]}: {height[i]}" for i in argsorted]
        return f"> {self.description}\n" + "\n".join(string_builder)
        #

    def results(self):
        height = np.zeros(len(self.bars), dtype=int)
        for indices in self.user_options.values():
            height[indices] += 1
        argsorted = np.argsort(height)[::-1]
        return discord.File(generate_image(height[argsorted], self.bars[argsorted]), filename="ctx.png")

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

        message = await ctx.send(content=entry.plot(), components=[entry.get_components(max_values),
                                                                   create_actionrow(
                                                                       create_button(style=ButtonStyle.grey,
                                                                                     label="plot results"))],
                                 hidden=False)
        self.poll_map[message.id] = entry

    @commands.Cog.listener()
    async def on_select_option(self, interaction):
        indices = np.array([int(component.value) for component in interaction.component])
        entry = self.poll_map[interaction.message.id]
        entry.update_user(interaction.author, indices)
        plot = entry.plot()
        await interaction.respond(type=InteractionType.UpdateMessage, content=plot)
        # await interaction.message.edit(file=entry.plot())

    @commands.Cog.listener()
    async def on_button_click(self, interaction):

        entry = self.poll_map[interaction.message.id]
        if entry.user != interaction.author:
            await interaction.respond("You did not create the poll")
            return

        components = interaction.message.components
        for interaction_row in components:
            for component in interaction_row:
                component.disabled = True

        await interaction.message.reply(content="resulting poll", file=entry.results())
        await interaction.respond(type=7, components=components)


def setup(client):
    client.add_cog(PollBot(client))
