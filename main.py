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
from fastapi.responses import FileResponse
from fastapi.openapi.utils import get_openapi
from utils.extra import download
from utils.tpxanime import TPXAnime
import aiohttp

app = FastAPI()

session = []
AIO_SESSIONS = 5


def get_session():
    session.sort(key=lambda i: i[1])
    ses = session[0]
    for i in session:
        if i == ses:
            session[session.index(i)][1] += 1

    return ses[0]


@app.on_event("startup")
async def startup_event():
    app.openapi_schema = get_openapi(
        title="TechZApi",
        version="1.3",
        description="Use powerfull api features provided by TechZBots",
        routes=app.routes,
    )

    print("Creating Aiohttp Sessions...")
    global session
    for i in range(AIO_SESSIONS):
        session.append([aiohttp.ClientSession(), 0])


@app.on_event("shutdown")
async def shutdown_event():
    for i in session:
        await i[0].close()


@app.get("/", name="home", tags=["Home"])
async def home():
    return {
        "status": "TechZBots - Api working fine...",
        "documentation": "/docs",
    }


# Wallpaperflare.com


@app.get("/wall/search", name="search wallflare", tags=["Wallpapers / Images"])
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

    data = await WallFlare(get_session()).search(query, page, max)
    return data


@app.get("/wall/download", name="download wallflare", tags=["Wallpapers / Images"])
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

    data = await WallFlare(get_session()).download_link(id)
    return data


# Unsplash.com


@app.get("/unsplash/search", name="search unsplash", tags=["Wallpapers / Images"])
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

    data = await Unsplash(get_session()).search(query, max)
    return data


# Logo Maker


@app.get("/logo", name="logo maker", tags=["Logo Maker"])
async def logo_maker(
    api_key: str,
    text: str,
    img: str = None,
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
            img = await download(get_session(), img)
        except Exception as e:
            print(e)
            return {"success": False, "error": "Invalid image url"}
    data = await generate_logo(get_session(), text, img, bg, square)
    return FileResponse(data)


# Lyrics


@app.get("/lyrics/search", name="search lyrics", tags=["Extra"])
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


@app.get("/nyaasi/latest", name="nyaasi latest", tags=["Nyaasi"])
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


@app.get("/nyaasi/info", name="nyaasi info", tags=["Nyaasi"])
async def nyaasi_info(api_key: str, id: int):
    """Get info of a file from nyaasi

    Price: 1 credits"""
    if not await DB.is_user(api_key):
        return {"success": False, "error": "Invalid api key"}

    try:
        await DB.reduce_credits(api_key, 1)
    except Exception as e:
        return {"success": False, "error": str(e)}

    data = await Nyaasi(get_session()).get_nyaa_info(id)
    return data


# Urban Dictionary


@app.get("/ud/search", name="search ud", tags=["Extra"])
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

    data = await get_urbandict(get_session(), query, max)
    return data


# Gogoanime


@app.get("/gogo/latest", name="gogo latest", tags=["Gogo Anime"])
async def gogo_latest(api_key: str, page: int = 1):
    """Get latest released animes from gogoanime

    - page: Page number (default: 1)

    Price: 1 credits"""
    if not await DB.is_user(api_key):
        return {"success": False, "error": "Invalid api key"}

    try:
        await DB.reduce_credits(api_key, 1)
    except Exception as e:
        pass

    data = await GoGoApi(get_session()).latest(page)
    return {"success": True, "results": data}


@app.get("/gogo/search", name="gogo search", tags=["Gogo Anime"])
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

    data = await GoGoApi(get_session()).search(query)
    return {"success": True, "results": data}


@app.get("/gogo/anime", name="gogo anime", tags=["Gogo Anime"])
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

    data = await GoGoApi(get_session()).anime(id)
    return {"success": True, "results": data}


@app.get("/gogo/episode", name="gogo episode", tags=["Gogo Anime"])
async def gogo_episode(
    api_key: str, id: str, lang: Literal["sub", "dub", "both", "any"] = "sub"
):
    """Get episode embed links from gogoanime

    - id : Episode id, Ex : horimiya-dub-episode-3
    - lang : sub | dub | both | any

    Price: 1 credits for sub and dub, 2 credits for both"""
    if not await DB.is_user(api_key):
        return {"success": False, "error": "Invalid api key"}

    try:
        await DB.reduce_credits(api_key, 2 if lang == "both" else 1)
    except Exception as e:
        return {"success": False, "error": str(e)}

    data = await GoGoApi(get_session()).episode(id, lang)
    return {"success": True, "results": data}


@app.get("/gogo/stream", name="gogo stream", tags=["Gogo Anime"])
async def gogo_stream(api_key: str, url: str):
    """Get episode stream links (m3u8) from gogoanime

    - url : Episode url, Ex : https://anihdplay.com/streaming.php?id=MTUyODYy&title=Horimiya+%28Dub%29+Episode+3

    Price: 1 credits"""
    if not await DB.is_user(api_key):
        return {"success": False, "error": "Invalid api key"}

    try:
        await DB.reduce_credits(api_key, 1)
    except Exception as e:
        return {"success": False, "error": str(e)}

    data = await get_m3u8(get_session(), url)
    return {"success": True, "results": data}


@app.get("/tpx/latest", name="tpx latest", tags=["TPX Anime"])
async def tpx_latest(api_key: str, page: int = 1):
    """Get latest released animes from TPX Anime (hindisub.in)

    - page: Page number (default: 1)

    Price: 5 credits"""
    if not await DB.is_user(api_key):
        return {"success": False, "error": "Invalid api key"}

    try:
        await DB.reduce_credits(api_key, 1)
    except Exception as e:
        return {"success": False, "error": str(e)}

    try:
        data = await TPXAnime(get_session()).latest(page)
        return {"success": True, "results": data}
    except Exception as e:
        return FileResponse('image.png')
