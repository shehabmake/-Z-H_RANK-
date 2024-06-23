import discord
from discord.ext import commands
from discord import Interaction, app_commands
import json
import os
import logging
import aiofiles
from datetime import datetime
import random
from discord import Interaction, app_commands
import logging
import asyncio
from keep_alive import keep_alive
from dotenv import load_dotenv


load_dotenv()

keep_alive()


#from dotenv import load_dotenv
#load_dotenv()

# Initialize bot
intents = discord.Intents.default()
intents.members = True  # Required to fetch member info
bot = commands.Bot(command_prefix='/', intents=intents)

# Set up logging
logging.basicConfig(level=logging.INFO)


# Load databases on startup
async def load_json(file_path: str, default: dict) -> dict:
    try:
        if os.path.exists(file_path):
            async with aiofiles.open(file_path, "r") as file:
                return json.loads(await file.read())
        else:
            return default
    except Exception as e:
        logging.error(f"Error loading {file_path}: {e}")
        return default


# Save databases
async def save_json(file_path: str, data: dict) -> None:
    try:
        async with aiofiles.open(file_path, "w") as file:
            await file.write(json.dumps(data, indent=4))
    except Exception as e:
        logging.error(f"Error saving {file_path}: {e}")


# File paths
database_path = "database.json"
clans_path = "clans.json"
events_path = "events.json"
log_database_path = "log_database.json"

# Global variables for databases
database = {}
clans_database = {}  # Clans database to store clans and their members
events_database = {}  # Events database to store events and participants
log_database = {}

rank_name_mapping = {
    ('3V3_GAME', 0, 500): "📥new_3V3📥",
    ('3V3_GAME', 500, 1000): "🍼noob_3V3🍼",
    ('3V3_GAME', 1000, 2000): "🔸AMATEUR_3V3🔸",
    ('3V3_GAME', 2000, 3000): "🔹MEDIUM_3V3🔹",
    ('3V3_GAME', 3000, 4000): "🥉SEMI-PRO_3V3🥉",
    ('3V3_GAME', 4000, 5000): "🥈PRO_3V3🥈",
    ('3V3_GAME', 5000, 5500): "🥇HIGH-PRO_3V3🥇",
    ('3V3_GAME', 5500, 6000): "🏆EXPERT_3V3🏆",
    ('AIR_GAME', 0, 500): "📥new_AIR📥",
    ('AIR_GAME', 500, 1000): "🍼noob_AIR🍼",
    ('AIR_GAME', 1000, 2000): "🔸AMATEUR_AIR🔸",
    ('AIR_GAME', 2000, 3000): "🔹MEDIUM_AIR🔹",
    ('AIR_GAME', 3000, 4000): "🥉SEMI-PRO_AIR🥉",
    ('AIR_GAME', 4000, 5000): "🥈PRO_AIR🥈",
    ('AIR_GAME', 5000, 5500): "🥇HIGH-PRO_AIR🥇",
    ('AIR_GAME', 5500, 6000): "🏆EXPERT_AIR🏆"
}

# List of roles to be managed by the bot
BOT_ROLES = [
    "📥new_3V3📥", "🍼noob_3V3🍼", "🔸AMATEUR_3V3🔸", "🔹MEDIUM_3V3🔹",
    "🥉SEMI-PRO_3V3🥉", "🥈PRO_3V3🥈", "🥇HIGH-PRO_3V3🥇", "🏆EXPERT_3V3🏆",
    "📥new_AIR📥", "🍼noob_AIR🍼", "🔸AMATEUR_AIR🔸", "🔹MEDIUM_AIR🔹",
    "🥉SEMI-PRO_AIR🥉", "🥈PRO_AIR🥈", "🥇HIGH-PRO_AIR🥇", "🏆EXPERT_AIR🏆",
    "🚫banned🚫", "⚜️bot_admin⚜️", "⌨️bot_developer⌨️", "🛡️bot_moderator🛡️"
]


def determine_rank_name(game_mode: str, rank: int) -> str:
    for (gm, min_rank, max_rank), rank_name in rank_name_mapping.items():
        if gm == game_mode and min_rank <= rank < max_rank:
            return rank_name
    return "Unknown"


# Save database functions
async def save_database() -> None:
    await save_json(database_path, database)


async def save_clans_database() -> None:
    await save_json(clans_path, clans_database)


async def save_events_database() -> None:
    await save_json(events_path, events_database)


async def save_log_database() -> None:
    await save_json(log_database_path, log_database)


# Custom Exceptions
class NotAdmin(Exception):
    pass


class NotDeveloper(Exception):
    pass


class NotModerator(Exception):
    pass


# Check if user is an admin for command checks
def is_admin(interaction: Interaction):
    admin_ids = [
        765417780500889611, 836651779302096906, 393912053984788481,
        1070097101217861724, 642286293384167445,594974233822494720
    ]  # Add admin IDs here
    if interaction.user.id not in admin_ids:
        raise NotAdmin("You do not have admin permissions.")
    return True


# Helper function to check if a user is an admin for event checks
def is_user_admin(user: discord.User):
    admin_ids = [
        765417780500889611, 836651779302096906, 393912053984788481,
        1070097101217861724, 642286293384167445,594974233822494720
    ]  # Add admin IDs here
    is_admin = user.id in admin_ids
    logging.info(
        f"Checking if user {user.name} (ID: {user.id}) is admin: {is_admin}")
    return is_admin


# Check if user is a developer
def is_developer(interaction: Interaction):
    developer_ids = [
        765417780500889611, 393912053984788481, 642286293384167445,594974233822494720
    ]  # Add developer IDs here
    if interaction.user.id not in developer_ids:
        raise NotDeveloper("You do not have developer permissions.")
    return True


# Check if user is a moderator
def is_moderator(interaction: Interaction):
    moderator_ids = [
        765417780500889611, 836651779302096906, 393912053984788481,
        1070097101217861724, 642286293384167445,594974233822494720
    ]  # Add moderator IDs here
    if interaction.user.id not in moderator_ids and interaction.user.id not in admin_ids and interaction.user.id not in developer_ids:
        raise NotModerator("You do not have moderator permissions.")
    return True


# IDs for admin, developer, and moderator roles
admin_ids = [
    765417780500889611, 836651779302096906, 393912053984788481,
    1070097101217861724, 642286293384167445,594974233822494720
]
developer_ids = [765417780500889611, 393912053984788481, 642286293384167445,594974233822494720]
moderator_ids = [
    765417780500889611, 836651779302096906, 393912053984788481,
    1070097101217861724, 642286293384167445,594974233822494720
]

#DEVELOPER_PASSWORD

DEVELOPER_PASSWORD = os.getenv("DEVELOPER_PASSWORD")


# Check if user is banned
async def check_banned(interaction: Interaction):
    user_id = str(interaction.user.id)
    if user_id in database and database[user_id].get('banned', False):
        await interaction.response.send_message(
            "You are banned from using the bot.")
        return False
    return True


# Error handler
@bot.event
async def on_command_error(interaction: Interaction, error):
    if isinstance(error, NotAdmin):
        await interaction.response.send_message(
            "Permission denied: You do not have admin permissions.",
            ephemeral=True)
    elif isinstance(error, NotDeveloper):
        await interaction.response.send_message(
            "Permission denied: You do not have developer permissions.",
            ephemeral=True)
    elif isinstance(error, NotModerator):
        await interaction.response.send_message(
            "Permission denied: You do not have moderator permissions.",
            ephemeral=True)
    else:
        await interaction.response.send_message(
            f"An error occurred: {str(error)}", ephemeral=True)


# Update rank names for a player
def update_rank_names(player_data: dict) -> None:
    player_data['rank_3v3_name'] = determine_rank_name(
        player_data['3V3_GAME']['rank'])
    player_data['rank_AIR_name'] = determine_rank_name(
        player_data['AIR_GAME']['rank'])


# Define the choices for the reset rank history command
RESET_CHOICES = [
    app_commands.Choice(name='all', value='all'),
    app_commands.Choice(name='done', value='done')
]


# Autocomplete function for clans
async def clan_autocomplete(interaction: Interaction, current: str):
    return [
        app_commands.Choice(name=clan, value=clan) for clan in clans_database
        if current.lower() in clan.lower()
    ][:25]  # Discord only supports a maximum of 25 choices in auto-complete


# Autocomplete function for events
async def event_autocomplete(interaction: Interaction, current: str):
    return [
        app_commands.Choice(name=event, value=event)
        for event in events_database if current.lower() in event.lower()
    ][:25]  # Discord only supports a maximum of 25 choices in auto-complete


### User Commands ###


# Command to check if the bot is alive
@bot.tree.command(name="ping", description="Check if the bot is alive or not.")
async def ping(interaction: Interaction):
    if not await check_banned(interaction):
        return
    await interaction.response.send_message('Pong!')


# Command to display help message in Arabic and English
@bot.tree.command(name="help",
                  description="Display help message in Arabic and English.")
async def help(interaction: Interaction):
    help_message = (
        "**Help - English**\n"
        "1. `/ping` - Check if the bot is alive.\n"
        "2. `/register` - Register a new player.\n"
        "3. `/add_clan_member` - Add a member to a clan (moderator only).\n"
        "4. `/player_stats` - Display player stats.\n"
        "5. `/toprank` - Display top-ranked players.\n"
        "6. `/event_sign_in` - Sign in to an event.\n"
        "7. `/sign_out` - Sign out of an event.\n"
        "8. `/view_event_names` - View available events.\n"
        "9. `/view_event_participants` - View participants of an event.\n"
        "10. `/maketeams` - Create balanced teams based on player mentions.\n"
        "11. `/list_clans` - List all available clans.\n"
        "\n"
        "**مساعدة - العربية**\n"
        "1. `/ping` - تحقق مما إذا كان البوت يعمل.\n"
        "2. `/register` - تسجيل لاعب جديد.\n"
        "3. `/add_clan_member` - إضافة عضو إلى عشيرة (للمشرف فقط).\n"
        "4. `/player_stats` - عرض إحصائيات اللاعب.\n"
        "5. `/toprank` - عرض أفضل اللاعبين تصنيفًا.\n"
        "6. `/event_sign_in` - التسجيل في فعالية.\n"
        "7. `/sign_out` - إلغاء التسجيل من فعالية.\n"
        "8. `/view_event_names` - مشاهدة الفعاليات المتاحة.\n"
        "9. `/view_event_participants` - مشاهدة المشاركين في فعالية.\n"
        "10. `/maketeams` - إنشاء فرق متوازنة بناءً على ذكر اللاعبين.\n"
        "11. `/list_clans` - عرض جميع العشائر المتاحة.\n")
    await interaction.response.send_message(f"```{help_message}```")


# Command to register a new player
@bot.tree.command(name="register", description="Register a new player.")
@app_commands.describe(nickname="Your nickname")
async def register(interaction: Interaction, nickname: str):
    if not await check_banned(interaction):
        return

    user_id = str(interaction.user.id)
    no_clan_name = "😢NO CLAN😢"

    # Ensure the "😢NO CLAN😢" clan exists
    if no_clan_name not in clans_database:
        clans_database[no_clan_name] = []

    if user_id in database:
        await interaction.response.send_message("You are already registered.")
        return
    if any(player['nickname'] == nickname for player in database.values()):
        await interaction.response.send_message(
            "This nickname is already in use.")
        return
    if len(nickname) > 12:
        await interaction.response.send_message(
            "Nickname exceeds 12 characters.")
        return

    player_info = {
        "player_name": interaction.user.name,
        "nickname": nickname,
        "discord_id": interaction.user.id,
        "clan": no_clan_name,
        "banned": False,
        "3V3_GAME": {
            "rank": 490,
            "rank_name": determine_rank_name('3V3_GAME', 490),
            "wins": 0,
            "losses": 0,
            "win_rate": 0.0
        },
        "AIR_GAME": {
            "rank": 490,
            "rank_name": determine_rank_name('AIR_GAME', 490),
            "wins": 0,
            "losses": 0,
            "win_rate": 0.0
        }
    }

    database[user_id] = player_info
    clans_database[no_clan_name].append(user_id)
    await save_database()
    await save_clans_database()
    await interaction.response.send_message(
        "You have been registered successfully.")
    await assign_roles(interaction.guild, [interaction.user.id])


# Army choices for autocomplete
ARMY_CHOICES = [
    app_commands.Choice(name='usa', value='USA'),
    app_commands.Choice(name='usa_air', value='usa_air'),
    app_commands.Choice(name='usa_laser', value='usa_laser'),
    app_commands.Choice(name='usa_super', value='usa_super'),
    app_commands.Choice(name='GLA', value='GLA'),
    app_commands.Choice(name='GLA_Stealth', value='GLA_Stealth'),
    app_commands.Choice(name='GLA_tox', value='GLA_tox'),
    app_commands.Choice(name='GLA_dumo', value='GLA_dumo'),
    app_commands.Choice(name='china', value='china'),
    app_commands.Choice(name='china_inf', value='china_inf'),
    app_commands.Choice(name='china_nuke', value='china_nuke'),
    app_commands.Choice(name='china_tank', value='china_tank')
]

# Game mode choices for autocomplete
GAME_MODE_CHOICES = [
    app_commands.Choice(name='3v3_GAME', value='3V3_GAME'),
    app_commands.Choice(name='AIR_GAME', value='AIR_GAME')
]

# armys_database
armys_data = {
    "armys": {
        "USA": 80,
        "usa_air": 100,
        "usa_laser": 85,
        "usa_super": 75,
        "GLA": 75,
        "GLA_Stealth": 78,
        "GLA_tox": 88,
        "GLA_dumo": 81,
        "china": 75,
        "china_inf": 85,
        "china_nuke": 82,
        "china_tank": 78
    },
    "USA": {
        "With List": {
            "USA": 12,
            "usa_air": 17,
            "usa_laser": 15,
            "usa_super": 10,
            "GLA": 7,
            "GLA_Stealth": 5,
            "GLA_tox": 10,
            "GLA_dumo": 8,
            "china": 10,
            "china_inf": 12,
            "china_nuke": 10,
            "china_tank": 7
        },
        "Against List": {
            "USA": 0,
            "usa_air": -15,
            "usa_laser": -5,
            "usa_super": 0,
            "GLA": 0,
            "GLA_Stealth": 0,
            "GLA_tox": 0,
            "GLA_dumo": 0,
            "china": -7,
            "china_inf": -10,
            "china_nuke": -5,
            "china_tank": -3
        }
    },
    "usa_air": {
        "With List": {
            "USA": 15,
            "usa_laser": 12,
            "usa_air": 15,
            "usa_super": 10,
            "GLA": 7,
            "GLA_Stealth": 3,
            "GLA_tox": 15,
            "GLA_dumo": 10,
            "china": 5,
            "china_inf": 5,
            "china_nuke": 15,
            "china_tank": 12
        },
        "Against List": {
            "USA": 0,
            "usa_air": 0,
            "usa_laser": -5,
            "usa_super": 0,
            "GLA": -10,
            "GLA_Stealth": -15,
            "GLA_tox": -5,
            "GLA_dumo": -5,
            "china": -5,
            "china_inf": -10,
            "china_nuke": -5,
            "china_tank": -10
        }
    },
    "usa_laser": {
        "With List": {
            "USA": 12,
            "usa_laser": 13,
            "usa_air": 17,
            "usa_super": 10,
            "GLA": 7,
            "GLA_Stealth": 3,
            "GLA_tox": 10,
            "GLA_dumo": 8,
            "china": 10,
            "china_inf": 12,
            "china_nuke": 10,
            "china_tank": 7
        },
        "Against List": {
            "USA": 0,
            "usa_air": -15,
            "usa_laser": 0,
            "usa_super": -10,
            "GLA": 0,
            "GLA_Stealth": -5,
            "GLA_tox": -7,
            "GLA_dumo": -5,
            "china": -7,
            "china_inf": -10,
            "china_nuke": -5,
            "china_tank": -5
        }
    },
    "usa_super": {
        "With List": {
            "USA": 12,
            "usa_air": 17,
            "usa_laser": 15,
            "usa_super": 10,
            "GLA": 7,
            "GLA_Stealth": 5,
            "GLA_tox": 10,
            "GLA_dumo": 8,
            "china": 10,
            "china_inf": 12,
            "china_nuke": 10,
            "china_tank": 7
        },
        "Against List": {
            "USA": 0,
            "usa_air": -3,
            "usa_laser": 0,
            "usa_super": 0,
            "GLA": 0,
            "GLA_Stealth": 0,
            "GLA_tox": -1,
            "GLA_dumo": 0,
            "china": -7,
            "china_inf": -10,
            "china_nuke": -5,
            "china_tank": -3
        }
    },
    "GLA": {
        "With List": {
            "USA": 10,
            "usa_air": 17,
            "usa_laser": 13,
            "usa_super": 9,
            "GLA": 0,
            "GLA_Stealth": 3,
            "GLA_tox": 7,
            "GLA_dumo": 5,
            "china": 10,
            "china_inf": 12,
            "china_nuke": 7,
            "china_tank": 3
        },
        "Against List": {
            "USA": -7,
            "usa_air": -15,
            "usa_laser": -10,
            "usa_super": -5,
            "GLA": 0,
            "GLA_Stealth": 0,
            "GLA_tox": -7,
            "GLA_dumo": -5,
            "china": -10,
            "china_inf": -10,
            "china_nuke": -7,
            "china_tank": -5
        }
    },
    "GLA_Stealth": {
        "With List": {
            "USA": 10,
            "usa_air": 17,
            "usa_laser": 13,
            "usa_super": 9,
            "GLA": 3,
            "GLA_Stealth": 3,
            "GLA_tox": 7,
            "GLA_dumo": 5,
            "china": 10,
            "china_inf": 12,
            "china_nuke": 7,
            "china_tank": 3
        },
        "Against List": {
            "USA": -10,
            "usa_air": -15,
            "usa_laser": -13,
            "usa_super": -7,
            "GLA": -7,
            "GLA_Stealth": 0,
            "GLA_tox": -10,
            "GLA_dumo": -10,
            "china": -3,
            "china_inf": -3,
            "china_nuke": -10,
            "china_tank": -7
        }
    },
    "GLA_tox": {
        "With List": {
            "USA": 10,
            "usa_air": 17,
            "usa_laser": 13,
            "usa_super": 9,
            "GLA": 3,
            "GLA_Stealth": 3,
            "GLA_tox": 7,
            "GLA_dumo": 5,
            "china": 10,
            "china_inf": 12,
            "china_nuke": 7,
            "china_tank": 3
        },
        "Against List": {
            "USA": -10,
            "usa_air": -15,
            "usa_laser": -13,
            "usa_super": -7,
            "GLA": 0,
            "GLA_Stealth": 0,
            "GLA_tox": 0,
            "GLA_dumo": 0,
            "china": -10,
            "china_inf": -13,
            "china_nuke": 0,
            "china_tank": -5
        }
    },
    "GLA_dumo": {
        "With List": {
            "USA": 10,
            "usa_air": 17,
            "usa_laser": 13,
            "usa_super": 9,
            "GLA": 3,
            "GLA_Stealth": 3,
            "GLA_tox": 7,
            "GLA_dumo": 5,
            "china": 10,
            "china_inf": 12,
            "china_nuke": 7,
            "china_tank": 3
        },
        "Against List": {
            "USA": -10,
            "usa_air": -15,
            "usa_laser": -13,
            "usa_super": -7,
            "GLA": 0,
            "GLA_Stealth": 0,
            "GLA_tox": -5,
            "GLA_dumo": 0,
            "china": -10,
            "china_inf": -13,
            "china_nuke": 0,
            "china_tank": 0
        }
    },
    "china": {
        "With List": {
            "USA": 10,
            "usa_air": 13,
            "usa_laser": 12,
            "usa_super": 8,
            "GLA": 8,
            "GLA_Stealth": 5,
            "GLA_tox": 10,
            "GLA_dumo": 9,
            "china": 0,
            "china_inf": 3,
            "china_nuke": 9,
            "china_tank": 8
        },
        "Against List": {
            "USA": -5,
            "usa_air": -10,
            "usa_laser": -7,
            "usa_super": -3,
            "GLA": -3,
            "GLA_Stealth": -5,
            "GLA_tox": -7,
            "GLA_dumo": -2,
            "china": 0,
            "china_inf": -5,
            "china_nuke": -2,
            "china_tank": -5
        }
    },
    "china_inf": {
        "With List": {
            "USA": 10,
            "usa_air": 13,
            "usa_laser": 12,
            "usa_super": 8,
            "GLA": 8,
            "GLA_Stealth": 5,
            "GLA_tox": 10,
            "GLA_dumo": 9,
            "china": 5,
            "china_inf": 1,
            "china_nuke": 10,
            "china_tank": 9
        },
        "Against List": {
            "USA": -5,
            "usa_air": -10,
            "usa_laser": -7,
            "usa_super": -3,
            "GLA": -3,
            "GLA_Stealth": -5,
            "GLA_tox": -7,
            "GLA_dumo": -2,
            "china": -15,
            "china_inf": 0,
            "china_nuke": 0,
            "china_tank": -1
        }
    },
    "china_nuke": {
        "With List": {
            "USA": 10,
            "usa_air": 13,
            "usa_laser": 12,
            "usa_super": 8,
            "GLA": 8,
            "GLA_Stealth": 5,
            "GLA_tox": 10,
            "GLA_dumo": 9,
            "china": 10,
            "china_inf": 12,
            "china_nuke": 2,
            "china_tank": 2
        },
        "Against List": {
            "USA": -7,
            "usa_air": -20,
            "usa_laser": -10,
            "usa_super": -10,
            "GLA": -5,
            "GLA_Stealth": -7,
            "GLA_tox": -12,
            "GLA_dumo": -10,
            "china": -7,
            "china_inf": -15,
            "china_nuke": 0,
            "china_tank": -5
        }
    },
    "china_tank": {
        "With List": {
            "USA": 10,
            "usa_air": 15,
            "usa_laser": 12,
            "usa_super": 8,
            "GLA": 5,
            "GLA_Stealth": 2,
            "GLA_tox": 10,
            "GLA_dumo": 9,
            "china": 10,
            "china_inf": 11,
            "china_nuke": 3,
            "china_tank": 3
        },
        "Against List": {
            "USA": -7,
            "usa_air": -20,
            "usa_laser": -10,
            "usa_super": -5,
            "GLA": -3,
            "GLA_Stealth": -5,
            "GLA_tox": -12,
            "GLA_dumo": -10,
            "china": -10,
            "china_inf": -13,
            "china_nuke": -8,
            "china_tank": 0
        }
    },
}


# Function to calculate army strength based on relationships
def get_rates(a0: str, a1: str, a2: str, g1: str, g2: str, g3: str):
    total_rnk1 = (
        armys_data["armys"][a0] + armys_data[a0]["With List"].get(a1, 0) +
        armys_data[a0]["With List"].get(a2, 0) +
        armys_data[a0]["Against List"].get(g1, 0) +
        armys_data[a0]["Against List"].get(g2, 0) +
        armys_data[a0]["Against List"].get(g3, 0) + armys_data["armys"][a1] +
        armys_data[a1]["With List"].get(a0, 0) +
        armys_data[a1]["With List"].get(a2, 0) +
        armys_data[a1]["Against List"].get(g1, 0) +
        armys_data[a1]["Against List"].get(g2, 0) +
        armys_data[a1]["Against List"].get(g3, 0) + armys_data["armys"][a2] +
        armys_data[a2]["With List"].get(a0, 0) +
        armys_data[a2]["With List"].get(a1, 0) +
        armys_data[a2]["Against List"].get(g1, 0) +
        armys_data[a2]["Against List"].get(g2, 0) +
        armys_data[a2]["Against List"].get(g3, 0))
    total_rnk2 = (
        armys_data["armys"][g1] + armys_data[g1]["With List"].get(g2, 0) +
        armys_data[g1]["With List"].get(g3, 0) +
        armys_data[g1]["Against List"].get(a0, 0) +
        armys_data[g1]["Against List"].get(a1, 0) +
        armys_data[g1]["Against List"].get(a2, 0) + armys_data["armys"][g2] +
        armys_data[g2]["With List"].get(g1, 0) +
        armys_data[g2]["With List"].get(g3, 0) +
        armys_data[g2]["Against List"].get(a0, 0) +
        armys_data[g2]["Against List"].get(a1, 0) +
        armys_data[g2]["Against List"].get(a2, 0) + armys_data["armys"][g3] +
        armys_data[g3]["With List"].get(g1, 0) +
        armys_data[g3]["With List"].get(g2, 0) +
        armys_data[g3]["Against List"].get(a0, 0) +
        armys_data[g3]["Against List"].get(a1, 0) +
        armys_data[g3]["Against List"].get(a2, 0))
    r = total_rnk1 / total_rnk2
    return r, total_rnk1, total_rnk2


# rankrecord
@bot.tree.command(
    name="rankrecord",
    description="Record the results of a match and update ranks.")
@app_commands.describe(winner2="Second winning player",
                       winner3="Third winning player",
                       winner_army1="Army of first winning player",
                       winner_army2="Army of second winning player",
                       winner_army3="Army of third winning player",
                       loser1="First losing player",
                       loser2="Second losing player",
                       loser3="Third losing player",
                       loser_army1="Army of first losing player",
                       loser_army2="Army of second losing player",
                       loser_army3="Army of third losing player",
                       game_mode="Game mode")
@app_commands.choices(winner_army1=ARMY_CHOICES,
                      winner_army2=ARMY_CHOICES,
                      winner_army3=ARMY_CHOICES,
                      loser_army1=ARMY_CHOICES,
                      loser_army2=ARMY_CHOICES,
                      loser_army3=ARMY_CHOICES,
                      game_mode=GAME_MODE_CHOICES)
async def rankrecord(
        interaction: Interaction, winner2: discord.Member,
        winner3: discord.Member, winner_army1: app_commands.Choice[str],
        winner_army2: app_commands.Choice[str],
        winner_army3: app_commands.Choice[str], loser1: discord.Member,
        loser2: discord.Member, loser3: discord.Member,
        loser_army1: app_commands.Choice[str],
        loser_army2: app_commands.Choice[str],
        loser_army3: app_commands.Choice[str],
        game_mode: app_commands.Choice[str]):
    await interaction.response.defer()  # Defer the response to give more time

    try:
        if not await check_banned(interaction):
            return

        winner1 = interaction.user  # Winner 1 is the user who invoked the command
        winner_team = [winner1, winner2, winner3]
        loser_team = [loser1, loser2, loser3]
        all_players = winner_team + loser_team

        # Check for duplicate players
        if len(set(all_players)) != len(all_players):
            await interaction.followup.send(
                "Error: Duplicate players are not allowed.")
            return

        # Check if all players are registered
        for player in all_players:
            if str(player.id) not in database:
                await interaction.followup.send(
                    f"Error: Player {player.mention} is not registered.")
                return

        # Calculate total rank points based on game_mode
        total_winner_rank = sum(
            database[str(player.id)][game_mode.value]['rank']
            for player in winner_team)
        total_loser_rank = sum(
            database[str(player.id)][game_mode.value]['rank']
            for player in loser_team)

        # Calculate z
        z = total_loser_rank / total_winner_rank if total_winner_rank else 0  # Avoid division by zero

        # Calculate r
        r, total_rnk1, total_rnk2 = get_rates(
            loser_army1.value,
            loser_army2.value,
            loser_army3.value,
            winner_army1.value,
            winner_army2.value,
            winner_army3.value,
        )

        # Define the function to determine k and L based on old_rank
        def determine_k_l(old_rank):
            if 0 <= old_rank < 500:
                return 450, 10
            elif 500 <= old_rank < 1000:
                return 400, 50
            elif 1000 <= old_rank < 2000:
                return 350, 100
            elif 2000 <= old_rank < 3000:
                return 300, 150
            elif 3000 <= old_rank < 4000:
                return 250, 200
            elif 4000 <= old_rank < 5000:
                return 200, 250
            elif 5000 <= old_rank < 5500:
                return 150, 300
            elif 5500 <= old_rank < 6000:
                return 100, 310
            elif 6000 <= old_rank < 7000:
                return 50, 340
            elif 7000 <= old_rank:
                return 10, 350
            else:
                return 500, 10  # Default values

        # Inside the rankrecord command, update the section where rank changes are calculated
        rank_changes = {}
        for player in winner_team:
            old_rank = database[str(player.id)][game_mode.value]['rank']
            k, _ = determine_k_l(old_rank)  # Determine k based on old_rank
            rank_gain = k * z * r
            rank_gain = max(0.1, min(rank_gain,
                                     864))  # Limit rank gain between 1 and 564
            rank_changes[str(player.id)] = round(rank_gain, 2)
        for player in loser_team:
            old_rank = database[str(player.id)][game_mode.value]['rank']
            _, L = determine_k_l(old_rank)  # Determine L based on old_rank
            rank_loss = L * z * r
            rank_loss = max(1, min(rank_loss,
                                   364))  # Limit rank loss between 5 and 300
            rank_changes[str(player.id)] = round(
                rank_loss, 2)  # Round off and store as positive

        # Calculate and display win rates
        total_winner_rank = sum(
            database[str(player.id)][game_mode.value]['rank']
            for player in winner_team)
        total_loser_rank = sum(
            database[str(player.id)][game_mode.value]['rank']
            for player in loser_team)

        combined_rank = total_winner_rank + total_loser_rank
        team_win_rate = (total_winner_rank / combined_rank *
                         100) if combined_rank > 0 else 0
        army_win_rate = (total_rnk2 / (total_rnk2 + total_rnk1) *
                         100) if (total_rnk1 + total_rnk2) > 0 else 0
        combined_win_rate = (team_win_rate + army_win_rate) / 2

        # Display rank changes
        message = f"**Match Results - {game_mode.value.replace('_', ' ')}**\n"
        message += "```\n"
        message += "🟢Winning Team:🟢\n"
        for player in winner_team:
            message += f"{database[str(player.id)]['nickname']}: {round(database[str(player.id)][game_mode.value]['rank'])} (+{rank_changes[str(player.id)]:.2f}🔼)\n"
        message += "\n🔴Losing Team:🔴\n"
        for player in loser_team:
            message += f"{database[str(player.id)]['nickname']}: {round(database[str(player.id)][game_mode.value]['rank'])} (-{rank_changes[str(player.id)]:.2f}🔽)\n"
        message += f"\n"
        message += f"Team Win Rate: {team_win_rate:.2f}% :إحتمالية فوز الفريق\n"
        message += f"Army Win Rate: {army_win_rate:.2f}% :إحتمالية فوز الجيوش\n"
        message += f"Combined Win Rate: {combined_win_rate:.2f}% :إحتمالية الفوز\n"
        message += "```\n"

        # Mention all players
        mentions = " ".join(player.mention for player in all_players)
        msg = await interaction.followup.send(f"{message}\n{mentions}")

        # React with approval emoji
        await msg.add_reaction("✅")

        # Ensure log database is loaded
        global log_database
        if not log_database:
            log_database = await load_json(log_database_path, {})

        # Use msg.id to save the message id
        log_message_id = msg.id

        # Save match results to log_database
        log_entry = {
            "message_id": log_message_id,
            "message_time": datetime.utcnow().isoformat(),
            "status": "non-active",  # Changed from 'state' to 'status'
            "channel_id": interaction.channel_id,  # Add the channel ID
            "winners": {
                str(winner1.id): {
                    "rank_gain": rank_changes[str(winner1.id)],
                    "army": winner_army1.value
                },
                str(winner2.id): {
                    "rank_gain": rank_changes[str(winner2.id)],
                    "army": winner_army2.value
                },
                str(winner3.id): {
                    "rank_gain": rank_changes[str(winner3.id)],
                    "army": winner_army3.value
                }
            },
            "losers": {
                str(loser1.id): {
                    "rank_loss": rank_changes[str(loser1.id)],
                    "army": loser_army1.value
                },
                str(loser2.id): {
                    "rank_loss": rank_changes[str(loser2.id)],
                    "army": loser_army2.value
                },
                str(loser3.id): {
                    "rank_loss": rank_changes[str(loser3.id)],
                    "army": loser_army3.value
                }
            },
            "game_mode": game_mode.value
        }
        log_database[str(log_message_id)] = log_entry  # Store as string
        await save_log_database()

    except Exception as e:
        logging.error(f"Error in rankrecord command: {e}")
        await interaction.followup.send(f"An error occurred: {e}")


# Event to handle reactions
@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    message_id = reaction.message.id
    logging.info(
        f"Reaction added by {user.name} (ID: {user.id}) on message {message_id} with emoji {reaction.emoji}"
    )

    if str(message_id) not in log_database:
        logging.info("Message ID not found in log database.")
        return

    log_entry = log_database[str(message_id)]

    if log_entry['status'] in ['Active', 'done']:
        logging.info("Log entry is already active or done.")
        return

    if reaction.emoji == "☑️":  # Handling admin approval emoji
        if is_user_admin(user):  # Check if the user is an admin
            logging.info(
                f"User {user.name} (ID: {user.id}) is an admin. Updating log entry status to Active."
            )
            log_entry['status'] = 'Active'
            logging.info(
                f"Log entry status before saving: {log_entry['status']}")
            await save_log_database()
            logging.info(
                f"Admin {user.name} set log entry for message {message_id} to Active."
            )
            await update_player_ranks()  # Call the new function
        else:
            logging.info(f"User {user.name} (ID: {user.id}) is not an admin.")
    elif reaction.emoji == "✅":  # Handling approval emoji
        loser_team_ids = list(log_entry['losers'].keys())
        logging.info(f"Loser team IDs: {loser_team_ids}")
        logging.info(
            f"User {user.name} ID: {user.id} reacted with approval emoji.")

        if user.id in [int(loser_team_ids[1]),
                       int(loser_team_ids[2])
                       ]:  # Check if user is loser2 or loser3
            logging.info(
                f"User {user.name} is in the loser team and reacted with approval emoji."
            )
            approval_reactions = [
                reaction for reaction in reaction.message.reactions
                if reaction.emoji == "✅"
            ]
            if len(approval_reactions) > 0:
                users_who_reacted = [
                    u async for u in approval_reactions[0].users()
                ]
                loser_approvals = [
                    u.id for u in users_who_reacted if u.id in
                    [int(loser_team_ids[1]),
                     int(loser_team_ids[2])]
                ]
                logging.info(f"Loser approvals: {loser_approvals}")
                if len(
                        loser_approvals
                ) >= 2:  # Check if at least two among loser2 or loser3 have reacted
                    log_database[str(message_id)]['status'] = 'Active'
                    logging.info(
                        f"Log entry status before saving: {log_database[str(message_id)]['status']}"
                    )
                    await save_log_database()
                    logging.info(
                        f"Log entry for message {message_id} set to Active.")
                    await update_player_ranks()  # Call the new function


# Save log database
async def save_log_database() -> None:
    try:
        await save_json('log_database.json', log_database)
        logging.info("Log database saved successfully.")
    except Exception as e:
        logging.error(f"Error saving log database: {e}")


# Load log database on startup
@bot.event
async def on_ready():
    global log_database
    log_database = await load_json('log_database.json', {})
    logging.info(f'Logged in as {bot.user}')


# Update player ranks function
async def update_player_ranks():
    rank_name_mapping = {
        ('3V3_GAME', 0, 500): "📥new_3V3📥",
        ('3V3_GAME', 500, 1000): "🍼noob_3V3🍼",
        ('3V3_GAME', 1000, 2000): "🔸AMATEUR_3V3🔸",
        ('3V3_GAME', 2000, 3000): "🔹MEDIUM_3V3🔹",
        ('3V3_GAME', 3000, 4000): "🥉SEMI-PRO_3V3🥉",
        ('3V3_GAME', 4000, 5000): "🥈PRO_3V3🥈",
        ('3V3_GAME', 5000, 5500): "🥇HIGH-PRO_3V3🥇",
        ('3V3_GAME', 5500, 6000): "🏆EXPERT_3V3🏆",
        ('AIR_GAME', 0, 500): "📥new_AIR📥",
        ('AIR_GAME', 500, 1000): "🍼noob_AIR🍼",
        ('AIR_GAME', 1000, 2000): "🔸AMATEUR_AIR🔸",
        ('AIR_GAME', 2000, 3000): "🔹MEDIUM_AIR🔹",
        ('AIR_GAME', 3000, 4000): "🥉SEMI-PRO_AIR🥉",
        ('AIR_GAME', 4000, 5000): "🥈PRO_AIR🥈",
        ('AIR_GAME', 5000, 5500): "🥇HIGH-PRO_AIR🥇",
        ('AIR_GAME', 5500, 6000): "🏆EXPERT_AIR🏆"
    }

    for message_id, log_entry in log_database.items():
        if log_entry['status'] == 'Active':
            winners = log_entry['winners']
            losers = log_entry['losers']
            game_mode = log_entry['game_mode']

            # Variables to store team and army win rates
            total_winner_rank = total_loser_rank = 0

            # Process winners
            for winner_id, winner_data in winners.items():
                player_data = database[winner_id][game_mode]
                old_rank = player_data['rank']
                rank_gain = winner_data['rank_gain']
                new_rank = old_rank + rank_gain
                player_data['rank'] = new_rank
                player_data['wins'] += 1
                player_data['win_rate'] = round(
                    (player_data['wins'] /
                     (player_data['wins'] + player_data['losses'])) * 100, 2)

                for (mode, lower,
                     upper), rank_name in rank_name_mapping.items():
                    if mode == game_mode and lower <= new_rank < upper:
                        player_data['rank_name'] = rank_name
                        break

                total_winner_rank += new_rank

            # Process losers
            for loser_id, loser_data in losers.items():
                player_data = database[loser_id][game_mode]
                old_rank = player_data['rank']
                rank_loss = loser_data['rank_loss']
                new_rank = old_rank - rank_loss
                player_data['rank'] = new_rank
                player_data['losses'] += 1
                player_data['win_rate'] = round(
                    (player_data['wins'] /
                     (player_data['wins'] + player_data['losses'])) * 100, 2)

                for (mode, lower,
                     upper), rank_name in rank_name_mapping.items():
                    if mode == game_mode and lower <= new_rank < upper:
                        player_data['rank_name'] = rank_name
                        break

                total_loser_rank += new_rank

            # Calculate win rates
            combined_rank = total_winner_rank + total_loser_rank
            team_win_rate = (total_winner_rank / combined_rank *
                             100) if combined_rank > 0 else 0

            # Change log entry status to 'done'
            log_entry['status'] = 'done'

            # Send confirmation message
            confirmation_message = "**Rank Update Confirmation**\n"
            confirmation_message += "```\n"
            confirmation_message += "Winners:\n"
            for winner_id, winner_data in winners.items():
                player_data = database[winner_id][game_mode]
                old_rank = int(player_data['rank'] - winner_data['rank_gain'])
                new_rank = int(player_data['rank'])
                rank_gain = int(winner_data['rank_gain'])
                confirmation_message += f"{database[winner_id]['nickname']}: Old Rank: {old_rank}, Rank Gain: +{rank_gain}, New Rank: {new_rank} ({player_data['rank_name']})\n"
            confirmation_message += "\nLosers:\n"
            for loser_id, loser_data in losers.items():
                player_data = database[loser_id][game_mode]
                old_rank = int(player_data['rank'] + loser_data['rank_loss'])
                new_rank = int(player_data['rank'])
                rank_loss = int(loser_data['rank_loss'])
                confirmation_message += f"{database[loser_id]['nickname']}: Old Rank: {old_rank}, Rank Loss: {rank_loss}, New Rank: {new_rank} ({player_data['rank_name']})\n"
            confirmation_message += "\n"
            confirmation_message += f"Team Win Rate: {int(team_win_rate)}%\n"
            confirmation_message += "```\n"

            channel = bot.get_channel(
                log_entry['channel_id']
            )  # Use the channel_id from the log entry
            await channel.send(confirmation_message)
            # Assign roles to updated players
            updated_player_ids = list(winners.keys()) + list(losers.keys())
            await assign_roles(channel.guild, updated_player_ids)

    await save_log_database()
    await save_json('database.json', database)


# Command for users to change their nickname
@bot.tree.command(name="edit_nickname", description="Change your nickname.")
@app_commands.describe(new_nickname="Your new nickname")
async def edit_nickname(interaction: Interaction, new_nickname: str):
    if not await check_banned(interaction):
        return

    user_id = str(interaction.user.id)
    if user_id not in database:
        await interaction.response.send_message("You are not registered.")
        return
    if any(player['nickname'] == new_nickname for player in database.values()):
        await interaction.response.send_message(
            "This nickname is already in use.")
        return
    if len(new_nickname) > 12:
        await interaction.response.send_message(
            "Nickname exceeds 12 characters.")
        return

    database[user_id]['nickname'] = new_nickname
    await save_database()
    await interaction.response.send_message(
        "Your nickname has been changed successfully.")


# Command to display player stats
@bot.tree.command(name="player_stats",
                  description="Display player stats by mentioning the player.")
@app_commands.describe(user="The user to display stats for")
async def player_stats(interaction: Interaction, user: discord.User):
    if not await check_banned(interaction):
        return
    user_id = str(user.id)

    if user_id not in database:
        await interaction.response.send_message(
            "Player not found in the database. Please ensure the user is registered."
        )
        return

    player_data = database[user_id]
    stats_message = (
        f"**Player Stats for {player_data['player_name']}**\n"
        f"{'-'*50}\n"
        f"**Nickname:** {player_data['nickname']}\n"
        f"**Clan:** {player_data['clan']}\n"
        f"**Status:** {'Banned' if player_data['banned'] else 'Active'}\n"
        f"\n**3V3 Game Stats**\n"
        f"{'Rank:':<15} {player_data['3V3_GAME']['rank']} ({player_data['3V3_GAME']['rank_name']})\n"
        f"{'Wins:':<15} {player_data['3V3_GAME']['wins']}\n"
        f"{'Losses:':<15} {player_data['3V3_GAME']['losses']}\n"
        f"{'Win Rate:':<15} {player_data['3V3_GAME']['win_rate']:.2f}%\n"
        f"\n**Air Game Stats**\n"
        f"{'Rank:':<15} {player_data['AIR_GAME']['rank']} ({player_data['AIR_GAME']['rank_name']})\n"
        f"{'Wins:':<15} {player_data['AIR_GAME']['wins']}\n"
        f"{'Losses:':<15} {player_data['AIR_GAME']['losses']}\n"
        f"{'Win Rate:':<15} {player_data['AIR_GAME']['win_rate']:.2f}%\n")

    await interaction.response.send_message(f"```{stats_message}```")


# Top rank command
GAME_MODES = [
    app_commands.Choice(name='3V3_GAME', value='3V3_GAME'),
    app_commands.Choice(name='AIR_GAME', value='AIR_GAME')
]


@bot.tree.command(name="toprank",
                  description="Display the top-ranked players.")
@app_commands.describe(game_mode="Select a game mode: 3V3_GAME or AIR_GAME")
@app_commands.choices(game_mode=GAME_MODES)
async def toprank(interaction: Interaction, game_mode: str):
    if not await check_banned(interaction):
        return
    try:
        # Filter out banned players and sort the remaining players by rank in the specified game mode
        sorted_players = sorted(
            [player for player in database.values() if not player['banned']],
            key=lambda x: x[game_mode]['rank'],
            reverse=True)

        # Format the response message
        top_rank_message = f"**Top Players in {game_mode.replace('_', ' ')}**\n"
        top_rank_message += f"{'Rank':<5} {'Player':<15} {'Rank Value':<10} {'Rank Name':<20} {'Win Rate':<10}\n"
        top_rank_message += "-" * 70 + "\n"

        for i, stats in enumerate(sorted_players[:100], 1):  # Top 100 players
            nickname = stats['nickname']
            fst_rank = str(sorted_players[0][game_mode]['rank'])

            if i == 1:
                nickname = '🏆' + nickname
            elif i == 2:
                nickname = '🥈'+ nickname
            elif i == 3:
                nickname = '🥉'+ nickname
            else:
                nickname = '⬛'+ nickname
            rank = int(stats[game_mode]['rank'])
            rank_nice = f"{str(rank):>{len(fst_rank)}}"
            rank_name = stats[game_mode]['rank_name']
            win_rate = f"{stats[game_mode]['win_rate']:.2f}%"
            top_rank_message += f"{i:<5} {nickname:<15} {rank_nice:<10} {rank_name:<20} {win_rate:<10}\n"

        await interaction.response.send_message(f"```{top_rank_message}```")
    except Exception as e:
        logging.error(f"Error in toprank command: {e}")
        await interaction.response.send_message(
            "An unexpected error occurred while retrieving the top-ranked players. Please try again later."
        )


# Command for players to sign in to an event
@bot.tree.command(name="event_sign_in",
                  description="Sign in to an available event.")
@app_commands.autocomplete(event=event_autocomplete)
async def event_sign_in(interaction: Interaction, event: str):
    if not await check_banned(interaction):
        return
    user_id = str(interaction.user.id)
    if user_id not in database:
        await interaction.response.send_message("You are not registered.")
        return
    if event not in events_database:
        await interaction.response.send_message("Event not found.")
        return
    game_mode = events_database[event]["game_mode"]
    player_rank = database[user_id][f"{game_mode}"]['rank']
    if not (events_database[event]['min_rank'] <= player_rank <=
            events_database[event]['max_rank']):
        await interaction.response.send_message(
            "You do not meet the rank requirements for this event.")
        return
    if user_id in events_database[event]["participants"]:
        await interaction.response.send_message(
            "You are already signed in to this event.")
        return
    events_database[event]["participants"].append(user_id)
    await save_events_database()
    await interaction.response.send_message(
        f"You have successfully signed in to the event '{event}'.")


# Command for players to sign out of an event
@bot.tree.command(name="sign_out", description="Sign out of an event.")
@app_commands.autocomplete(event=event_autocomplete)
async def sign_out(interaction: Interaction, event: str):
    if not await check_banned(interaction):
        return
    user_id = str(interaction.user.id)
    if user_id not in database:
        await interaction.response.send_message("You are not registered.")
        return
    if event not in events_database:
        await interaction.response.send_message("Event not found.")
        return
    if user_id not in events_database[event]["participants"]:
        await interaction.response.send_message(
            "You are not signed in to this event.")
        return
    events_database[event]["participants"].remove(user_id)
    await save_events_database()
    await interaction.response.send_message(
        f"You have successfully signed out of the event '{event}'.")


# Command to view the list of available events
@bot.tree.command(name="view_event_names",
                  description="View the list of available events.")
async def view_event_names(interaction: Interaction):
    if not await check_banned(interaction):
        return
    if not events_database:
        await interaction.response.send_message(
            "There are no available events.")
        return
    event_list = "Available events:\n"
    for event_name, event_details in events_database.items():
        event_list += (
            f"Event: {event_name}\n"
            f"  Game Mode: {event_details['game_mode']}\n"
            f"  Rank Range: {event_details['min_rank']} - {event_details['max_rank']}\n\n"
        )
    await interaction.response.send_message(f"```{event_list}```")


# Command to view the list of participants in an event
@bot.tree.command(name="view_event_participants",
                  description="View the list of participants in an event.")
@app_commands.autocomplete(event=event_autocomplete)
async def view_event_participants(interaction: Interaction, event: str):
    if not await check_banned(interaction):
        return
    if event not in events_database:
        await interaction.response.send_message("Event not found.")
        return
    if not events_database[event]["participants"]:
        await interaction.response.send_message(
            f"No participants in the event '{event}'.")
        return
    game_mode = events_database[event]["game_mode"]
    sorted_participants = sorted(
        events_database[event]["participants"],
        key=lambda uid: database[uid][f"{game_mode}"]['rank'],
        reverse=True)
    participants = [
        f"{database[uid]['nickname']} (Rank: {database[uid][f'{game_mode}']['rank']})"
        for uid in sorted_participants
    ]
    participants_list = f"Participants in '{event}':\n" + "\n".join(
        participants)
    await interaction.response.send_message(f"```{participants_list}```")


# Command to list all clans with player count and rank statistics
@bot.tree.command(
    name="list_clans",
    description=
    "List all available clans with player count and rank statistics.")
async def list_clans(interaction: Interaction):
    if not await check_banned(interaction):
        return
    if not clans_database:
        await interaction.response.send_message("No clans available.")
        return

    clans_list = "**Available Clans:**\n"
    for clan, members in clans_database.items():
        if members:
            total_rank = sum(database[uid]["3V3_GAME"]["rank"] +
                             database[uid]["AIR_GAME"]["rank"]
                             for uid in members)
            average_rank = total_rank / (2 * len(members)
                                         )  # Considering both game modes
        else:
            total_rank = 0
            average_rank = 0

        clans_list += (f"Clan: {clan}\n"
                       f"  Number of Players: {len(members)}\n"
                       f"  Total Rank: {round(total_rank)}\n"
                       f"  Average Rank: {round(average_rank):.2f}\n\n")

    await interaction.response.send_message(f"```{clans_list}```")


#make tram


def calculate_balance_score(teams):
    """
    Calculate the balance score for the teams. The score is calculated
    based on the difference in total ranks between teams.

    Args:
        teams (list): List of teams, where each team is a list of (user_id, rank) tuples.

    Returns:
        int: The calculated balance score.
    """
    # Calculate the total rank for each team
    team_totals = [sum(player[1] for player in team) for team in teams]

    # Calculate the max and min total ranks
    max_total = max(team_totals)
    min_total = min(team_totals)

    # The balance score is the difference between the max and min total ranks
    score = max_total - min_total

    return score


@bot.tree.command(
    name="maketeams",
    description="Create balanced teams based on player mentions.")
@app_commands.describe(players="List of mentioned players (use @)",
                       game_mode="Select a game mode: 3V3_GAME or AIR_GAME")
@app_commands.choices(game_mode=GAME_MODES)
async def maketeams(interaction: Interaction, players: str,
                    game_mode: app_commands.Choice[str]):
    if not await check_banned(interaction):
        return

    # Extract mentioned user IDs from the provided list of players
    mentioned_users = players.split()
    if interaction.guild is None:
        await interaction.response.send_message(
            "This command can only be used in a server.")
        return
    mentioned_user_ids = {
        user.id: user
        for user in interaction.guild.members
        if user.mention in mentioned_users
    }

    # Filter unique player IDs
    unique_player_ids = list(set(mentioned_user_ids.keys()))

    # Validate player existence in the database
    non_existing_players = []
    existing_player_ids = []
    for user_id in unique_player_ids:
        if str(user_id) in database:
            existing_player_ids.append(user_id)
        else:
            non_existing_players.append(mentioned_user_ids[user_id].name)

    # Check if there are enough players to form teams
    if len(existing_player_ids) < 6:
        await interaction.response.send_message(
            "Not enough players to start a match. At least 6 players are required."
        )
        return

    # Determine players who will not play to make the list divisible by 3
    not_playing = []
    while len(existing_player_ids) % 3 != 0:
        not_playing.append(
            existing_player_ids.pop(
                random.randint(0,
                               len(existing_player_ids) - 1)))

    # Get ranks of remaining participants
    player_ranks = [(str(uid),
                     database[str(uid)][f"{game_mode.value}"]['rank'])
                    for uid in existing_player_ids]

    # Number of teams
    num_teams = len(player_ranks) // 3

    # Initialize best teams and best score
    best_teams = None
    best_score = float('inf')

    # Perform multiple iterations to find the best balanced teams
    for _ in range(1000):  # Number of iterations
        # Shuffle the players to ensure randomness
        random.shuffle(player_ranks)

        # Initialize teams
        teams = [player_ranks[i * 3:(i + 1) * 3] for i in range(num_teams)]

        # Calculate the balance score for the current teams
        score = calculate_balance_score(teams)

        # Update best teams if current teams are better balanced
        if score < best_score:
            best_teams = teams
            best_score = score

    # Calculate team details for the best teams
    if best_teams is not None:  # Check if best teams were found
        team_details = []
        for team in best_teams:
            total_rank = sum(player[1] for player in team)
            average_rank = total_rank / len(team)
            team_info = {
                "members": [database[uid]["nickname"] for uid, _ in team],
                "total_rank": total_rank,
                "average_rank": average_rank
            }
            team_details.append(team_info)
    else:
        # Handle the case where no balanced teams were found
        await interaction.response.send_message(
            f"Unable to find balanced teams for the given players.")
        return

    # Create a response message with team details
    team_message = f"**Balanced Teams for Game Mode '{game_mode.value}'**\n"
    for i, team in enumerate(team_details, 1):
        team_message += f"Team {i}:\n"
        team_message += f"  Members: {', '.join(team['members'])}\n"
        team_message += f"  Total Rank: {round(team['total_rank'])}\n"
        team_message += f"  Average Rank: {round(team['average_rank']):.2f}\n\n"

    if not_playing:
        team_message += f"**Players not playing:**\n{', '.join([database[str(uid)]['nickname'] for uid in not_playing])}\n"

    if non_existing_players:
        team_message += f"**Players not in database:**\n{', '.join(non_existing_players)}\n"

    await interaction.response.send_message(f"```{team_message}```")


# New version of maketeams that takes all players in a voice channel as input
@bot.tree.command(
    name="maketeams_voice",
    description="Create balanced teams from users in the voice channel.")
@app_commands.describe(game_mode="Select a game mode: 3V3_GAME or AIR_GAME")
@app_commands.choices(game_mode=GAME_MODES)
async def maketeams_voice(interaction: Interaction,
                          game_mode: app_commands.Choice[str]):
    if not await check_banned(interaction):
        return

    voice_channel = interaction.user.voice.channel if interaction.user.voice else None
    if not voice_channel:
        await interaction.response.send_message(
            "You are not in a voice channel.")
        return

    mentioned_user_ids = [member.id for member in voice_channel.members]

    # Filter unique player IDs
    unique_player_ids = list(set(mentioned_user_ids))

    # Validate player existence in the database
    non_existing_players = []
    existing_player_ids = []
    for user_id in unique_player_ids:
        if str(user_id) in database:
            existing_player_ids.append(user_id)
        else:
            non_existing_players.append(bot.get_user(user_id).name)

    # Check if there are enough players to form teams
    if len(existing_player_ids) < 6:
        await interaction.response.send_message(
            "Not enough players to start a match. At least 6 players are required."
        )
        return

    # Determine players who will not play to make the list divisible by 3
    not_playing = []
    while len(existing_player_ids) % 3 != 0:
        not_playing.append(
            existing_player_ids.pop(
                random.randint(0,
                               len(existing_player_ids) - 1)))

    # Get ranks of remaining participants
    player_ranks = [(str(uid),
                     database[str(uid)][f"{game_mode.value}"]['rank'])
                    for uid in existing_player_ids]

    # Number of teams
    num_teams = len(player_ranks) // 3

    # Initialize best teams and best score
    best_teams = None
    best_score = float('inf')

    # Perform multiple iterations to find the best balanced teams
    for _ in range(1000):  # Number of iterations
        # Shuffle the players to ensure randomness
        random.shuffle(player_ranks)

        # Initialize teams
        teams = [player_ranks[i * 3:(i + 1) * 3] for i in range(num_teams)]

        # Calculate the balance score for the current teams
        score = calculate_balance_score(teams)

        # Update best teams if current teams are better balanced
        if score < best_score:
            best_teams = teams
            best_score = score

    # Calculate team details for the best teams
    if best_teams is not None:  # Check if best teams were found
        team_details = []
        for team in best_teams:
            total_rank = sum(player[1] for player in team)
            average_rank = total_rank / len(team)
            team_info = {
                "members": [database[uid]["nickname"] for uid, _ in team],
                "total_rank": total_rank,
                "average_rank": average_rank
            }
            team_details.append(team_info)
    else:
        # Handle the case where no balanced teams were found
        await interaction.response.send_message(
            f"Unable to find balanced teams for the given players.")
        return

    # Create a response message with team details
    team_message = f"**Balanced Teams for Game Mode '{game_mode.value}'**\n"
    for i, team in enumerate(team_details, 1):
        team_message += f"Team {i}:\n"
        team_message += f"  Members: {', '.join(team['members'])}\n"
        team_message += f"  Total Rank: {team['total_rank']}\n"
        team_message += f"  Average Rank: {team['average_rank']:.2f}\n\n"

    if not_playing:
        team_message += f"**Players not playing:**\n{', '.join([database[str(uid)]['nickname'] for uid in not_playing])}\n"

    if non_existing_players:
        team_message += f"**Players not in database:**\n{', '.join(non_existing_players)}\n"

    await interaction.response.send_message(f"```{team_message}```")


### Moderator Commands ###


# Command to add a clan member (moderator only)
@bot.tree.command(name="add_clan_member",
                  description="[MODERATOR] Add a member to a clan.")
@app_commands.describe(user="User to add to the clan",
                       new_clan="Choose the new clan from the list")
@app_commands.autocomplete(new_clan=clan_autocomplete)
async def add_clan_member(interaction: Interaction, user: discord.User,
                          new_clan: str):
    if not is_moderator(interaction):
        await interaction.response.send_message(
            "Permission denied: You do not have moderator permissions.")
        return
    user_id = str(user.id)
    if user_id not in database:
        await interaction.response.send_message("User is not registered.")
        return
    if new_clan not in clans_database:
        await interaction.response.send_message(
            "Invalid clan. Please select a valid clan.")
        return
    old_clan = database[user_id]["clan"]
    database[user_id]["clan"] = new_clan
    clans_database[old_clan].remove(user_id)
    clans_database[new_clan].append(user_id)
    await save_database()
    await save_clans_database()
    await interaction.response.send_message(
        f"User {user.name} has been added to the clan {new_clan}.")


### Admin Commands ###


# Command to ban or unban a player (admin only)
@bot.tree.command(name="ban_unban",
                  description="[ADMIN] Ban or unban a player.")
@app_commands.describe(user="User to ban or unban",
                       ban_status="Set ban status to True or False")
async def ban_unban(interaction: Interaction, user: discord.User,
                    ban_status: bool):
    if not is_admin(interaction):
        await interaction.response.send_message(
            "Permission denied: You do not have admin permissions.")
        return
    user_id = str(user.id)
    if user_id not in database:
        await interaction.response.send_message("User not found.")
        return
    database[user_id]['banned'] = ban_status
    await save_database()
    status = "banned" if ban_status else "unbanned"
    await interaction.response.send_message(
        f"User {user.name} has been {status} successfully.")


# Command to add new clans (admin only)
@bot.tree.command(name="addclan", description="[ADMIN] Add a new clan.")
@app_commands.describe(clan_name="The name of the new clan")
async def addclan(interaction: Interaction, clan_name: str):
    if not is_admin(interaction):
        await interaction.response.send_message(
            "Permission denied: You do not have admin permissions.")
        return
    if clan_name in clans_database:
        await interaction.response.send_message("Clan already exists.")
        return
    clans_database[clan_name] = []
    await save_clans_database()
    await interaction.response.send_message(
        f"Clan '{clan_name}' has been added successfully.")


# Command to register a new player (admin only)
@bot.tree.command(name="admin_register",
                  description="[ADMIN] Register a new player.")
@app_commands.describe(user="User to register",
                       nickname="User's nickname",
                       clan="User's clan")
@app_commands.autocomplete(clan=clan_autocomplete)
async def admin_register(interaction: Interaction, user: discord.User,
                         nickname: str, clan: str):
    try:
        if not is_admin(interaction):
            await interaction.response.send_message(
                "Permission denied: You do not have admin permissions.")
            return

        user_id = str(user.id)
        if user_id in database:
            await interaction.response.send_message(
                "User is already registered.")
            return
        if any(player['nickname'] == nickname for player in database.values()):
            await interaction.response.send_message(
                "This nickname is already in use.")
            return
        if len(nickname) > 12:
            await interaction.response.send_message(
                "Nickname exceeds 12 characters.")
            return
        if clan not in clans_database:
            await interaction.response.send_message(
                "Invalid clan. Please select a valid clan or add a new clan first."
            )
            return

        player_info = {
            "player_name": user.name,
            "nickname": nickname,
            "discord_id": user.id,
            "clan": clan,
            "banned": False,
            "3V3_GAME": {
                "rank": 490,
                "rank_name": determine_rank_name('3V3_GAME', 490),
                "wins": 0,
                "losses": 0,
                "win_rate": 0.0
            },
            "AIR_GAME": {
                "rank": 490,
                "rank_name": determine_rank_name('AIR_GAME', 490),
                "wins": 0,
                "losses": 0,
                "win_rate": 0.0
            }
        }

        database[user_id] = player_info
        clans_database[clan].append(user_id)
        await save_database()
        await save_clans_database()
        await interaction.response.send_message(
            f"{user.name} has been registered successfully.")
        await assign_roles(interaction.guild, [user.id])

    except NotAdmin as e:
        await interaction.response.send_message(str(e), ephemeral=True)
    except Exception as e:
        logging.error(f"Error in admin_register command: {e}")
        await interaction.response.send_message(
            f"An unexpected error occurred: {e}", ephemeral=True)


# Command to create a new event (admin only)
@bot.tree.command(name="new_event", description="[ADMIN] Create a new event.")
@app_commands.describe(name="Name of the event",
                       min_rank="Minimum rank points",
                       max_rank="Maximum rank points",
                       game_mode="Game mode (3V3_GAME or AIR_GAME)")
@app_commands.choices(game_mode=GAME_MODES)
async def new_event(interaction: Interaction, name: str, min_rank: int,
                    max_rank: int, game_mode: app_commands.Choice[str]):
    if not is_admin(interaction):
        await interaction.response.send_message(
            "Permission denied: You do not have admin permissions.")
        return
    if name in events_database:
        await interaction.response.send_message(
            "Event with this name already exists.")
        return
    events_database[name] = {
        "min_rank": min_rank,
        "max_rank": max_rank,
        "game_mode": game_mode.value,
        "participants": []
    }
    await save_events_database()
    await interaction.response.send_message(
        f"Event '{name}' has been created successfully.")


# Command to delete a player from an event (admin only)
@bot.tree.command(name="delete_player",
                  description="[ADMIN] Delete a player from an event.")
@app_commands.describe(user="The user to delete from the event")
@app_commands.autocomplete(event=event_autocomplete)
async def delete_player(interaction: Interaction, user: discord.User,
                        event: str):
    if not is_admin(interaction):
        await interaction.response.send_message(
            "Permission denied: You do not have admin permissions.")
        return
    if event not in events_database:
        await interaction.response.send_message("Event not found.")
        return
    user_id = str(user.id)
    if user_id not in events_database[event]["participants"]:
        await interaction.response.send_message(
            "User is not signed in to this event.")
        return
    events_database[event]["participants"].remove(user_id)
    await save_events_database()
    await interaction.response.send_message(
        f"User {user.name} has been deleted from the event '{event}'.")


# Command for admin to sign in a player to an event (admin only)
@bot.tree.command(name="admin_sign_event",
                  description="[ADMIN] Sign in a player to an event.")
@app_commands.describe(user="User to sign in to the event")
@app_commands.autocomplete(event=event_autocomplete)
async def admin_sign_event(interaction: Interaction, user: discord.User,
                           event: str):
    if not is_admin(interaction):
        await interaction.response.send_message(
            "Permission denied: You do not have admin permissions.")
        return
    user_id = str(user.id)
    if user_id not in database:
        await interaction.response.send_message("User is not registered.")
        return
    if event not in events_database:
        await interaction.response.send_message("Event not found.")
        return
    game_mode = events_database[event]["game_mode"]
    player_rank = database[user_id][f"{game_mode}"]['rank']
    if not (events_database[event]['min_rank'] <= player_rank <=
            events_database[event]['max_rank']):
        await interaction.response.send_message(
            "Player does not meet the rank requirements for this event.")
        return
    if user_id in events_database[event]["participants"]:
        await interaction.response.send_message(
            "Player is already signed in to this event.")
        return
    events_database[event]["participants"].append(user_id)
    await save_events_database()
    await interaction.response.send_message(
        f"{user.name} has been successfully signed in to the event '{event}'.")


# Command to start an event (admin only)
@bot.tree.command(name="start_event", description="[ADMIN] Start an event.")
@app_commands.autocomplete(event=event_autocomplete)
async def start_event(interaction: Interaction, event: str):
    if not is_admin(interaction):
        await interaction.response.send_message(
            "Permission denied: You do not have admin permissions.")
        return
    if event not in events_database:
        await interaction.response.send_message("Event not found.")
        return
    participants = events_database[event]["participants"]
    if len(participants) < 3:
        await interaction.response.send_message(
            "Not enough participants to start the event.")
        return

    # Sort participants by the order they signed in (ascending)
    sorted_participants = participants

    # Select participants to not play (if not divisible by 3)
    not_playing = []
    while len(sorted_participants) % 3 != 0:
        not_playing.append(sorted_participants.pop())

    # Get ranks of remaining participants
    player_ranks = [
        (uid, database[uid][f"{events_database[event]['game_mode']}"]['rank'])
        for uid in sorted_participants
    ]

    # Number of teams
    num_teams = len(player_ranks) // 3

    # Initialize best teams and best score
    best_teams = None
    best_score = float('inf')

    # Perform multiple iterations to find the best balanced teams
    for _ in range(1000):  # Number of iterations
        # Shuffle the players to ensure randomness
        random.shuffle(player_ranks)

        # Initialize teams
        teams = [player_ranks[i * 3:(i + 1) * 3] for i in range(num_teams)]

        # Calculate the balance score for the current teams
        score = calculate_balance_score(teams)

        # Update best teams if current teams are better balanced
        if score < best_score:
            best_teams = teams
            best_score = score

    # Calculate team details for the best teams
    team_details = []
    for team in best_teams:
        total_rank = sum(player[1] for player in team)
        average_rank = total_rank / len(team)
        team_info = {
            "members": [database[uid]["nickname"] for uid, _ in team],
            "total_rank": total_rank,
            "average_rank": average_rank
        }
        team_details.append(team_info)

    # Create a response message with team details
    team_message = f"**Teams for Event '{event}'**\n"
    for i, team in enumerate(team_details, 1):
        team_message += f"Team {i}:\n"
        team_message += f"  Members: {', '.join(team['members'])}\n"
        team_message += f"  Total Rank: {team['total_rank']}\n"
        team_message += f"  Average Rank: {team['average_rank']:.2f}\n\n"
    if not_playing:
        team_message += f"**Players not playing:**\n{', '.join([database[uid]['nickname'] for uid in not_playing])}\n"

    await interaction.response.send_message(f"```{team_message}```")


### Developer Commands ###


# Command to edit a clan name (developer only)
@bot.tree.command(name="edit_clan",
                  description="[DEVELOPER] Edit a clan name.")
@app_commands.describe(clan_name="The current name of the clan",
                       new_clan_name="The new name of the clan")
@app_commands.autocomplete(clan_name=clan_autocomplete)
async def edit_clan(interaction: Interaction, clan_name: str,
                    new_clan_name: str):
    if not is_developer(interaction):
        await interaction.response.send_message(
            "Permission denied: You do not have developer permissions.")
        return
    if clan_name not in clans_database:
        await interaction.response.send_message("Clan not found.")
        return
    if new_clan_name in clans_database:
        await interaction.response.send_message("New clan name already exists."
                                                )
        return
    clans_database[new_clan_name] = clans_database.pop(clan_name)
    for user_id in database:
        if database[user_id]['clan'] == clan_name:
            database[user_id]['clan'] = new_clan_name
    await save_clans_database()
    await save_database()
    await interaction.response.send_message(
        f"Clan '{clan_name}' has been renamed to '{new_clan_name}' successfully."
    )


# Command to delete a clan (developer only)
@bot.tree.command(name="delete_clan", description="[DEVELOPER] Delete a clan.")
@app_commands.describe(clan_name="The name of the clan to delete")
@app_commands.autocomplete(clan_name=clan_autocomplete)
async def delete_clan(interaction: Interaction, clan_name: str):
    if not is_developer(interaction):
        await interaction.response.send_message(
            "Permission denied: You do not have developer permissions.")
        return

    if clan_name not in clans_database:
        await interaction.response.send_message("Clan not found.")
        return

    if clan_name == "😢NO CLAN😢":
        await interaction.response.send_message(
            "You cannot delete the '😢NO CLAN😢' clan.")
        return

    # Move players to "😢NO CLAN😢" if the clan has players
    if clan_name in clans_database and clans_database[clan_name]:
        if "😢NO CLAN😢" not in clans_database:
            clans_database["😢NO CLAN😢"] = []
        for user_id in clans_database[clan_name]:
            database[user_id]['clan'] = "😢NO CLAN😢"
            clans_database["😢NO CLAN😢"].append(user_id)

    del clans_database[clan_name]
    await save_clans_database()
    await save_database()
    await interaction.response.send_message(
        f"Clan '{clan_name}' has been deleted successfully.")


# Command to delete a user (developer only)
@bot.tree.command(name="delete",
                  description="[DEVELOPER] Delete a user from the database.")
@app_commands.describe(user="The user to delete from the database")
async def delete(interaction: Interaction, user: discord.User):
    try:
        is_developer(interaction)
    except NotDeveloper as e:
        await interaction.response.send_message(str(e), ephemeral=True)
        return

    try:
        user_id = str(user.id)
        if user_id in database:
            clan = database[user_id]["clan"]
            del database[user_id]
            if user_id in clans_database[clan]:
                clans_database[clan].remove(user_id)
            await save_database()
            await save_clans_database()
            await interaction.response.send_message(
                f"User {user.name} deleted successfully.")
        else:
            await interaction.response.send_message(
                "User not found in the database.")
    except Exception as e:
        logging.error(f"Error in delete command: {e}")
        await interaction.response.send_message(f"An error occurred: {e}")


# Command to delete the entire database (developer only)
@bot.tree.command(name="deletedatabase",
                  description="[DEVELOPER] Delete the entire database.")
@app_commands.describe(password="The developer password")
async def deletedatabase(interaction: Interaction, password: str):
    if not is_developer(interaction) or password != DEVELOPER_PASSWORD:
        await interaction.response.send_message(
            "Permission denied: You do not have developer permissions or incorrect password."
        )
        return
    try:
        database.clear()
        clans_database.clear()
        events_database.clear()
        await save_database()
        await save_clans_database()
        await save_events_database()
        await interaction.response.send_message(
            "Database cleared successfully.")
    except Exception as e:
        logging.error(f"Error in deletedatabase command: {e}")
        await interaction.response.send_message(f"An error occurred: {e}")


# Command to delete an event (developer only)
@bot.tree.command(name="delete_event",
                  description="[DEVELOPER] Delete an event.")
@app_commands.autocomplete(event=event_autocomplete)
async def delete_event(interaction: Interaction, event: str):
    if not is_developer(interaction):
        await interaction.response.send_message(
            "Permission denied: You do not have developer permissions.")
        return
    if event not in events_database:
        await interaction.response.send_message("Event not found.")
        return
    del events_database[event]
    await save_events_database()
    await interaction.response.send_message(
        f"Event '{event}' has been deleted successfully.")


# Command to make an announcement in all servers (developer only)
@bot.tree.command(
    name="announcement",
    description="[DEVELOPER] Make an announcement in all servers.")
@app_commands.describe(message="The message to announce")
async def announcement(interaction: Interaction, message: str):
    if not is_developer(interaction):
        await interaction.response.send_message(
            "Permission denied: You do not have developer permissions.")
        return

    # Defer the response to avoid interaction timeout
    await interaction.response.defer()

    # Announce the message in all text channels of all servers the bot is part of
    announcements_sent = 0
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                try:
                    await channel.send(message)
                    announcements_sent += 1
                except discord.Forbidden:
                    logging.error(
                        f"Failed to send message to channel {channel.name} in guild {guild.name}: Missing Permissions"
                    )
                except Exception as e:
                    logging.error(
                        f"Failed to send message to channel {channel.name} in guild {guild.name}: {e}"
                    )

    await interaction.followup.send(
        f"Announcement sent to {announcements_sent} channel(s).")


#Command for developer to create roles in the server
@bot.tree.command(name="create_roles",
                  description="[DEVELOPER] Create server roles.")
async def create_roles(interaction: Interaction):
    if not is_developer(interaction):
        await interaction.response.send_message(
            "Permission denied: You do not have developer permissions.")
        return

    roles = [
        "📥new_3V3📥", "🍼noob_3V3🍼", "🔸AMATEUR_3V3🔸", "🔹MEDIUM_3V3🔹",
        "🥉SEMI-PRO_3V3🥉", "🥈PRO_3V3🥈", "🥇HIGH-PRO_3V3🥇", "🏆EXPERT_3V3🏆",
        "📥new_AIR📥", "🍼noob_AIR🍼", "🔸AMATEUR_AIR🔸", "🔹MEDIUM_AIR🔹",
        "🥉SEMI-PRO_AIR🥉", "🥈PRO_AIR🥈", "🥇HIGH-PRO_AIR🥇", "🏆EXPERT_AIR🏆",
        "🚫banned🚫", "⚜️bot_admin⚜️", "⌨️bot_developer⌨️", "🛡️bot_moderator🛡️"
    ]
    guild = interaction.guild
    if guild is None:
        await interaction.response.send_message(
            "This command can only be used in a server.")
        return

    if not guild.me.guild_permissions.manage_roles:
        await interaction.response.send_message(
            "Permission denied: The bot does not have the 'Manage Roles' permission."
        )
        return
    try:
        # Defer the response to avoid interaction timeout
        await interaction.response.defer()

        created_roles = []
        for role_name in roles:
            existing_role = discord.utils.get(guild.roles, name=role_name)
            if not existing_role:
                try:
                    new_role = await guild.create_role(
                        name=role_name,
                        reason="Creating predefined game roles")
                    created_roles.append(new_role)
                except discord.Forbidden:
                    await interaction.followup.send(
                        "Permission denied: The bot does not have the 'Manage Roles' permission."
                    )
                    return
                except discord.HTTPException as e:
                    logging.error(
                        f"HTTPException while creating role {role_name}: {e}")
                    await interaction.followup.send(
                        f"Failed to create role {role_name} due to an HTTP error."
                    )
                    return
                except Exception as e:
                    logging.error(
                        f"Error while creating role {role_name}: {e}")
                    await interaction.followup.send(
                        f"Failed to create role {role_name} due to an unknown error."
                    )
                    return

        if created_roles:
            role_names = ', '.join([role.name for role in created_roles])
            await interaction.followup.send(
                f"Roles created successfully: {role_names}")
        else:
            await interaction.followup.send("All roles already exist.")
    except Exception as e:
        logging.error(f"Error in create_roles command: {e}")
        await interaction.followup.send(f"An error occurred: {e}")


# Function to assign roles to players
async def assign_roles(guild: discord.Guild, player_ids: list):
    """
    Assigns roles to players based on their database information.

    Args:
        guild: The Discord guild object.
        player_ids: A list of player IDs to assign roles to.
    """

    # Check if the bot has the required permissions
    if not guild.me.guild_permissions.manage_roles:
        logging.warning("The bot does not have the 'Manage Roles' permission.")
        return

    # Check if all required roles exist
    for role_name in BOT_ROLES:
        if not discord.utils.get(guild.roles, name=role_name):
            logging.warning(f"Role '{role_name}' not found in guild.")
            return

    # Filter players not in the database
    player_ids = [
        str(player_id) for player_id in player_ids
        if str(player_id) in database
    ]

    for player_id in player_ids:
        try:
            user = await guild.fetch_member(
                int(player_id))  # Use fetch_member instead of get_member
        except discord.NotFound:
            logging.warning(f"Player with ID {player_id} not found in guild.")
            continue
        except discord.Forbidden:
            logging.warning(
                f"Bot lacks permissions to fetch member with ID {player_id}.")
            continue
        except discord.HTTPException as e:
            if e.status == 429:
                logging.warning(
                    "Rate limited by Discord, sleeping for a bit...")
                await asyncio.sleep(5)  # Sleep for 5 seconds before retrying
                user = await guild.fetch_member(int(player_id)
                                                )  # Retry fetching the member
            else:
                logging.error(
                    f"HTTPException while fetching member with ID {player_id}: {e}"
                )
                continue

        player_data = database[player_id]

        # Remove all bot-managed roles except "banned"
        for role in user.roles:
            if role.name in BOT_ROLES and role.name != "🚫banned🚫":
                try:
                    await user.remove_roles(role,
                                            reason="Updating player roles.")
                except discord.Forbidden:
                    logging.warning(
                        f"Permission denied: Unable to remove role '{role.name}' from {user.mention}."
                    )
                except discord.HTTPException as e:
                    logging.error(
                        f"HTTPException while removing role '{role.name}' from {user.mention}: {e}"
                    )
                except Exception as e:
                    logging.error(
                        f"Error while removing role '{role.name}' from {user.mention}: {e}"
                    )

        # Assign roles based on ban status and rank
        if player_data['banned']:
            banned_role = discord.utils.get(guild.roles, name="🚫banned🚫")
            if banned_role:
                try:
                    await user.add_roles(banned_role,
                                         reason="Player is banned.")
                except discord.Forbidden:
                    logging.warning(
                        f"Permission denied: Unable to add role '{banned_role.name}' to {user.mention}."
                    )
                except discord.HTTPException as e:
                    logging.error(
                        f"HTTPException while adding role '{banned_role.name}' to {user.mention}: {e}"
                    )
                except Exception as e:
                    logging.error(
                        f"Error while adding role '{banned_role.name}' to {user.mention}: {e}"
                    )
        else:
            for game_mode in ['3V3_GAME', 'AIR_GAME']:
                rank = player_data[game_mode]['rank']
                for (mode, min_rank,
                     max_rank), role_name in rank_name_mapping.items():
                    if mode == game_mode and min_rank <= rank < max_rank:
                        role = discord.utils.get(guild.roles, name=role_name)
                        if role:
                            try:
                                await user.add_roles(
                                    role, reason="Updating player roles.")
                            except discord.Forbidden:
                                logging.warning(
                                    f"Permission denied: Unable to add role '{role.name}' to {user.mention}."
                                )
                            except discord.HTTPException as e:
                                logging.error(
                                    f"HTTPException while adding role '{role.name}' to {user.mention}: {e}"
                                )
                            except Exception as e:
                                logging.error(
                                    f"Error while adding role '{role.name}' to {user.mention}: {e}"
                                )

        # Assign admin, developer, or moderator role if applicable
        if int(player_id) in developer_ids:
            developer_role = discord.utils.get(guild.roles,
                                               name="⌨️bot_developer⌨️")
            if developer_role:
                try:
                    await user.add_roles(developer_role,
                                         reason="Player is a developer.")
                except discord.Forbidden:
                    logging.warning(
                        f"Permission denied: Unable to add role '{developer_role.name}' to {user.mention}."
                    )
                except discord.HTTPException as e:
                    logging.error(
                        f"HTTPException while adding role '{developer_role.name}' to {user.mention}: {e}"
                    )
                except Exception as e:
                    logging.error(
                        f"Error while adding role '{developer_role.name}' to {user.mention}: {e}"
                    )
        elif int(player_id) in admin_ids:
            admin_role = discord.utils.get(guild.roles, name="⚜️bot_admin⚜️")
            if admin_role:
                try:
                    await user.add_roles(admin_role,
                                         reason="Player is an admin.")
                except discord.Forbidden:
                    logging.warning(
                        f"Permission denied: Unable to add role '{admin_role.name}' to {user.mention}."
                    )
                except discord.HTTPException as e:
                    logging.error(
                        f"HTTPException while adding role '{admin_role.name}' to {user.mention}: {e}"
                    )
                except Exception as e:
                    logging.error(
                        f"Error while adding role '{admin_role.name}' to {user.mention}: {e}"
                    )
        elif int(player_id) in moderator_ids:
            moderator_role = discord.utils.get(guild.roles,
                                               name="🛡️bot_moderator🛡️")
            if moderator_role:
                try:
                    await user.add_roles(moderator_role,
                                         reason="Player is a moderator.")
                except discord.Forbidden:
                    logging.warning(
                        f"Permission denied: Unable to add role '{moderator_role.name}' to {user.mention}."
                    )
                except discord.HTTPException as e:
                    logging.error(
                        f"HTTPException while adding role '{moderator_role.name}' to {user.mention}: {e}"
                    )
                except Exception as e:
                    logging.error(
                        f"Error while adding role '{moderator_role.name}' to {user.mention}: {e}"
                    )


# Command to reset rank history (developer only)
@bot.tree.command(name="reset_rank_history",
                  description="[DEVELOPER] Reset rank history.")
@app_commands.describe(option="Choose to reset 'all' or 'done' history")
@app_commands.choices(option=RESET_CHOICES)
async def reset_rank_history(interaction: Interaction,
                             option: app_commands.Choice[str]):
    if not is_developer(interaction):
        await interaction.response.send_message(
            "Permission denied: You do not have developer permissions.")
        return

    global log_database

    if option.value == 'all':
        # Delete all entries in the log_database
        log_database.clear()
        await save_log_database()
        await interaction.response.send_message(
            "All rank history has been reset.")
        logging.info("All rank history has been reset by a developer.")
    elif option.value == 'done':
        # Delete only entries with log_entry['status'] = 'done'
        done_entries = [
            key for key, entry in log_database.items()
            if entry['status'] == 'done'
        ]
        for key in done_entries:
            del log_database[key]
        await save_log_database()
        await interaction.response.send_message(
            "Rank history with status 'done' has been reset.")
        logging.info(
            "Rank history with status 'done' has been reset by a developer.")
    else:
        await interaction.response.send_message("Invalid option selected.")


### Load databases on startup ###
@bot.event
async def on_ready():
    global database, clans_database, events_database, log_database
    database = await load_json(database_path, {})
    clans_database = await load_json(clans_path, {})
    events_database = await load_json(events_path, {})
    log_database = await load_json(log_database_path, {})
    logging.info(f'We have logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        logging.info(f'Synced {len(synced)} command(s)')
    except Exception as e:
        logging.error(f"Error syncing commands: {e}")


### Start bot ###
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
bot.run(TOKEN)
