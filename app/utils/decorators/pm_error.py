from functools import wraps
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ChatType
from app import bot, logger


def pm_error(func):
    @wraps(func)
    async def wraper(_, message: Message):
        try:
            if message.chat.type == ChatType.PRIVATE:
                return await message.reply_text(
                    "This command is made to be used in group chats, not in pm!",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Add me to Group", url=f"http://t.me/{bot.me.username}?startgroup=help")]])
                )
        except Exception as e:
            return logger.error(e)
        
        return await func(_, message)
    return wraper
