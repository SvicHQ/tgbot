from pyrogram.types import Message, User, InlineKeyboardButton, InlineKeyboardMarkup

from app import TL_LANG_CODES_URL
from app.modules.translator import translate

async def autoTranslate(message: Message, user: User, lang_code: str):
    """
    :param message: Message Class
    :param user: User class (`message.from_user`)
    :param lang_code: Get from user/chat database
    """
    text = message.text or message.caption
    # main func
    response = translate(text, lang_code)

    if response is False:
        await message.reply_text(
            "Invalid language code was given! Use /settings to set chat language.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Language code's", url=TL_LANG_CODES_URL)]])
        )
        return
    
    if not response:
        return
    
    if response.lower() != text.lower():
        await message.reply_text(f"{user.mention}: {response}")
