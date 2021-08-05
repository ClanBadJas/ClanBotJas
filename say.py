import os

import discord
from discord.ext import commands

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')
ANNOUNCEMENT_CHANNEL = int(os.getenv('ANNOUNCEMENT_CHANNEL'))


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def say_channel(self, ctx, id: int, *, arg):
        """Stops and disconnects the bot from voice"""
        channel = bot.get_channel(id)
        await channel.send(arg)

    @commands.command()
    async def say(self, ctx, *, arg):
        """Stops and disconnects the bot from voice"""
        channel = bot.get_channel(ANNOUNCEMENT_CHANNEL)
        await channel.send(arg)


bot = commands.Bot(command_prefix=commands.when_mentioned_or("."),
                   description='Relatively simple music bot example')

@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')

bot.add_cog(Music(bot))
bot.run(TOKEN)
