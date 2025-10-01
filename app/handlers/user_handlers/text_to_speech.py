from time import time

from pyrogram import filters
from pyrogram.types import Message, Chat, InlineKeyboardButton, InlineKeyboardMarkup

from app import bot, TTS_LANG_CODES_URL
from app.helpers.args_extractor import extract_cmd_args
from app.modules.gtts import text_to_speech


@bot.on_message(filters.command("tts", ["/", "!", "-", "."]))
async def func_tts(_, message: Message):
    user = message.from_user or message.sender_chat
    re_msg = message.reply_to_message
    text_to_conv = (re_msg.text or re_msg.caption) if re_msg else None
    lang_code = extract_cmd_args(message.text, message.command) or "en" # Default Lang Code `en`

    if not text_to_conv:
        return await message.reply_text(
            f"Reply any text to convert it into a voice message! E.g. Reply any message with `/{message.command[0]} en` to get english accent voice.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Language code's", url=TTS_LANG_CODES_URL)]])
        )
    
    sent_message = await message.reply_text("Processing...")

    response = text_to_speech(text_to_conv, lang_code)
    if not response:
        return await sent_message.edit_text("Oops! Something went wrong!")
    
    if isinstance(user, Chat):
        mention = "Anonymous" # user.title
        user_id = "Hidden"
    else:
        mention = user.mention
        user_id = user.id
    
    await sent_message.delete()
    await message.reply_audio(
        response,
        caption=(
            f"**Text:** <blockquote expandable>{text_to_conv}</blockquote>\n"
            f"**Req by:** {mention}\n"
            f"**ID:** `{user_id}`\n"
            f"**Timestamp:** `{int(time())}`"
        ),
        title=f"Voice {re_msg.id} [ {lang_code} ].mp3"
    )
