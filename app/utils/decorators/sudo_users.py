from functools import wraps
from pyrogram.types import Message
from app import logger, config
from app.utils.database import MemoryDB

def require_sudo(func):
    """
    :returns list: list of sudo's including **owner_id**
    """
    @wraps(func)
    async def wraper(_, message: Message):
        try:
            owner_id = config.owner_id
            sudo_users = MemoryDB.bot_data.get("sudo_users") or []

            if owner_id not in sudo_users:
                sudo_users.append(owner_id)
            
            if message.from_user.id not in sudo_users:
                return await message.reply_text("Access denied!")
        except Exception as e:
            return logger.error(e)
        
        return await func(_, message)
    return wraper
