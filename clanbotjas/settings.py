import os

import discord
import numpy as np
from PIL import ImageFont, Image
from discord_slash.model import SlashCommandPermissionType
from discord_slash.utils.manage_commands import create_choice, create_permission
from dotenv import load_dotenv

load_dotenv()


def _int(name: str):
    try:
        return int(name)
    except ValueError:
        return name


DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

DISCORD_GUILD_ID = _int(os.getenv('DISCORD_GUILD_ID'))
DISCORD_VOICE_CHANNEL_DEFAULT_NAME = os.getenv("VOICE_CHANNEL_DEFAULT_NAME")
DISCORD_VOICE_CHANNEL_CATEGORY = _int(os.getenv('DISCORD_VOICE_CHANNEL_CATEGORY'))
DISCORD_LOG_CHANNEL = _int(os.getenv('DISCORD_LOG_CHANNEL'))
DISCORD_ROLEBOT_SETTINGS_CHANNEL = _int(os.getenv('DISCORD_ROLEBOT_SETTINGS_CHANNEL'))
DISCORD_COMMAND_PERMISSION_ROLE = _int(os.getenv('DISCORD_COMMAND_PERMISSION_ROLE'))

DISCORD_GUILD_IDS = [DISCORD_GUILD_ID]
INTENTS = discord.Intents(members=True, presences=True, voice_states=True, guild_messages=True, guilds=True)
DISCORD_COGS = [
    create_choice(name="rolebot", value="RoleBot"),
    create_choice(name="commands", value="Commands"),
    create_choice(name="voicechannelbot", value="VoiceChannelBot"),
    create_choice(name="pollbot", value="PollBot"),
]

DISCORD_COMMAND_PERMISSIONS = {
    DISCORD_GUILD_ID: [create_permission(DISCORD_COMMAND_PERMISSION_ROLE, SlashCommandPermissionType.ROLE, True),]
}

DISCORD_TTF_SCALE_FACTOR = 10
DISCORD_TTF_POLL_NORMAL = ImageFont.truetype("data/Helvetica.ttf", 15 * DISCORD_TTF_SCALE_FACTOR)
DISCORD_TTF_POLL_BOLD = ImageFont.truetype("data/Helvetica-Bold-Font.ttf", 15 * DISCORD_TTF_SCALE_FACTOR)
DISCORD_POLL_EMPTY, DISCORD_POLL_FULL, DISCORD_POLL_WIN = np.split(np.array(Image.open('data/basepollimages.png')), 3)