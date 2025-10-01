from pyrogram import filters
from pyrogram.types import Message, ReplyParameters

from app import bot
from app.helpers.args_extractor import extract_cmd_args
from app.utils.decorators.sudo_users import require_sudo


@bot.on_message(filters.command("say", ["/", "!", "-", "."]))
@require_sudo
async def func_say(_, message: Message):
    re_msg = message.reply_to_message
    speech = extract_cmd_args(message.text.html if message.text else "", message.command) # the sentence to say
    
    try:
        await message.delete()
    except Exception as e:
        return await message.reply_text(str(e))
    
    if not speech:
        return await message.reply_text(f"What should I say, lol? Example: `/{message.command[0]} Hi`")
    
    await message.reply_text(speech, reply_parameters=ReplyParameters(message_id=re_msg.id if re_msg else None))
