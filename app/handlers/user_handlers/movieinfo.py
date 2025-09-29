from pyrogram import filters
from pyrogram.types import Message

from app import bot
from app.helpers.args_extractor import extract_cmd_args
from app.modules.omdb_info import fetch_movieinfo

@bot.on_message(filters.command("movie", ["/", "!", "-", "."]))
async def func_movie(_, message: Message):
    movie_name = extract_cmd_args(message.text, message.command)

    if not movie_name:
        return await message.reply_text(
            f"Use `/{message.command[0]} movie name`\n"
            f"E.g. `/{message.command[0]} animal` OR\n"
            f"`/{message.command[0]} -i tt13751694` [IMDB ID] OR\n"
            f"`/{message.command[0]} bodyguard -y 2011`"
        )
        
    
    if "-i" in movie_name and "-y" in movie_name:
        return await message.reply_text(
            f"⚠ You can't use both statement at once!\n"
            f"/{message.command[0]} for details."
        )
    
    imdb_id = None
    year = None
    
    if "-i" in movie_name:
        index_i = movie_name.index("-i")
        imdb_id = movie_name[index_i + len("-i"):].strip()
        movie_name = None
    elif "-y" in movie_name:
        index_y = movie_name.index("-y")
        year = movie_name[index_y + len("-y"):].strip()
        movie_name = movie_name[0: index_y].strip()
    
    movie_info = await fetch_movieinfo(movie_name=movie_name, imdb_id=imdb_id, year=year)
    if not movie_info:
        return await message.reply_text("Oops! Something went wrong!")
    
    elif movie_info["Response"] == "False":
        return await message.reply_text("Invalid movie name!")
    
    runtime = movie_info["Runtime"]
    runtime = f"{int(runtime[0:3]) // 60} Hour {int(runtime[0:3]) % 60} Min" if runtime != "N/A" else "N/A"

    text = (
        f"**<a href='https://www.imdb.com/title/{movie_info.get('imdbID')}'>{movie_info.get('Title')} | {movie_info.get('imdbID')}</a>**\n\n"
        f"**🎥 Content Type:** {movie_info.get('Type')}\n"
        f"**📄 Title:** {movie_info.get('Title')}\n"
        f"**👁‍🗨 Released:** {movie_info.get('Released')}\n"
        f"**🕐 Time:** {runtime}\n"
        f"**🎨 Genre:** {movie_info.get('Genre')}\n"
        f"**🤵‍♂️ Director:** {movie_info.get('Director')}\n"
        f"**🧑‍💻 Writer:** {movie_info.get('Writer')}\n"
        f"**👫 Actors:** {movie_info.get('Actors')}\n"
        f"**🗣 Language:** {movie_info.get('Language')}\n"
        f"**🌐 Country:** {movie_info.get('Country')}\n"
        f"**🏆 Awards:** {movie_info.get('Awards')}\n"
        f"**🎯 Meta Score:** {movie_info.get('Metascore')}\n"
        f"**🎯 IMDB Rating:** {movie_info.get('imdbRating')}\n"
        f"**📊 IMDB Votes:** {movie_info.get('imdbVotes')}\n"
        f"**🏷 IMDB ID:** `{movie_info.get('imdbID')}`\n"
        f"**💰 BoxOffice:** {movie_info.get('BoxOffice')}\n\n"
        f"<blockquote expandable>**📝 Plot:** {movie_info.get('Plot')}</blockquote>"
    )

    photo = movie_info.get("Poster")
    if photo:
        await message.reply_photo(photo, caption=text)
    else:
        await message.reply_text(text)
