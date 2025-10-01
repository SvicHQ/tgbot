from urllib.parse import quote

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from app import bot, PSNDL_WEBSITE_URL
from app.helpers.args_extractor import extract_cmd_args


@bot.on_message(filters.command("psndl", ["/", "!", "-", "."]))
async def func_psndl(_, message: Message):
    game_name = extract_cmd_args(message.text, message.command)

    if not game_name:
        return await message.reply_text(
            f"Use `/{message.command[0]} game name`\n"
            f"E.g. `/{message.command[0]} red dead redemption`",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Website", url=PSNDL_WEBSITE_URL)]])
        )
    
    await message.reply_text(
        f"Search result for `{game_name}`",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"Result('{game_name}')", url=f"{PSNDL_WEBSITE_URL}?name={quote(game_name)}")]])
    )
