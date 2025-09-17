from uuid import uuid4
from datetime import datetime

from pyrogram import filters
from pyrogram.types import Message

from app import bot
from app.utils.decorators.pm_only import pm_only
from app.utils.decorators.sudo_users import require_sudo

@bot.on_message(filters.command("log", ["/", "!", "-", "."]))
@pm_only
@require_sudo
async def func_log(_, message: Message):
    current_time = datetime.now()
    time_text = f"{current_time.hour}:{current_time.minute}:{current_time.second}"

    await message.reply_document(
        open("sys/log.txt", "rb"),
        caption=(
            f"**LogID:** `{uuid4()}`\n"
            f"**Time:** `{time_text}`"
        ),
        file_name=(
            f"log [{time_text}].txt"
        )
    )
