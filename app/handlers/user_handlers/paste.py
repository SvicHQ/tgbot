from pyrogram import filters
from pyrogram.types import Message, Chat, InlineKeyboardButton, InlineKeyboardMarkup

from app import bot
from app.helpers.args_extractor import extract_cmd_args
from app.modules import telegraph

@bot.on_message(filters.command("paste", ["/", "!", "-", "."]))
async def func_paste(_, message: Message):
    user = message.from_user or message.sender_chat
    re_msg = message.reply_to_message

    if re_msg and re_msg.text:
        text = re_msg.text.html
    elif re_msg and re_msg.caption:
        text = re_msg.caption.html
    else:
        text = extract_cmd_args(message.text, message.command)
    
    if not text:
        return await message.reply_text(f"Use `/{message.command[0]} text` or reply the message/text with `/{message.command[0]}` command.")

    sent_message = await message.reply_text("Creating...")

    response = await telegraph.paste(text, user.full_name)
    if not response:
        return await sent_message.edit_text("Oops! Something went wrong!")
    
    if isinstance(user, Chat):
        mention = "Anonymous" # user.title
        user_id = "Hidden"
    else:
        mention = user.mention
        user_id = user.id
    
    await sent_message.edit_text(
        f"**URL:** {response}\n"
        f"**Req by:** {mention} | `{user_id}`\n",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Instant View", url=response)]])
    )
