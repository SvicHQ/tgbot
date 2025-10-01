import asyncio
from functools import wraps
from pyrogram.types import Message
from pyrogram.enums import ChatType
from app import logger


def pm_only(func):
    @wraps(func)
    async def wraper(_, message: Message):
        try:
            if message.chat.type != ChatType.PRIVATE:
                try:
                    await message.delete()
                except Exception as e:
                    # No Return
                    await message.reply_text(str(e))
                
                sent_message = await message.reply_text("This command is made to be used in pm, not in public chat!")
                await asyncio.sleep(3)
                await sent_message.delete()
                return
        except Exception as e:
            return logger.error(e)
        
        return await func(_, message)
    return wraper
