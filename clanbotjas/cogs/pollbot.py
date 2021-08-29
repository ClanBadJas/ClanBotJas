import functools
import io
from enum import Enum

import discord
import numpy as np
from PIL import Image, ImageDraw
from discord_slash.utils.manage_components import create_select, create_select_option, create_actionrow, create_button
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash import SlashContext, cog_ext
from discord_slash.model import ButtonStyle
from discord.ext import commands
from discord_components import InteractionType
import discord_components

import cogmanager
import settings


class PercentageMode:
    CUMULATIVE = 0
    RESPONDENT = 1


poll_options = [create_option(name="description", description="Poll description", option_type=3, required=True),
                create_option(name="max_values", description="Maximum options the voter can select", option_type=4,
                              required=False),
                create_option(name="percentage_mode", description="Percentage calculation mode", option_type=4,
                              required=False,
                              choices=[create_choice(name="cumulative", value=PercentageMode.CUMULATIVE),
                                       create_choice(name="respondent", value=PercentageMode.RESPONDENT)]),
                create_option(name=f"option0", description="option", option_type=3, required=False),
                create_option(name=f"option1", description="option", option_type=3, required=False),
                create_option(name=f"option2", description="option", option_type=3, required=False),
                create_option(name=f"option3", description="option", option_type=3, required=False),
                create_option(name=f"option4", description="option", option_type=3, required=False),
                create_option(name=f"option5", description="option", option_type=3, required=False),
                create_option(name=f"option6", description="option", option_type=3, required=False),
                create_option(name=f"option7", description="option", option_type=3, required=False),
                create_option(name=f"option8", description="option", option_type=3, required=False),
                create_option(name=f"option9", description="option", option_type=3, required=False)
                ]


class Poll(object):
    """
    Object that contains state information about ongoing polls, this information is lost when te server is restarted
    """
    def __init__(self, user, description, percentage_mode, max_values, opts):
        self.description = description
        self.user = user
        self.user_options = {}
        self.percentage_mode = percentage_mode
        self.options = np.array(list(opts.values()))
        self.max_values = min(self.options.size, max_values)
        pass

    def update_user(self, user, values):
        """
        Update the user's choices
        :param user: The user object that selected the options
        :param values: the options chosen in a numpy array format, np.array([0,2])
        :return:
        """
        self.user_options[user.id] = values

    def create_embed(self):
        """
        create an embed representing the current poll.
        :return: The embed
        """
        options = "\n".join(self.options)
        height = np.zeros(len(self.options), dtype=int)
        for indices in self.user_options.values():
            height[indices] += 1
        votes = "\n".join([str(i) for i in height])

        embed = discord.Embed(title=self.description)
        embed.set_author(name=self.user.name, icon_url=self.user.avatar_url)
        embed.add_field(name="Option", value=options, inline=True)
        embed.add_field(name="Votes", value=votes, inline=True)
        return embed

    def results(self):
        """
        calculate the results of the poll in percentages and load the image.
        :return: Image representing results of the poll
        """
        # Sum all the results
        heights = np.zeros(len(self.options), dtype=int)
        for indices in self.user_options.values():
            heights[indices] += 1

        # Calculate the percentage
        if len(self.user_options) == 0:
            pass
        elif self.percentage_mode == PercentageMode.CUMULATIVE:
            heights = heights * 100 // np.sum(heights)
        else:
            heights = heights * 100 // len(self.user_options)

        # create the image
        buf = io.BytesIO()
        image = self._create_poll_image(heights)
        image.save(buf, format='PNG')
        buf.seek(0)

        return discord.File(buf, filename="pollresult.png")

    @staticmethod
    def _draw_text(draw, bar_width, bar_y, text, percentage, win):
        """
        Helper function to draw the text results on the Bar plot.
        :param draw: the PIL Draw object
        :param bar_width: Width of the bar
        :param bar_y: Y postition of the text
        :param text: name of the bar
        :param percentage: percentage
        :param win: If it is an winning answer
        :return:
        """
        font = settings.DISCORD_TTF_POLL_BOLD if win else settings.DISCORD_TTF_POLL_NORMAL
        lbound, rbound = 25 * settings.DISCORD_TTF_SCALE_FACTOR, bar_width - 25 * settings.DISCORD_TTF_SCALE_FACTOR

        label_center = bar_y - draw.textbbox((0, 0), text=text, font=font, anchor="lt")[3] // 2
        percentage_center = bar_y - draw.textbbox((0, 0), text=percentage, font=font, anchor="lt")[3] // 2

        draw.text((lbound, label_center), text, fill="white", anchor="lt", font=font)
        draw.text((rbound, percentage_center), percentage, fill="white", anchor="rt", font=font)

    def _create_poll_image(self, percentages):
        """
        Create a Bar plot image.
        :param percentages: array of result percentage
        :return: An image.
        """
        # Initialize the image bitmap
        bitmap = np.tile(settings.DISCORD_POLL_EMPTY, (percentages.size, 1, 1))
        bar_height, bar_width, _ = settings.DISCORD_POLL_EMPTY.shape
        max = np.max(percentages)

        # Fill the bars
        for i, percentage in enumerate(percentages):
            width = percentage * bar_width // 100
            bar = settings.DISCORD_POLL_WIN if percentage == max else settings.DISCORD_POLL_FULL
            bitmap[i * bar_height:(i + 1) * bar_height, :width] = bar[:, :width]

        # Create the PIL image and draw the text
        image = Image.fromarray(bitmap)
        draw = ImageDraw.Draw(image)
        for i, percentage in enumerate(percentages):
            bar_y = bar_height // 2 + i * bar_height
            self._draw_text(draw, bar_width, bar_y, self.options[i], f"{percentage}%", max == percentage)
        return image

    def get_components(self):
        """
        Turn the different option names into components for a select menu
        :return:
        """
        options = [create_select_option(label=name, value=str(i)) for i, name in enumerate(self.options)]
        return create_actionrow(
            create_select(options, placeholder=f"select up to {self.max_values} option(s)", max_values=self.max_values))


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
                       guild_ids=settings.DISCORD_GUILD_IDS, options=poll_options)
    @slashcommandlogger
    async def _createpoll(self, ctx, description, max_values=1, percentage_mode=PercentageMode.CUMULATIVE, **opts):
        """
        Create a poll with the user selected options

        :param ctx: The slash context
        :param description: title of the poll
        :param max_values: Amount of options a voter can select
        :param percentage_mode: Either cumulative or respondent
        :param opts: all of the poll options
        :return:
        """
        if len(opts) == 0:
            return await ctx.send(content="Please provide arguments", hidden=True)
        poll = Poll(ctx.author, description, percentage_mode, max_values, opts)
        components = [poll.get_components(), create_actionrow(create_button(ButtonStyle.grey, "Finish poll", custom_id="poll"))]
        message = await ctx.send(embed=poll.create_embed(), components=components, hidden=False)
        self.poll_map[message.id] = poll

    @staticmethod
    def disable_components(components):
        for interaction_row in components:
            for component in interaction_row:
                component.disabled = True
                if isinstance(component, discord_components.Button):
                    component.label = "Poll closed"


    @commands.Cog.listener()
    async def on_select_option(self, interaction):
        """
        When a voter selected new options
        """
        # Make sure the poll is current
        if interaction.message.id not in self.poll_map:
            components = interaction.message.components
            self.disable_components(components)

            # Deactivate the poll and give feedback to voter
            await interaction.message.edit(components=components)
            await interaction.respond(content="State information on this poll is lost in the ether.")
            return

        # Update the voter indices and update the original poll message
        indices = np.array([int(component.value) for component in interaction.component])
        poll = self.poll_map[interaction.message.id]
        poll.update_user(interaction.author, indices)

        await interaction.respond(type=InteractionType.UpdateMessage, embed=poll.create_embed())

    @commands.Cog.listener()
    async def on_button_click(self, interaction):
        """


        :param interaction: Information on what buttons was clicked, by what user etc...
        :return:
        """
        if interaction.custom_id != "poll":
            return
        # Button needs to be deactivated
        components = interaction.message.components
        self.disable_components(components)


        # If the poll is old deactivate it without further action
        if interaction.message.id not in self.poll_map:
            await interaction.message.edit(components=components)
            await interaction.respond(content="State information on this poll is lost in the ether.")
            return

        # Check if the person who clicked the button is the original author
        poll = self.poll_map[interaction.message.id]
        if poll.user.id != interaction.author.id:
            await interaction.respond(content="You did not create the poll.")
            return

        # Original polls
        await interaction.respond(type=7, components=components)
        await interaction.message.reply(content=f"> {poll.description}", file=poll.results())


def setup(client):
    client.add_cog(PollBot(client))
