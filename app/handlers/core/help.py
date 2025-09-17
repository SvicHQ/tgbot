import random

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ChatType
from pyrogram.errors import BadRequest

from app import bot, logger
from app.utils.database import MemoryDB, database_add_user

class HelpMenuData:
    TEXT = (
        "<blockquote>**Help Menu**</blockquote>\n\n"
        "Hey! Welcome to the bot help section.\n"
        "I'm a Telegram bot that manages groups and handles various tasks effortlessly.\n\n"
        "• /start - Start the bot\n"
        "• /help - To see this message\n"
        "• /support - Get Support or Report any bug related to bot"
    )

    BUTTONS = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Group Management", "help_menu_gm1"),
            InlineKeyboardButton("AI/LLM", "help_menu_ai_knowledge")
        ],
        [
            InlineKeyboardButton("Misc", "help_menu_misc"),
            InlineKeyboardButton("Owner/Sudo", "help_menu_owner")
        ],
        [
            InlineKeyboardButton("» bot.info()", "help_menu_botinfo"),
            InlineKeyboardButton("Close", "misc_close"),
            InlineKeyboardButton("Try inline", "switch_to_inline")
        ]
    ])


@bot.on_message(filters.command("help", ["/", "!", "-", "."]) | filters.regex("^/start help$"))
async def func_help(_, message: Message):
    user = message.from_user or message.sender_chat
    chat = message.chat

    if chat.type != ChatType.PRIVATE:
        return await message.reply_text(
            f"Hey, {user.first_name or user.title}\nContact me in PM for help!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Help Menu", url=f"http://t.me/{bot.me.username}?start=help")]])
        )
    
    # Database entry checking if user is registered. (Optionally Given!! /start detects all users)
    database_add_user(user)

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
            return await message.reply_photo(photo or photo_file_id, caption=HelpMenuData.TEXT, reply_markup=HelpMenuData.BUTTONS)
        except BadRequest:
            pass
        except Exception as e:
            logger.error(e)
    
    # if BadRequest or No Photo or Other error
    await message.reply_text(HelpMenuData.TEXT, reply_markup=HelpMenuData.BUTTONS)
