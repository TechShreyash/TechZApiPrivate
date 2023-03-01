from typing import Literal
from fastapi import FastAPI
from utils.extractor.gogo_extractor import get_m3u8
from utils.gogo import GoGoApi
from utils.wallflare import WallFlare
from utils.unsplash import Unsplash
from utils.logo import generate_logo
from utils.lyrics import get_lyrics
from utils.nyaa import Nyaasi
from utils.ud import get_urbandict
from utils.db import DB
from fastapi.responses import RedirectResponse, FileResponse

from utils.extra import download
import aiohttp

app = FastAPI()

session = None


@app.on_event("startup")
async def startup_event():
    print("Creating Aiohttp Session")
    global session
    session = aiohttp.ClientSession()


@app.on_event("shutdown")
async def shutdown_event():
    await session.close()


@app.get("/")
async def home():
    return {
        "status": "TechZBots - Api working fine...",
        "documentation": "/docs",
    }


# Wallpaperflare.com


@app.get("/wall/search")
async def search_wall(api_key: str, query: str, page: int = 1, max: int = 10):
    """Search wallpapers on wallpaperflare.com

    - api_key: Your api key
    - query: Search query
    - page: Page number (default: 1)

    Price: 2 credits"""
    if not await DB.is_user(api_key):
        return {"success": False, "error": "Invalid api key"}

    try:
        await DB.reduce_credits(api_key, 2)
    except Exception as e:
        return {"success": False, "error": str(e)}

    data = await WallFlare(session).search(query, page, max)
    return data


@app.get("/wall/download")
async def download_wall(api_key: str, id: str):
    """Get download link of wallpaper from wallpaperflare.com

    - id : Get from /wall/search

    Price: 1 credits"""
    if not await DB.is_user(api_key):
        return {"success": False, "error": "Invalid api key"}

    try:
        await DB.reduce_credits(api_key, 1)
    except Exception as e:
        return {"success": False, "error": str(e)}

    data = await WallFlare(session).download_link(id)
    return data


# Unsplash.com


@app.get("/unsplash/search")
async def search_unsplash(api_key: str, query: str, max: int = 10):
    """Search images on unsplash.com

    - query: Search query

    Price: 2 credits"""
    if not await DB.is_user(api_key):
        return {"success": False, "error": "Invalid api key"}

    try:
        await DB.reduce_credits(api_key, 2)
    except Exception as e:
        return {"success": False, "error": str(e)}

    data = await Unsplash(session).search(query, max)
    return data


# Logo Maker


@app.get("/logo")
async def logo_maker(
    api_key: str,
    text: str,
    img: str | None = None,
    bg: Literal["wallflare", "unsplash"] = "wallflare",
    square: bool = False,
):
    """Generate cool logos

    - text: Text to be displayed on logo
    - img: Direct url of image to be used as background
    - bg: Get background from - wallflare or unsplash (default: wallflare)
    - square: True to make square logos (default: False)

    Price: 5 credits"""
    if not await DB.is_user(api_key):
        return {"success": False, "error": "Invalid api key"}

    try:
        await DB.reduce_credits(api_key, 5)
    except Exception as e:
        return {"success": False, "error": str(e)}

    if img:
        try:
            img = await download(session, img)
        except Exception as e:
            print(e)
            return {"success": False, "error": "Invalid image url"}
    data = await generate_logo(session, text, img, bg, square)
    return FileResponse(data)


# Lyrics


@app.get("/lyrics/search")
async def search_lyrics(api_key: str, query: str):
    """Search lyrics of songs

    - query: Search query

    Price: 1 credits"""
    if not await DB.is_user(api_key):
        return {"success": False, "error": "Invalid api key"}

    try:
        await DB.reduce_credits(api_key, 1)
    except Exception as e:
        return {"success": False, "error": str(e)}

    data = await get_lyrics(query)
    return data


# nyaa.si


@app.get("/nyaasi/latest")
async def nyaasi_latest(api_key: str, max: int = 10):
    """Get latest uploads from nyaasi

    - max: Max posts to get

    Price: 1 credits"""
    if not await DB.is_user(api_key):
        return {"success": False, "error": "Invalid api key"}

    try:
        await DB.reduce_credits(api_key, 1)
    except Exception as e:
        return {"success": False, "error": str(e)}

    data = await Nyaasi.get_nyaa_latest()
    return data


@app.get("/nyaasi/info")
async def nyaasi_info(api_key: str, id: int):
    """Get info of a file from nyaasi

    Price: 1 credits"""
    if not await DB.is_user(api_key):
        return {"success": False, "error": "Invalid api key"}

    try:
        await DB.reduce_credits(api_key, 1)
    except Exception as e:
        return {"success": False, "error": str(e)}

    data = await Nyaasi(session).get_nyaa_info(id)
    return data


# Urban Dictionary


@app.get("/ud/search")
async def search_ud(api_key: str, query: str, max: int = 10):
    """Search meanings of words on Urban Dictionary

    - query: Word whose meaning you want
    - max: Max definitions to get

    Price: 1 credits"""
    if not await DB.is_user(api_key):
        return {"success": False, "error": "Invalid api key"}

    try:
        await DB.reduce_credits(api_key, 1)
    except Exception as e:
        return {"success": False, "error": str(e)}

    data = await get_urbandict(session, query, max)
    return data


# Gogoanime


@app.get("/gogo/latest")
async def gogo_latest(api_key: str, page: int = 1):
    """Get latest released animes from gogoanime

    - page: Page number (default: 1)

    Price: 1 credits"""
    if not await DB.is_user(api_key):
        return {"success": False, "error": "Invalid api key"}

    try:
        await DB.reduce_credits(api_key, 1)
    except Exception as e:
        return {"success": False, "error": str(e)}

    data = await GoGoApi(session).latest(page)
    return {"success": True, "results": data}


@app.get("/gogo/search")
async def gogo_search(api_key: str, query: str):
    """Search animes on gogoanime

    - query: Search query

    Price: 1 credits"""
    if not await DB.is_user(api_key):
        return {"success": False, "error": "Invalid api key"}

    try:
        await DB.reduce_credits(api_key, 1)
    except Exception as e:
        return {"success": False, "error": str(e)}

    data = await GoGoApi(session).search(query)
    return {"success": True, "results": data}


@app.get("/gogo/anime")
async def gogo_anime(api_key: str, id: str):
    """Get anime info from gogoanime

    - id : Anime id, Ex : horimiya-dub

    Price: 1 credits"""
    if not await DB.is_user(api_key):
        return {"success": False, "error": "Invalid api key"}

    try:
        await DB.reduce_credits(api_key, 1)
    except Exception as e:
        return {"success": False, "error": str(e)}

    data = await GoGoApi(session).anime(id)
    return {"success": True, "results": data}


@app.get("/gogo/episode")
async def gogo_episode(api_key: str, id: str):
    """Get episode embed links from gogoanime

    - id : Episode id, Ex : horimiya-dub-episode-3

    Price: 1 credits"""
    if not await DB.is_user(api_key):
        return {"success": False, "error": "Invalid api key"}

    try:
        await DB.reduce_credits(api_key, 1)
    except Exception as e:
        return {"success": False, "error": str(e)}

    data = await GoGoApi(session).episode(id)
    return {"success": True, "results": data}


@app.get("/gogo/stream")
async def gogo_stream(api_key: str, url: str):
    """Get episode stream links (m3u8) from gogoanime

    - url : Episode url, Ex : https://anihdplay.com/streaming.php?id=MTUyODYy&title=Horimiya+%28Dub%29+Episode+3

    Price: 2 credits"""
    if not await DB.is_user(api_key):
        return {"success": False, "error": "Invalid api key"}

    try:
        await DB.reduce_credits(api_key, 2)
    except Exception as e:
        return {"success": False, "error": str(e)}

    data = await get_m3u8(session, url)
    return {"success": True, "results": data}
