# bot.py
import os
import random

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')
ALLOW_ANNOUNCEMENT_ROLE = 873270271132454942
bot = commands.Bot(command_prefix='!')

def has_role(member, role_id):
    for role in member.roles:
        if role.id == role_id:
            return True

    return False

@bot.command(name='say')
async def say(ctx):
    if has_role(ctx.author, ALLOW_ANNOUNCEMENT_ROLE):
        await ctx.send(ctx.message.content[5:])
        await ctx.message.delete()
    else:
        await ctx.send('You do not have permissions to use that command.')




if __name__ == "__main__":
    bot.run(TOKEN)
