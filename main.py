from typing import Literal
from fastapi import FastAPI
from utils.wallflare import WallFlare
from utils.unsplash import Unsplash
from utils.logo import generate_logo
from utils.lyrics import get_lyrics
from utils.nyaa import Nyaasi
from utils.ud import get_urbandict
from fastapi.responses import RedirectResponse, FileResponse

from utils.extra import download

app = FastAPI()


@app.get("/")
async def home():
    return {
        "status": "TechZBots - Api working fine...",
        "docs": "https://techzbots-api.herokuapp.com/docs",
    }


# Wallpaperflare.com


@app.get("/wall/search")
async def search_wall(query: str, page: int = 1, max: int = 10):
    """Search wallpapers on wallpaperflare.com

    - query: Search query
    - page: Page number (default: 1)"""
    data = await WallFlare.search(query, page, max)
    return data


@app.get("/wall/download")
async def download_wall(id: str):
    """Get download link of wallpaper from wallpaperflare.com

    - id : Get from /wall/search"""
    data = await WallFlare.download_link(id)
    return data


# Unsplash.com


@app.get("/unsplash/search")
async def search_unsplash(query: str, max: int = 10):
    """Search images on unsplash.com

    - query: Search query"""
    data = await Unsplash.search(query, max)
    return data


# Logo Maker


@app.get("/logo")
async def search_unsplash(
    text: str,
    img: str | None = None,
    bg: Literal["wallflare", "unsplash"] = "wallflare",
    square: bool = False,
):
    """Generate cool logos

    - text: Text to be displayed on logo
    - img: Direct url of image to be used as background
    - bg: Get background from - wallflare or unsplash (default: wallflare)
    - square: True to make square logos (default: False)"""
    if img:
        try:
            img = await download(img)
        except Exception as e:
            print(e)
            return {"success": "False", "error": "Invalid image url"}
    data = await generate_logo(text, img, bg, square)
    return FileResponse(data)


# Lyrics


@app.get("/lyrics/search")
async def search_lyrics(query: str):
    """Search lyrics of songs

    - query: Search query"""
    data = await get_lyrics(query)
    return data


# nyaa.si


@app.get("/nyaasi/latest")
async def nyaasi_latest(max: int = 10):
    """Get latest uploads from nyaasi

    - max: Max posts to get"""
    data = await Nyaasi.get_nyaa_latest()
    return data


@app.get("/nyaasi/info")
async def nyaasi_info(code: int):
    """Get info of a file from nyaasi"""
    data = await Nyaasi.get_nyaa_info(code)
    return data


# Urban Dictionary


@app.get("/ud/search")
async def search_ud(query: str, max: int = 10):
    """Search meanings of words on Urban Dictionary

    - query: Word whose meaning you want
    - max: Max definitions to get"""
    data = await get_urbandict(query, max)
    return data
