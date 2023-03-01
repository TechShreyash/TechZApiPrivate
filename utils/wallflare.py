import asyncio
import random
import aiohttp
from bs4 import BeautifulSoup as bs
import urllib


class WallFlare:
    def __init__(self, session):
        self.session = session

    async def home(self):
        url = "https://www.wallpaperflare.com"

        async with self.session.get(url) as resp:
            soup = bs(await resp.read(), "html.parser")
            li = soup.find_all("li", {"itemprop": "associatedMedia"})
            print(len(li))
        wall_list = []
        for i in li:
            if i.find("img"):
                if i.find("img").get("data-src"):
                    wall_list.append(
                        {
                            "id": i.find("a")
                            .get("href")
                            .replace("https://www.wallpaperflare.com/", "")
                            .strip(),
                            "preview": i.find("img").get("data-src"),
                        }
                    )
        random.shuffle(wall_list)
        return {"success": True, "results": wall_list}

    async def search(self, query, page, max=10):
        url = (
            "https://www.wallpaperflare.com/search?wallpaper="
            + urllib.parse.quote_plus(query.replace(" ", "+") + f"&page={page}")
        )

        async with self.session.get(url) as resp:
            soup = bs(await resp.read(), "html.parser")
            li = soup.find_all("li", {"itemprop": "associatedMedia"})
            print(len(li))
        li = li[:max]
        wall_list = []
        for i in li:
            if i.find("img"):
                if i.find("img").get("data-src"):
                    wall_list.append(
                        {
                            "id": i.find("a")
                            .get("href")
                            .replace("https://www.wallpaperflare.com/", "")
                            .strip(),
                            "preview": i.find("img").get("data-src"),
                        }
                    )
        random.shuffle(wall_list)
        return {"success": True, "results": wall_list}

    async def download_link(self, id):
        url = f"https://www.wallpaperflare.com/{id}/download"

        async with self.session.get(url) as resp:
            soup = bs(await resp.text(), "html.parser")
            img = soup.find("img", {"id": "show_img"}).get("src")
            return {"success": True, "url": img}
