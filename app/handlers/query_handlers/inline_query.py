from base64 import b64decode, b64encode

from pyrogram.types import InlineQuery, InputTextMessageContent, InlineQueryResultArticle, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ChatType

from app import bot
from app.utils.database import DBConstants, MemoryDB
from app.modules.utils import UTILITY


@bot.on_inline_query()
async def inline_query_handler(_, query: InlineQuery):
    user = query.from_user
    message = query.query
    results = []
    # Default button
    btn = InlineKeyboardMarkup([[InlineKeyboardButton("Try inline", switch_inline_query_current_chat="")]])

    if not message:
        # instruction for user
        instruction_message = (
            "<blockquote>**Instructions: Available inline modes**</blockquote>\n\n"

            "**• Whisper: send someone a secret message in group chat! Similar command: /whisper**\n"
            f"   <i>- Example: `@{bot.me.username} @bishalqx980 This is a secret message 😜`</i>\n\n"

            f"**• userinfo({user.full_name}): Get your userinfo! Similar command: /info**\n"
            f"   <i>- Example: `@{bot.me.username} info`</i>\n\n"

            "**• Base64 Encode/Decode: Encode/Decode base64 in any chat! Similar commands: /encode | /decode**\n"
            f"   <i>- Example: `@{bot.me.username} base64 data or normal text`</i>\n\n"

            f"**• Instructions: `@{bot.me.username}` - to get this message!**\n\n"

            "**• Source code:** <a href='https://github.com/bishalqx980/tgbot'>GitHub</a>\n"
            "**• Report bug:** <a href='https://github.com/bishalqx980/tgbot/issues'>Report</a>\n"
            "**• Developer:** <a href='https://t.me/bishalqx680/22'>bishalqx980</a>"
        )

        results.append(
            InlineQueryResultArticle(
                title="ℹ️ Instructions",
                input_message_content=InputTextMessageContent(instruction_message),
                description="Click to see instructions...!",
                reply_markup=btn
            )
        )
        
        return await query.answer(results)
    
    # whisper option: if chat isn't private | This whisper system is temporary store message, use /whisper cmd for permanent message store
    if query.chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        splitted_message = message.split()
        whisper_username = splitted_message[0]
        secret_message = " ".join(splitted_message[1:])
        process_whisper = True

        if not whisper_username.startswith("@"):
            process_whisper = False
            results.append(InlineQueryResultArticle(
                title="😮‍💨 Whisper: Error ❌",
                input_message_content=InputTextMessageContent(f"`{whisper_username}` isn't a valid username! Check instructions... Example: `@{bot.me.username} @username Your Secret message!`"),
                description=f"{whisper_username}, isn't a valid username!",
                reply_markup=btn
            ))
        
        elif whisper_username.endswith("bot"):
            process_whisper = False
            results.append(InlineQueryResultArticle(
                title="😮‍💨 Whisper: Error ❌",
                input_message_content=InputTextMessageContent("Whisper isn't for bots!"),
                description="same",
                reply_markup=btn
            ))
        
        elif not secret_message:
            process_whisper = False
            results.append(InlineQueryResultArticle(
                title="😮‍💨 Whisper: Error ❌",
                input_message_content=InputTextMessageContent("What do you want to whisper? There is not whisper message!"),
                description="same",
                reply_markup=btn
            ))
        
        elif len(secret_message) > 150:
            process_whisper = False
            results.append(InlineQueryResultArticle(
                title="😮‍💨 Whisper: Error ❌",
                input_message_content=InputTextMessageContent("Whisper message is too long. (Max limit: 150 Characters)"),
                description="same",
                reply_markup=btn
            ))
        
        if process_whisper:
            data_center = MemoryDB.data_center.get("whisper_data") or {}
            whispers = data_center.get("whispers") or {}
            whisper_key = UTILITY.randomString()

            whispers.update({
                whisper_key: {
                    "sender_user_id": user.id,
                    "username": whisper_username, # contains @ prefix
                    "message": secret_message
                }
            })
            
            # Diffrent from normal /whisper cmd
            MemoryDB.insert(DBConstants.DATA_CENTER, "whisper_data", {"whispers": whispers})

            btn = InlineKeyboardMarkup([
                [InlineKeyboardButton("See the message 💭", f"misc_tmp_whisper_{whisper_key}")],
                [InlineKeyboardButton("Try Yourself!", "switch_to_inline")]
            ])

            results.append(InlineQueryResultArticle(
                title=f"😮‍💨 Whisper: Send to {whisper_username}? ✅",
                input_message_content=InputTextMessageContent(f"Hey, {whisper_username}. You got a whisper message from {user.name}."),
                description=f"Send whisper to {whisper_username}!",
                reply_markup=btn
            ))
    
    # Need to be here after message update otherwise it shows cached info
    user_info = (
        "<blockquote>`» user.info()`</blockquote>\n\n"
        f"**• Full name:** `{user.full_name}`\n"
        f"**  » First name:** `{user.first_name}`\n"
        f"**  » Last name:** `{user.last_name}`\n"
        f"**• Mention:** {user.mention}\n"
        f"**• Username:** {f'@{user.username}' if user.username else '-'}\n"
        f"**• User ID:** `{user.id}`\n"
        f"**• DC ID:** `{user.dc_id}`\n"
        f"**• Lang:** `{user.language_code}`\n"
        f"**• Is bot:** `{'Yes' if user.is_bot else 'No'}`\n"
        f"**• Is premium:** `{'Yes' if user.is_premium else 'No'}`"
    )

    results.append(InlineQueryResultArticle(
        title=f"❕ user.info({user.full_name})",
        input_message_content=InputTextMessageContent(user_info),
        description="See your info...!",
        reply_markup=btn
    ))

    # base64 encode / decode
    try:
        b64_decode = b64decode(message).decode("utf-8")
        results.append(InlineQueryResultArticle(
            title="📦 Base64: Decode (base64 to text)",
            input_message_content=InputTextMessageContent(f"`{b64_decode}`"),
            description=b64_decode,
            reply_markup=btn
        )) if b64_decode else None
    except:
        pass

    try:
        b64_encode = b64encode(message.encode("utf-8")).decode("utf-8")
        results.append(InlineQueryResultArticle(
            title="📦 Base64: Encode (text to base64)",
            input_message_content=InputTextMessageContent(f"`{b64_encode}`"),
            description=b64_encode,
            reply_markup=btn
        )) if b64_encode else None
    except:
        pass

    # Final result
    if not results:
        return
    
    await query.answer(results)
