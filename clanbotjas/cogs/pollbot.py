import functools
import io

import discord
import numpy as np
from PIL import Image, ImageDraw

from discord.ext import commands
from discord import option
from discord.commands.options import OptionChoice       

import cogmanager
import settings

class PercentageMode:
    CUMULATIVE = 0
    RESPONDENT = 1

class PollSelect(discord.ui.Select):
    async def callback(self, interaction: discord.Interaction):
        """
        When a voter selected new options
        """
        # Update the voter indices and update the original poll message
        indices = np.array([int(component) for component in self.values])
        self.view.update_user(interaction.user, indices)

        await interaction.response.edit_message(embed=self.view.create_embed())

class PollButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Finish poll"),

    async def callback(self, interaction: discord.Interaction):
        
        # If the poll is old deactivate it without further action
        # Check if the person who clicked the button is the original author
        if self.view.user.id != interaction.user.id:
            await interaction.respond(content="You did not create the poll.")
            return
        # Button needs to be deactivated
        for item in self.view.children:
           item.disabled = True
        # Original polls
        await interaction.response.edit_message(embed=self.view.create_embed(), view=self.view)
        await interaction.message.reply(content=f"> {self.view.description}", file=self.view.results())

class PollView(discord.ui.View):
    """
    Object that contains state information about ongoing polls, this information is lost when te server is restarted
    """
    def __init__(self, user, description, percentage_mode, max_values, opts):
        super().__init__(timeout=None) # timeout of the view must be set to None
       
        self.description = description
        self.user = user
        self.user_options = {}
        self.percentage_mode = percentage_mode
        self.options = np.array(list(opts))
        self.max_values = min(self.options.size, max_values)
        
        options = [discord.SelectOption(label=name, value=str(i)) for i, name in enumerate(self.options)]
        description = f"select up to {self.max_values} option(s)"
        self.add_item(PollSelect(placeholder=description, min_values=1, max_values=self.max_values, options=options))
        self.add_item(PollButton())

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
        embed.set_author(name=self.user.name, icon_url=self.user.avatar.url)
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

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.get_channel(settings.DISCORD_LOG_CHANNEL).send(":white_check_mark: Cog: \"pollbot\" ready.")


    @commands.slash_command(name="createpoll", description="Create a poll", guild_ids=settings.DISCORD_GUILD_IDS,
                            default_permission=False)
    @commands.has_role(settings.DISCORD_COMMAND_PERMISSION_ROLE)
    @option(name="description", description="Poll description", required=True)
    @option(name="max_values", description="Maximum options the voter can select",required=False)
    @option(name="percentage_mode", description="Percentage calculation mode",required=False,
            choices=[OptionChoice(name="cumulative", value=PercentageMode.CUMULATIVE),
                     OptionChoice(name="respondent", value=PercentageMode.RESPONDENT)])
    @option(name=f"option0", description="option", required=False)
    @option(name=f"option1", description="option", required=False)
    @option(name=f"option2", description="option", required=False)
    @option(name=f"option3", description="option", required=False)
    @option(name=f"option4", description="option", required=False)
    @option(name=f"option5", description="option", required=False)
    @option(name=f"option6", description="option", required=False)
    @option(name=f"option7", description="option", required=False)
    @option(name=f"option8", description="option", required=False)
    @option(name=f"option9", description="option", required=False)
    @slashcommandlogger
    async def _createpoll(self, ctx: discord.ApplicationContext, 
                          description: str,  max_values: int = 1, 
                          percentage_mode: int=PercentageMode.CUMULATIVE, 
                          option0: str = None, option1: str = None, option2: str = None, 
                          option3: str = None, option4: str = None, option5: str = None, 
                          option6: str = None, option7: str = None, option8: str = None, 
                          option9: str = None):
        """
        Create a poll with the user selected options

        :param ctx: The slash context
        :param description: title of the poll
        :param max_values: Amount of options a voter can select
        :param percentage_mode: Either cumulative or respondent
        :param opts: all of the poll options
        :return:
        """   
        opts = [option0, option1, option2, option3, option4, option5, option6, option7, option8, option9]
        opts = list(filter(lambda item: item is not None, opts))
        if len(opts) == 0:
            return await ctx.respond(content="Please provide arguments", ephemeral=True)
        poll = PollView(ctx.author, description, percentage_mode, max_values, opts)
        await ctx.respond(embed=poll.create_embed(), view=poll)

def setup(client):
    client.add_cog(PollBot(client))
