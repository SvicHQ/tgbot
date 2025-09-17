from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ChatType
from pyrogram.errors import BadRequest

from app import bot, logger, ORIGINAL_BOT_USERNAME, ORIGINAL_BOT_ID
from app.utils.database import database_add_user, MemoryDB

@bot.on_message(filters.command("start", ["/", "!", "-", "."]) & ~filters.regex("help"))
async def func_start(_, message: Message):
    user = message.from_user or message.sender_chat
    chat = message.chat

    if chat.type != ChatType.PRIVATE:
        return await message.reply_text(
            f"Hey, {user.first_name or user.title}\nStart me in PM!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Start me in PM", url=f"http://t.me/{bot.me.username}?start=start")]])
        )
    
    # Database entry checking if user is registered.
    database_add_user(user)

    # Required variables
    show_bot_pic = MemoryDB.bot_data.get("show_bot_pic") # boolean
    support_chat = MemoryDB.bot_data.get("support_chat")
    photo_file_id = None # the photo id of bot itself

    if show_bot_pic:
        try:
            async for bp in bot.get_chat_photos("me", 1):
                photo_file_id = bp.file_id # the high quality photo file_id
        except:
            pass
    
    text = (
        f"Hey, {user.first_name}! I'm {bot.me.first_name}!\n\n"
        "I can help you to manage your chat with a lots of useful features!\n"
        "Feel free to add me to your chat.\n\n"
        "• /help - Get bot help menu\n\n"
        "**• Source code:** <a href='https://github.com/bishalqx980/tgbot'>GitHub</a>\n"
        "**• Report bug:** <a href='https://github.com/bishalqx980/tgbot/issues'>Report</a>\n"
        "**• Developer:** <a href='https://t.me/bishalqx680/22'>bishalqx980</a>"
    )

    if bot.me.id != ORIGINAL_BOT_ID:
        text += f"\n\n<blockquote>Cloned bot of @{ORIGINAL_BOT_USERNAME}</blockquote>"
    
    btn_data = [InlineKeyboardButton("Add me to Group", url=f"http://t.me/{bot.me.username}?startgroup=help")]
    if support_chat:
        btn_data.append(InlineKeyboardButton("Support Chat", url=support_chat))
    
    btn = InlineKeyboardMarkup([btn_data])

    if photo_file_id:
        try:
            return await message.reply_photo(photo_file_id, caption=text, reply_markup=btn)
        except BadRequest:
            pass
        except Exception as e:
            logger.error(e)
    
    # if BadRequest or No Photo or Other error
    await message.reply_text(text, reply_markup=btn)
