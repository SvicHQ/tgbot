from time import time

from pyrogram import filters
from pyrogram.types import Message, Chat

from app import bot
from app.helpers.args_extractor import extract_cmd_args
from app.modules import llm

@bot.on_message(filters.command("imagine", ["/", "!", "-", "."]))
async def func_imagine(_, message: Message):
    user = message.from_user or message.sender_chat
    prompt = extract_cmd_args(message.text, message.command)

    if not prompt:
        return await message.reply_text(
            f"Use `/{message.command[0]} prompt`\n"
            f"E.g. `/{message.command[0]} A cat and a dog playing`"
        )
    
    sent_message = await message.reply_text("🎨 Generating...")

    start_time = time()
    response = await llm.imagine(prompt)
    response_time = f"{(time() - start_time):.2f}s"

    if not response:
        return await sent_message.edit_text("Oops! Something went wrong!")
    
    if isinstance(user, Chat):
        mention = "Anonymous" # user.title
        user_id = "Hidden"
    else:
        mention = user.mention
        user_id = user.id
    
    caption = (
        f"<blockquote>{mention}: {prompt}</blockquote>\n"
        f"**Process time:** `{response_time}`\n"
        f"**UserID:** `{user_id}`"
    )

    await sent_message.delete()
    await message.reply_photo(response, caption=caption)
