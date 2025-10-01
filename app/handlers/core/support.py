from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from app import bot, config, logger
from app.utils.database import MemoryDB, DBConstants
from app.utils.decorators.pm_only import pm_only


@bot.on_message(filters.command("support", ["/", "!", "-", "."]))
@pm_only
async def init_support_conv(_, message: Message):
    user = message.from_user

    await message.reply_text(
        f"Hey, {user.first_name}! Please send your request/report in one message.\n"
        "• /cancel to cancel conversation.\n\n"
        "<blockquote>**Note:** Request/Report should be related to this bot."
        "And we don't provide any support for ban, mute or other things related to groups managed by this bot.</blockquote>"
    )

    MemoryDB.insert(DBConstants.DATA_CENTER, user.id, {"support_status": 1})


async def support_state_one(_, message: Message):
    user = message.from_user

    try:
        text = (
            f"**Name:** <i>{user.mention}</i>\n"
            f"**UserID:** `{user.id}`\n"
            f"**Message:** {message.text.html if message.text else ''}\n\n"
            "<i>Reply to this message to continue conversation! or use /send</i>\n"
            f"||#uid{hex(user.id)}||"
        )

        btn = InlineKeyboardMarkup([[InlineKeyboardButton("User Profile", user_id=user.id)]]) if user.username else None
        await bot.send_message(config.owner_id, text, reply_markup=btn)
        # confirm message
        text = "Report has been submitted. Support team will contact you as soon as possible."
    except Exception as e:
        logger.error(e)
        text = "Oops, Something went wrong. Please try again."

    await message.reply_text(text)
    MemoryDB.insert(DBConstants.DATA_CENTER, message.from_user.id, {"support_status": 0})


@bot.on_message(filters.command("cancel", ["/", "!", "-", "."]))
@pm_only
async def cancel_support_conv(_, message: Message):
    user = message.from_user

    user_data = MemoryDB.data_center.get(user.id) or {}
    support_status = user_data.get("support_status")

    if not support_status:
        text = "There is no active conversation at the moment. /support to contact with support team!"
    else:
        text = "Reporting has been cancelled."
        # Cancel Reporting
        MemoryDB.insert(DBConstants.DATA_CENTER, user.id, {"support_status": 0})

    await message.reply_text(text)
