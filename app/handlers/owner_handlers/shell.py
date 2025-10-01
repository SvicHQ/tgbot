import subprocess
from io import BytesIO
from time import time

from pyrogram import filters
from pyrogram.types import Message

from app import bot
from app.helpers.args_extractor import extract_cmd_args
from app.utils.decorators.pm_only import pm_only
from app.utils.decorators.sudo_users import require_sudo


@bot.on_message(filters.command("shell", ["/", "!", "-", "."]))
@pm_only
@require_sudo
async def func_shell(_, message: Message):
    command = extract_cmd_args(message.text, message.command).replace("'", "")
    
    if not command:
        return await message.reply_text(f"Use `/{message.command[0]} dir/ls` [linux/Windows Depend on your hosting server]")
    
    sent_message = await message.reply_text("**⌊ please wait... ⌉**")

    time_executing = time()

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
    except Exception as e:
        return await sent_message.edit_text(str(e))
    
    time_executed = time()
    
    if not result.stdout and not result.stderr:
        return await sent_message.edit_text("**⌊ None ⌉**")

    result = result.stdout if result.stdout else result.stderr
    
    info = (
        f"**Command**: `{command}`\n"
        f"**Execute time**: `{(time_executed - time_executing):.2f}s`"
    )

    try:
        await sent_message.edit_text(
            f"{info}\n"
            f"<pre>{result}</pre>"
        )
    except:
        shell = BytesIO(result.encode())
        shell.name = "shell.txt"

        await sent_message.delete()
        await message.reply_document(shell, caption=info)
