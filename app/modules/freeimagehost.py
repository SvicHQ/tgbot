from time import time
from io import BytesIO
from aiohttp import ClientSession, FormData, ServerTimeoutError
from app import logger

async def upload_image(image):
    """
    :param URL/BASE64/Bytes: *image URL or BASE64 string or BytesIO/Binary open(example, 'rb')*
    :returns JSON:
    """
    api_key = "6d207e02198a847aa98d0a2a901485a5" # public access api key
    url = "https://freeimage.host/api/1/upload"

    params = {
        "key": api_key, # API Key
        "action": "upload", # What you want to do [values: upload].
        # "source": image_path, # img url or base64 string
        "format": "json" # Sets the return format [values: json (default), redirect, txt].
    }

    form = FormData()

    if isinstance(image, BytesIO):
        # This is BytesIO bytes
        image.seek(0)
        form.add_field("source", image, filename=image.name)
    elif isinstance(image, str):
        # This is img url or base64
        params["source"] = image
    else:
        # This is open(path, 'rb')
        form.add_field("source", image, filename=f"{int(time())}.png")
    
    try:
        async with ClientSession() as session:
            async with session.post(url, params=params, data=form) as response:
                json_data = await response.json()
                return json_data
    except ServerTimeoutError as e:
        logger.error(e)
        return False
    except Exception as e:
        logger.error(e)
