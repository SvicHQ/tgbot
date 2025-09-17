from pyrogram import filters
from pyrogram.types import Message

from app import bot
from app.helpers.args_extractor import extract_cmd_args
from app.modules import telegraph

@bot.on_message(filters.command("paste", ["/", "!", "-", "."]))
async def func_paste(_, message: Message):
    user = message.from_user or message.sender_chat
    re_msg = message.reply_to_message

    if re_msg and re_msg.text:
        text = message.text.html
    elif re_msg and re_msg.caption:
        text = message.caption.html
    else:
        text = extract_cmd_args(message.text, message.command)
    
    if not text:
        return await message.reply_text(f"Use `/{message.command[0]} text` or reply the message/text with `/{message.command[0]}` command.")

    sent_message = await message.reply_text(f"Creating...")

    paste = await telegraph.paste(text, user.full_name)
    if not paste:
        return await sent_message.edit_text("Oops! Something went wrong!")
    
    await sent_message.edit_text(paste)
