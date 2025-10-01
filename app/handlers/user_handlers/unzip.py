import os
from time import time
from asyncio import sleep

from pyrogram import Client, filters
from pyrogram.types import Message, Chat, ReplyParameters

from app import bot, logger
from app.helpers.args_extractor import extract_cmd_args
from app.helpers.progress_updater import progress_updater
from app.modules.utils import UTILITY


@bot.on_message(filters.command(["unzip", "uz"], ["/", "!", "-", "."]))
async def func_unzip(_: Client, message: Message):
    user = message.from_user or message.sender_chat
    re_msg = message.reply_to_message
    password = extract_cmd_args(message.text, message.command)

    if not re_msg or not re_msg.document:
        return await message.reply_text(f"Reply any `.zip` file to extract the file. E.g. `/{message.command[0]} password (if needed)`")
    
    if not re_msg.document.file_name.endswith(".zip"):
        return await message.reply_text("Replied file isn't a `.zip` file!")
    
    sent_message = await message.reply_text("Please wait...", reply_parameters=ReplyParameters(message_id=re_msg.id))
    await sent_message.pin(both_sides=True)

    startTime = time()
    zipFile = await re_msg.download(re_msg.document.file_name, progress=progress_updater, progress_args=[message, "Downloading...", startTime])
    if not zipFile:
        return await sent_message.edit_text("Unable to download!")
    
    # Unzipping
    await sent_message.edit_text("Unziping...")
    response = UTILITY.unzipFile(zipFile, password)

    # Remove Zip file
    try:
        os.remove(zipFile)
    except Exception as e:
        logger.error(e)
    
    # After Response
    if not isinstance(response, list):
        return await sent_message.edit_text(f"Error: {response}")
    
    # File path list
    counter, uploaded, uploadfailed= 0, 0, ""
    startTime = time()
    for i in response:
        try:
            counter += 1
            is_uploaded = None
            percent = counter * 100/len(response)
            
            text = (
                f"Uploading...\n"
                f"**File:** `{i}`\n"
                f"**Total Percent:** `{UTILITY.createProgressBar(int(percent))}` `{percent:.2f}%`"
            )

            try:
                is_uploaded = await message.reply_photo(i, progress=progress_updater, progress_args=[sent_message, text, startTime])
            except:
                try:
                    is_uploaded = await message.reply_video(i, width=1920, height=1080, progress=progress_updater, progress_args=[sent_message, text, startTime])
                except:
                    is_uploaded = await message.reply_document(i, progress=progress_updater, progress_args=[sent_message, text, startTime])
            
            if is_uploaded: uploaded += 1
        except Exception as e:
            uploadfailed += f"- {e}: `{i}`\n"
        
        # Zzz
        await sleep(0.5)

        try:
            os.remove(i)
        except Exception as e:
            logger.error(e)
    
    if isinstance(user, Chat):
        mention = "Anonymous" # user.title
        user_id = "Hidden"
    else:
        mention = user.mention
        user_id = user.id
    
    await sent_message.edit_text(
        f"**✅ Upload Completed!**\n\n"
        f"**Uploaded:** {uploaded}/{len(response)}\n"
        f"**Failed:** {uploadfailed or 0}\n"
        f"**Req by:** {mention}\n"
        f"**UserID:** `{user_id}`"
    )
