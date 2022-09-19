import os

import discord
import numpy as np
from PIL import ImageFont, Image
from discord.commands.options import OptionChoice
from dotenv import load_dotenv

load_dotenv()

def _int(name: str):
    try:
        return int(name)
    except ValueError:
        return None


# Get General Bot settings
DISCORD_TOKEN = os.getenv("BOT_TOKEN")
DISCORD_DB_LINK = os.getenv("DB_LINK_ASYNCIO")

# Enable/disable feature toggles:
DISCORD_COMMANDS_ENABLE = os.getenv("COMMANDS_ENABLE") in ["true", None]
DISCORD_VOICE_SCALER_ENABLE = os.getenv("VOICE_SCALER_ENABLE") == "true"
DISCORD_ROLEBOT_ENABLE = os.getenv("ROLEBOT_ENABLE") == "true"
DISCORD_AUTO_ROLE_ENABLE = os.getenv("AUTO_ROLE_ENABLE") == "true"
DISCORD_POLL_ENABLE = os.getenv("POLL_ENABLE") == "true"

#  The default cog(s) to be started
DISCORD_COGS = []

# If non-default cogs are enabled in config, add cogs to DISCORD_COGS to be started list.
if DISCORD_COMMANDS_ENABLE:
    DISCORD_COGS.append(OptionChoice(name="commands", value="Commands"))

if DISCORD_VOICE_SCALER_ENABLE:
    DISCORD_COGS.append(OptionChoice(name="voicechannelbot", value="VoiceChannelBot"))

if DISCORD_ROLEBOT_ENABLE:
    DISCORD_COGS.append(OptionChoice(name="rolebot", value="RoleBot"))
    # Get Self-Role text channel subscription settings
    DISCORD_ROLEBOT_SETTINGS_CHANNEL = _int(os.getenv("ROLEBOT_SETTINGS_CHANNEL"))  # TODO: Remove
    DISCORD_GUILD_ID = _int(os.getenv("GUILD_ID")) # TODO: Remove

if DISCORD_AUTO_ROLE_ENABLE:
    DISCORD_COGS.append(OptionChoice(name="autorole", value="AutoRole"))

if DISCORD_POLL_ENABLE:
    DISCORD_COGS.append(OptionChoice(name="pollbot", value="PollBot"))
    # Get Poll settings
    DISCORD_POLL_FONT_REGULAR = os.getenv("POLL_FONT_REGULAR")
    DISCORD_POLL_FONT_BOLD = os.getenv("POLL_FONT_BOLD")
    DISCORD_POLL_FONT_SCALE = _int(os.getenv("POLL_FONT_SCALE"))
    DISCORD_TTF_SCALE_FACTOR = DISCORD_POLL_FONT_SCALE
    DISCORD_TTF_POLL_NORMAL = ImageFont.truetype(
        "data/{}".format(DISCORD_POLL_FONT_REGULAR), 15 * DISCORD_TTF_SCALE_FACTOR
    )
    DISCORD_TTF_POLL_BOLD = ImageFont.truetype(
        "data/{}".format(DISCORD_POLL_FONT_BOLD), 15 * DISCORD_TTF_SCALE_FACTOR
    )
    DISCORD_POLL_EMPTY, DISCORD_POLL_FULL, DISCORD_POLL_WIN = np.split(
        np.array(Image.open("data/basepollimages.png")), 3
    )

# Define which intents the bot requires to function
INTENTS = discord.Intents(
    members=True,
    presences=True,
    voice_states=True,
    guild_messages=True,
    guilds=True,
    message_content=True,
)
