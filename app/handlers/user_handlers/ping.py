import aiohttp
from time import time

from pyrogram import filters
from pyrogram.types import Message

from app import bot
from app.helpers.args_extractor import extract_cmd_args

@bot.on_message(filters.command("ping", ["/", "!", "-", "."]))
async def func_ping(_, message: Message):
    url = extract_cmd_args(message.text, message.command)

    if not url:
        return await message.reply_text(f"Use `/{message.command[0]} url`\nE.g. `/{message.command[0]} https://google.com`")
    
    if url[0:4] != "http":
        url = f"http://{url}"

    sent_message = await message.reply_text(f"Pinging {url}\nPlease wait...")
    start_time = time()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response_time = int((time() - start_time) * 1000) # converting to ms
                if response_time > 1000:
                    response_time = f"{(response_time / 1000):.2f}s"
                else:
                    response_time = f"{response_time}ms"
                
                status_codes = {
                    200: "✅ Online (OK)",
                    201: "✅ Created",
                    202: "✅ Accepted",
                    204: "⚠️ No Content",
                    301: "➡️ Moved Permanently",
                    302: "➡️ Found (Redirect)",
                    400: "❌ Bad Request",
                    401: "🔒 Unauthorized",
                    403: "🚫 Forbidden",
                    404: "❌ Not Found",
                    408: "⏳ Request Timeout",
                    500: "🔥 Internal Server Error",
                    502: "⚠️ Bad Gateway",
                    503: "⚠️ Service Unavailable"
                }

                status = status_codes.get(response.status, "⚠️ Unknown Status")
                text = (
                    f"Site: {url}\n"
                    f"R.time: `{response_time}`\n"
                    f"R.code: `{response.status}`\n"
                    f"Status: `{status}`"
                )
    except aiohttp.ServerTimeoutError:
        text = "Error: Request timeout."
    except aiohttp.ServerConnectionError:
        text = "Error: Connection error."
    except Exception as e:
        text = f"Error: {e}"
    
    await sent_message.edit_text(f"**{text}**")
