from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatType
from pyrogram.errors import Forbidden

from app import bot
from app.helpers.args_extractor import extract_cmd_args
from app.utils.decorators.pm_only import pm_only
from app.utils.decorators.sudo_users import require_sudo


@bot.on_message(filters.command("send", ["/", "!", "-", "."]))
@pm_only
@require_sudo
async def func_send(_, message: Message):
    chat = message.chat
    user = message.from_user
    re_msg = message.reply_to_message
    args = extract_cmd_args(message.text, message.command) # contains something if forward is true and contains victim_id >> /send f chat_id
    
    if not args or not re_msg:
        return await message.reply_text(
            f"Use `/{message.command[0]} ChatID/Username` by replying a message!\n"
            f"`/{message.command[0]} f ChatID/Username` to forward the replied message to ChatID/Username!\n"
            "<blockquote expandable>Returns reaction on message\n"
            "- Sent: 👍\n"
            "- Forbidden: 👎\n"
            "- Something went wrong: 🤷‍♂ </blockquote>"
        )
    
    forward_confirm = None
    victim_id = args # ID or Username
    reaction = "👍"

    splited_text = args.split()
    if len(splited_text) == 2:
        forward_confirm, victim_id = splited_text
    
    try:
        if forward_confirm:
            await bot.forward_messages(victim_id, chat.id, re_msg.id)
        
        else:
            try:
                victim_chat_info = await bot.get_chat(victim_id)
            except Exception as e:
                return await message.reply_text(str(e))
            
            if victim_chat_info.type == ChatType.PRIVATE:
                text = (
                    f"Message: {re_msg.text.html if re_msg.text else '-'}\n\n"
                    "<i>Reply to this message to continue conversation!</i>\n"
                    f"||#uid{hex(user.id)}||"
                )
                caption = (
                    f"Message: {re_msg.caption.html if re_msg.caption else '-'}\n\n"
                    "<i>Reply to this message to continue conversation!</i>\n"
                    f"||#uid{hex(user.id)}||"
                )
            else:
                text = re_msg.text.html if re_msg.text else None
                caption = re_msg.caption.html if re_msg.caption else None
            
            photo = re_msg.photo
            audio = re_msg.audio
            video = re_msg.video
            document = re_msg.document
            voice = re_msg.voice
            video_note = re_msg.video_note
            btn = re_msg.reply_markup

            if re_msg.text:
                await bot.send_message(victim_id, text, reply_markup=btn)

            elif photo:
                await bot.send_photo(victim_id, photo.file_id, caption, reply_markup=btn)

            elif audio:
                await bot.send_audio(victim_id, audio.file_id, caption, title=audio.file_name, file_name=audio.file_name, reply_markup=btn)

            elif video:
                await bot.send_video(victim_id, video.file_id, caption, reply_markup=btn)

            elif document:
                await bot.send_document(victim_id, document.file_id, caption=caption, file_name=document.file_name, reply_markup=btn)
            
            elif voice:
                await bot.send_voice(victim_id, voice.file_id, caption, reply_markup=btn)
            
            elif video_note:
                await bot.send_video_note(victim_id, video_note.file_id, reply_markup=btn)
            
            else:
                return await message.reply_text("Replied content isn't added yet. /support to contact with developer.")
            
    except Forbidden:
        reaction = "👎"
    except Exception as e:
        await message.reply_text(f"Error: `{e}`")
        reaction = "🤷‍♂"

    await message.react(reaction)
