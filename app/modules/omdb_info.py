import aiohttp
from app import logger
from app.utils.database import MemoryDB

async def fetch_movieinfo(movie_name=None, imdb_id=None, year=None):
    """
    :param movie_name: requird if `imdb_id` wasn't provided
    :param imdb_id: requird if `movie_name` wasn't provided
    :param year: optional but recommended if you are using `movie_name`
    """
    omdb_api = MemoryDB.bot_data.get("omdb_api")
    if not omdb_api:
        return logger.error("OMDB API key wasn't provided!")
    
    if movie_name is None and imdb_id is None:
        return logger.error("Both value can't be None! movie_name or imdb_id must be provided!")
    
    api_url = "https://omdbapi.com/"
    params = {
        "apikey": omdb_api,
        "t": movie_name, # title
        "i": imdb_id,
        "y": year
    }
    # filtering out None values
    params = {k: v for k, v in params.items() if v is not None}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, params=params) as response:
                if response.ok:
                    data = await response.json()
                    return data
    except Exception as e:
        logger.error(e)
