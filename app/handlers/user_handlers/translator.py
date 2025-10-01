from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ChatType

from app import bot, TL_LANG_CODES_URL
from app.helpers.args_extractor import extract_cmd_args
from app.modules.translator import fetch_lang_codes, translate
from app.utils.database import DBConstants, database_search


@bot.on_message(filters.command("tr", ["/", "!", "-", "."]))
async def func_tr(_, message: Message):
    chat = message.chat
    user = message.from_user or message.sender_chat
    re_msg = message.reply_to_message
    text = (re_msg.text or re_msg.caption) if re_msg else None
    args = extract_cmd_args(message.text, message.command)

    if not text and not args:
        return await message.reply_text(
            f"Use `/{message.command[0]} text` or `/{message.command[0]} lang code text` or reply the text with `/{message.command[0]}` or `/{message.command[0]} lang code`\n\n"
            "Enable auto translator mode for this chat from /settings",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Language code's", url=TL_LANG_CODES_URL)]])
        )
    
    to_translate = None
    lang_code = None
    LANG_CODE_LIST = fetch_lang_codes()
    
    if args:
        words = args.split()
        first_word = words[0]
        if first_word in LANG_CODE_LIST:
            lang_code = first_word
            to_translate = " ".join(words[1:])
    
    if not text and not to_translate and args: # /tr text & lang_code = from database
        to_translate = args

    elif text and not to_translate: # /tr (maybe lang_code or maybe not) and replied
        to_translate = text
    
    if not lang_code:
        if chat.type == ChatType.PRIVATE:
            collection_name = DBConstants.USERS_DATA
            to_find = "user_id"
            to_match = user.id # Private Chat User, No need to check anonymous
        else:
            collection_name = DBConstants.CHATS_DATA
            to_find = "chat_id"
            to_match = chat.id

        database_data = database_search(collection_name, to_find, to_match)
        if not database_data:
            return await message.reply_text("<blockquote>**Error:** Chat isn't registered! Remove/Block me from this chat then add me again!</blockquote>")
        
        lang_code = database_data.get("lang")
    
    if not lang_code:
        return await message.reply_text(
            f"Chat language code wasn't found! Use /{message.command[0]} to get more details or /settings to set chat language.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Language code's", url=TL_LANG_CODES_URL)]])
        )
    
    sent_message = await message.reply_text("💭 Translating...")

    translated_text = translate(to_translate, lang_code)
    btn = None

    if translated_text is False:
        text = f"Invalid language code was given! Use /{message.command[0]} to get more details or /settings to set chat language."
        btn = InlineKeyboardMarkup([[InlineKeyboardButton("Language code's", url=TL_LANG_CODES_URL)]])

    elif not translated_text:
        text = "Oops! Something went wrong!"

    else:
        text = translated_text
    
    await sent_message.edit_text(text, reply_markup=btn)
