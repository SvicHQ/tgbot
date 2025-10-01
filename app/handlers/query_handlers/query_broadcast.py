import asyncio
from time import time
from io import BytesIO

from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import BadRequest, Forbidden

from app import bot
from app.modules.utils import UTILITY
from app.utils.database import DBConstants, MemoryDB, MongoDB


@bot.on_callback_query(filters.regex(r"broadcast_[A-Za-z0-9]+"))
async def query_broadcast(_, query: CallbackQuery):
    chat = query.message.chat

    # refined query data
    query_data = query.data.removeprefix("broadcast_")

    # accessing Database
    broadcastData = MemoryDB.data_center.get("broadcast")
    if not broadcastData:
        return await query.answer("Session Expired!", True)
    
    # handling query
    if query_data == "none":
        return await query.answer()
    
    # only for boolean (toggle)
    elif query_data.startswith("value_"):
        # for example data will be `forward` or `pin`
        data = query_data.removeprefix("value_")

        existing_data = broadcastData.get(data) # Boolean
        if existing_data:
            broadcastData.update({data: False})
        else:
            broadcastData.update({data: True})
        
        await query.answer(f"Updated: {data}: {broadcastData.get(data)}", True)
    
    elif query_data == "send":
        # variables
        broadcastText = broadcastData["broadcastText"] # only if the message doesn't contain any video/doc or other things
        broadcastCaption = broadcastData["broadcastCaption"] # message with video/audio/doc etc.

        broadcastPhoto = broadcastData["broadcastPhoto"]

        broadcastDocument = broadcastData["broadcastDocument"]
        broadcastDocument_filename = broadcastData["broadcastDocument_filename"]

        broadcastVideo = broadcastData["broadcastVideo"]
        broadcastVideo_note = broadcastData["broadcastVideo_note"]

        broadcastAudio = broadcastData["broadcastAudio"]
        broadcastAudio_filename = broadcastData["broadcastAudio_filename"]

        broadcastVoice = broadcastData["broadcastVoice"]

        is_forward = broadcastData["forward"]
        is_pin = broadcastData["pin"]

        # getting userID from DB
        users_id = MongoDB.find(DBConstants.USERS_DATA, "user_id") # registed users ID list
        active_status = MongoDB.find(DBConstants.USERS_DATA, "active_status") # if users with `active_status`, no matter its True or False
        active_users = []

        if len(users_id) != len(active_status): # Checking if there is any user data that doesn't contains `active_status`
            active_users = users_id
        else:
            # Separating `active_status` True users
            combined_list = list(zip(users_id, active_status))
            for user_id, is_active in combined_list:
                if is_active: active_users.append(user_id)
        
        # counters
        sent_count = 0
        exception_count = 0
        progress = 0
        # exception happend with users ID
        exception_users_id = []

        broadcastUpdateText = (
            "<blockquote>**Broadcast**</blockquote>\n\n"

            "**📦 Database information**\n"
            "**• Total users:** `{}`\n"
            "**• Active users:** `{}`\n\n"

            "**📊 Progress**\n"
            "**• Sent:** `{}`\n"
            "**• Exception:** `{}`\n"
            "**• Progress:** `{}%`\n"
            "{}" # progress bar
        )

        text = broadcastUpdateText.format(
            len(users_id),
            len(active_users),
            sent_count,
            exception_count,
            f"{progress:.2f}",
            "[]"
        )

        broadcastButton = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", "broadcast_cancel")]])
        
        try:
            await query.edit_message_text(text, reply_markup=broadcastButton)
        except BadRequest:
            await query.edit_message_caption(text, reply_markup=broadcastData)
        except Exception as e:
            return await bot.send_message(chat.id, str(e))

        broadcastStartTime = time()

        for user_id in active_users:
            sent_message = None

            is_cancelled = broadcastData["is_cancelled"]
            if is_cancelled:
                return
            
            try:
                if is_forward:
                    sent_message = await bot.forward_messages(user_id, chat.id, broadcastData["replied_message_id"])
                else:
                    if broadcastText:
                        sent_message = await bot.send_message(chat_id=user_id, text=broadcastText)
                    elif broadcastPhoto:
                        sent_message = await bot.send_photo(chat_id=user_id, photo=broadcastPhoto, caption=broadcastCaption)
                    elif broadcastDocument:
                        sent_message = await bot.send_document(chat_id=user_id, document=broadcastDocument, caption=broadcastCaption, file_name=broadcastDocument_filename)
                    elif broadcastVideo:
                        sent_message = await bot.send_video(chat_id=user_id, video=broadcastVideo, caption=broadcastCaption)
                    elif broadcastVideo_note:
                        sent_message = await bot.send_video_note(chat_id=user_id, video_note=broadcastVideo_note)
                    elif broadcastAudio:
                        sent_message = await bot.send_audio(chat_id=user_id, audio=broadcastAudio, title=broadcastAudio_filename, caption=broadcastCaption, file_name=broadcastAudio_filename)
                    elif broadcastVoice:
                        sent_message = await bot.send_voice(chat_id=user_id, voice=broadcastVoice, caption=broadcastCaption)
                
                if sent_message: sent_count += 1

            except Forbidden:
                exception_count += 1
                exception_users_id.append(f"Forbidden: {user_id}")
                # Updating MongoDB (user blocked the bot)
                MongoDB.update(DBConstants.USERS_DATA, "user_id", int(user_id), {"active_status": False})
            
            except Exception as e:
                exception_count += 1
                exception_users_id.append(f"{str(e)}: {user_id}")
            
            if is_pin and sent_message:
                try:
                    await sent_message.pin()
                except:
                    pass
            
            progress = (sent_count + exception_count) * 100 / len(active_users)
            progressBar = UTILITY.createProgressBar(progress)

            updateText = broadcastUpdateText.format(
                len(users_id),
                len(active_users),
                sent_count,
                exception_count,
                f"{progress:.2f}",
                progressBar
            )

            btn = None if (sent_count + exception_count) == len(active_users) else broadcastButton

            try:
                await query.edit_message_text(updateText, reply_markup=btn)
            except BadRequest:
                await query.edit_message_caption(updateText, reply_markup=btn)
            except Exception as e:
                await bot.send_message(chat.id, f"An error occured (broadcast still running): {e}")

            await asyncio.sleep(0.5) # sleep for 0.5 sec
        
        broadcastEndTime = time()

        if (broadcastEndTime - broadcastStartTime) > 60:
            time_took = f"{((broadcastEndTime - broadcastStartTime) / 60):.2f} min"
        else:
            time_took = f"{(broadcastEndTime - broadcastStartTime):.2f} sec"
        
        updateText += f"\n\n**Broadcast Done ✅: {time_took}**"
        
        try:
            await query.edit_message_text(updateText)
        except BadRequest:
            await query.edit_message_caption(updateText)
        except Exception as e:
            await bot.send_message(chat.id, f"An error occured (After broadcast done): {e}")

        if exception_users_id:
            exception_file = BytesIO(", ".join(exception_users_id).encode())
            exception_file.name = "Exception.txt"

            await bot.send_document(chat_id=chat.id, document=exception_file, caption=f"Total Exception: {len(exception_users_id)}")
    
    elif query_data == "cancel":
        broadcastData.update({"is_cancelled": True})
        await query.answer("Broadcast is cancelled!", True)
