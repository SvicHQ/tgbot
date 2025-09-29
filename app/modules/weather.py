import aiohttp
from app import logger
from app.utils.database import MemoryDB

async def weather_info(location):
    weather_api = MemoryDB.bot_data.get("weather_api")
    if not weather_api:
        return logger.error("Weather API wasn't provided!")
    
    api_url = "https://api.weatherapi.com/v1/current.json"
    params = {
        "key": weather_api,
        "q": location,
        "aqi": "no"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, params=params) as response:
                if response.ok:
                    data = await response.json()
                    return data
    except Exception as e:
        logger.error(e)
