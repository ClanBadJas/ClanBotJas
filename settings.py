import os

import discord
from discord_slash.model import SlashCommandPermissionType
from discord_slash.utils.manage_commands import create_choice, create_permission
from dotenv import load_dotenv

load_dotenv()
DISCORD_GUILD_ID = int(os.getenv('DISCORD_GUILD_ID'))
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_VOICE_CHANNEL_BOT_ID = int(os.getenv('DISCORD_VOICE_CHANNEL_BOT_ID'))
DISCORD_LOG_CHANNEL = int(os.getenv('DISCORD_LOG_CHANNEL'))
DISCORD_ROLEBOT_SETTINGS_CHANNEL = int(os.getenv('DISCORD_ROLEBOT_SETTINGS_CHANNEL'))

DISCORD_GUILD_IDS = [DISCORD_GUILD_ID]
INTENTS = discord.Intents(members=True, presences=True, voice_states=True, guild_messages=True, guilds=True)
DISCORD_COGS = [
    create_choice(name="rolebot", value="RoleBot"),
    create_choice(name="commands", value="Commands"),
    create_choice(name="voicechannelbot", value="VoiceChannelBot"),
]

DISCORD_COMMAND_PERMISSION_ROLE = int(os.getenv('DISCORD_COMMAND_PERMISSION_ROLE'))
DISCORD_COMMAND_PERMISSIONS = {
    DISCORD_GUILD_ID: [
        create_permission(DISCORD_COMMAND_PERMISSION_ROLE, SlashCommandPermissionType.ROLE, True),
    ]
}
