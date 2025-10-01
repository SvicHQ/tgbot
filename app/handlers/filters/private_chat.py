from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import Forbidden

from app import bot, config, TL_LANG_CODES_URL
from app.utils.database import DBConstants, database_search, MemoryDB

from app.handlers.core.support import support_state_one
from .edit_database import edit_database
from .auto_translate import autoTranslate


@bot.on_message(filters.private & ~filters.regex(r"^[\/!\-.]"))
async def filter_private_chat(_, message: Message):
    chat = message.chat
    user = message.from_user
    re_msg = message.reply_to_message

    user_data = MemoryDB.data_center.get(user.id) or {}
    support_status = user_data.get("support_status")
    if support_status:
        return await support_state_one(_, message)
    
    # Support Conversation
    if re_msg:
        message_text = re_msg.text or re_msg.caption

        if message_text and "#uid" in message_text:
            try:
                support_seeker_uid = int(message_text.split("#uid")[1].strip(), 16) # base 16: hex
                text, btn = "", None
                # if user sending message to owner then add userinfo
                if user.id != config.owner_id:
                    text += (
                        f"**Name:** <i>{user.mention}</i>\n"
                        f"**UserID:** `{user.id}`\n"
                    )

                    btn = InlineKeyboardMarkup([[InlineKeyboardButton("User Profile", user_id=user.id)]]) if user.username else None
                
                # Common text for owner & user
                text += (
                    f"**Message:** {message.text.html if message.text else '-'}\n\n"
                    "<i>Reply to this message to continue conversation!</i>\n"
                    f"||#uid{hex(user.id)}||"
                )

                await bot.send_message(support_seeker_uid, text, reply_markup=btn)
                reaction = "👍"
            except Forbidden:
                reaction = "👎"
            except Exception as e:
                await message.reply_text(f"Error: `{e}`")
                reaction = "🤷‍♂"
            # Confirm that message is sent or not
            await message.react(reaction)
    
    is_editing = edit_database(chat.id, user.id, message)
    if is_editing:
        return
    
    user_data = database_search(DBConstants.USERS_DATA, "user_id", user.id)
    if not user_data:
        return await message.reply_text("<blockquote>**Error:** Chat isn't registered! Remove/Block me from this chat then add me again!</blockquote>")
    
    # Echo message
    if user_data.get("echo"):
        echo_message = None

        if message.text:
            echo_message = message.text.html
        elif message.caption:
            echo_message = message.caption.html
        
        if echo_message:
            await message.reply_text(echo_message)
    
    # Auto Translator
    auto_tr = user_data.get("auto_tr")
    chat_lang = user_data.get("lang")

    if auto_tr and not chat_lang:
        await message.reply_text(
            "Chat language code wasn't found! Use /settings to set chat language.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Language code's", url=TL_LANG_CODES_URL)]])
        )
    
    elif auto_tr:
        await autoTranslate(message, user, chat_lang)
