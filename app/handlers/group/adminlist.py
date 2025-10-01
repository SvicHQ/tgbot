from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMembersFilter, ChatMemberStatus

from app import bot
from app.utils.decorators.pm_error import pm_error


@bot.on_message(filters.command("adminlist", ["/", "!", "-", "."]))
@pm_error
async def func_adminlist(_, message: Message):
    chat = message.chat

    owner, admins = [], []

    async for member in chat.get_members(filter=ChatMembersFilter.ADMINISTRATORS):
        name = "Anonymous" if member.privileges.is_anonymous else member.user.mention
        title = member.custom_title or "~"
        formatted = f"• {name} - <i>{title}</i>"

        if member.status == ChatMemberStatus.OWNER:
            owner.append(formatted)
        elif not member.user.is_bot:
            admins.append(formatted)

    text = f"<blockquote>{chat.title}</blockquote>\n\n"
    if owner:
        text += "**Owner:**\n" + "\n".join(owner)
    if admins:
        text += "\n\n**Admins:**\n" + "\n".join(admins)

    await message.reply_text(text)
