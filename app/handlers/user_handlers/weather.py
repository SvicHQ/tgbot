from pyrogram import filters
from pyrogram.types import Message

from app import bot
from app.helpers.args_extractor import extract_cmd_args
from app.modules.weather import weather_info

@bot.on_message(filters.command("weather", ["/", "!", "-", "."]))
async def func_weather(_, message: Message):
    location = extract_cmd_args(message.text, message.command)

    if not location:
        return await message.reply_text(f"Use `/{message.command[0]} location name`\nE.g. `/{message.command[0]} los angeles`")
    
    info = await weather_info(location)
    if not info:
        return await message.reply_text("Oops! Something went wrong! (invalid location name? 🤔)")
    
    await message.reply_text(
        f"<blockquote>**Location info**</blockquote>\n\n"

        f"**City:** `{info['location']['name']}`\n"
        f"**Country:** `{info['location']['country']}`\n"
        f"**Zone:** `{info['location']['tz_id']}`\n"
        f"**Local time:** `{info['location']['localtime']}`\n\n"

        f"<blockquote>**Weather info**</blockquote>\n\n"

        f"**Condition:** `{info['current']['condition']['text']}`\n"
        f"**Temp (C):** `{info['current']['temp_c']}℃` **feels:** `{info['current']['feelslike_c']}℃`\n"
        f"**Temp (F):** `{info['current']['temp_f']}℉` **feels:** `{info['current']['feelslike_f']}℉`\n"
        f"**Humidity:** `{info['current']['humidity']}%`\n\n"

        f"**Wind:** `{info['current']['wind_mph']}mph` | `{info['current']['wind_kph']}kph`\n"
        f"**Wind (Angle):** `{info['current']['wind_degree']}°`\n"
        f"**UV Ray:** `{info['current']['uv']}`\n\n"

        "<blockquote>**Note:** ⚠ 8 or higher is harmful for skin!</blockquote>"
    )
