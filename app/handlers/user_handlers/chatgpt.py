from time import time

from pyrogram import filters
from pyrogram.types import Message, Chat

from app import bot
from app.helpers.args_extractor import extract_cmd_args
from app.modules import llm


@bot.on_message(filters.command("gpt", ["/", "!", "-", "."]))
async def func_gpt(_, message: Message):
    user = message.from_user or message.sender_chat
    prompt = extract_cmd_args(message.text, message.command)

    if not prompt:
        return await message.reply_text(
            f"Use `/{message.command[0]} prompt`\n"
            f"E.g. `/{message.command[0]} what is relativity? explain in simple and short way.`"
        )
    
    sent_message = await message.reply_text("💭 Generating...")
    
    start_time = time()
    response = await llm.text_gen(prompt)
    response_time = int(time() - start_time)

    if isinstance(user, Chat):
        mention = "Anonymous" # user.title
        user_id = "Hidden"
    else:
        mention = user.mention
        user_id = user.id

    if response:
        text = (
            f"<blockquote expandable>{mention}: {prompt}</blockquote>\n"
            f"<blockquote expandable>**{bot.me.first_name}:** {response}</blockquote>\n"
            f"**Process time:** `{response_time}s`\n"
            f"**UserID:** `{user_id}`"
        )
    else:
        text = "Oops! Something went wrong!"
    
    await sent_message.edit_text(text)
