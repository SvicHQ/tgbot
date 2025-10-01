import random

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import BadRequest

from app import bot, logger
from app.utils.database import DBConstants, MemoryDB
from app.utils.decorators.pm_only import pm_only
from app.utils.decorators.sudo_users import require_sudo


class BotSettingsData:
    TEXT = (
        "<blockquote>**Bot Settings**</blockquote>\n\n"
        "• Show Bot Photo: `{}`\n"
        "• Images: `{}`\n"
        "• Support chat: `{}`\n"
        "• Server url: `{}`\n"
        "• Sudo: `{}`\n"
        "• Shrinkme API: `{}`\n"
        "• OMDB API: `{}`\n"
        "• Weather API: `{}`"
    )

    BUTTONS = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Show Bot Photo", "bsettings_show_bot_pic"),
            InlineKeyboardButton("Images", "bsettings_images")
        ],
        [
            InlineKeyboardButton("Support Chat", "bsettings_support_chat"),
            InlineKeyboardButton("Server URL", "bsettings_server_url")
        ],
        [
            InlineKeyboardButton("Sudo", "bsettings_sudo"),
            InlineKeyboardButton("Shrinkme API", "bsettings_shrinkme_api")
        ],
        [
            InlineKeyboardButton("OMDB API", "bsettings_omdb_api"),
            InlineKeyboardButton("Weather API", "bsettings_weather_api")
        ],
        [
            InlineKeyboardButton("> ⁅ Database ⁆", "bsettings_database"),
            InlineKeyboardButton("Close", "misc_close")
        ]
    ])


@bot.on_message(filters.command("bsettings", ["/", "!", "-", "."]))
@pm_only
@require_sudo
async def func_bsettings(_, message: Message):
    user = message.from_user

    # required data needed for editing
    data = {
        "user_id": user.id, # authorization
        "collection_name": DBConstants.BOT_DATA,
        "search_key": "_id",
        "match_value": MemoryDB.bot_data.get("_id")
    }

    MemoryDB.insert(DBConstants.DATA_CENTER, user.id, data)

    # accessing bot data
    bot_data = MemoryDB.bot_data

    text = BotSettingsData.TEXT.format(
        'Yes' if bot_data.get('show_bot_pic') else 'No',
        len(bot_data.get('images') or []),
        bot_data.get('support_chat') or '-',
        bot_data.get('server_url') or '-',
        len(bot_data.get('sudo_users') or []),
        bot_data.get('shrinkme_api') or '-',
        bot_data.get('omdb_api') or '-',
        bot_data.get('weather_api') or '-'
    )
    
    # Required variables
    show_bot_pic = MemoryDB.bot_data.get("show_bot_pic") # boolean
    images = MemoryDB.bot_data.get("images")
    photo = None # random images set by owner/sudo
    photo_file_id = None # the photo id of bot itself

    if images:
        photo = random.choice(images).strip()
    elif show_bot_pic:
        try:
            async for bp in bot.get_chat_photos("me", 1):
                photo_file_id = bp.file_id # the high quality photo file_id
        except:
            pass
    
    if photo or photo_file_id:
        try:
            return await message.reply_photo(photo or photo_file_id, caption=text, reply_markup=BotSettingsData.BUTTONS)
        except BadRequest:
            pass
        except Exception as e:
            logger.error(e)
    
    # if BadRequest or No Photo or Other error
    await message.reply_text(text, reply_markup=BotSettingsData.BUTTONS)
