from bs4 import BeautifulSoup as bs
import PyBypass
import time
import asyncio
import aiohttp
import json
import base64
import re


LATEST_CACHE = {}
SEARCH_CACHE = {"query": {}}
ANIME_CACHE = {}
CLOUDFLARE_CACHE = {}


class TPXAnime:
    def __init__(self, session) -> None:
        self.host = "hindisub.com"
        self.session = session

    async def latest(self, page=1):
        if (await self.isCloudflareUP()) is True:
            return "Cloudflare is up on the site. Please try again later."

        global LATEST_CACHE

        if page in LATEST_CACHE:
            if time.time() - LATEST_CACHE.get(page, {}).get("time", 0) < 60 * 5:
                print("from cache")
                return LATEST_CACHE[page]["results"]

        async with self.session.get(f"https://hindisub.com/page/{page}") as resp:
            soup = bs(
                await resp.text(),
                "html.parser",
            )
        animes = soup.find_all("article")
        results = []

        for i in animes:
            id = i.find("a").get("href").split("/")[3]
            img = (
                i.find("img").get("srcset") or i.find("img").get("data-srcset")
            ).strip()
            imgs = {}
            for q in img.split(","):
                x, y = q.strip().split(" ")
                imgs[y.replace("w", "")] = x
            title = i.find("h2", "entry-title").text.strip()
            updated_on = i.find("span", "updated").text.strip()
            results.append(
                {"id": id, "img": imgs, "title": title, "updated_on": updated_on}
            )

        if len(results) != 0:
            LATEST_CACHE[page] = {"time": time.time(), "results": results}
        return results

    async def search(self, query):
        if (await self.isCloudflareUP()) is True:
            return "Cloudflare is up on the site. Please try again later."
        global SEARCH_CACHE

        if query in SEARCH_CACHE.get("query", {}):
            print("from cache")
            return SEARCH_CACHE["query"][query]

        if time.time() - SEARCH_CACHE.get("time", 0) < 60 * 60:
            SEARCH_CACHE = {"time": time.time(), "query": {}}

        async with self.session.get(f"https://{self.host}/?s=" + query) as resp:
            soup = bs(
                await resp.text(),
                "html.parser",
            )
        animes = soup.find_all("article")

        results = []
        for i in animes:
            id = i.find("a").get("href").split("/")[3]
            img = (
                i.find("img").get("srcset") or i.find("img").get("data-srcset")
            ).strip()

            imgs = {}
            for q in img.split(","):
                x, y = q.strip().split(" ")
                imgs[y.replace("w", "")] = x

            title = i.find("h2", "entry-title").text.strip()
            updated_on = i.find("span", "updated").text.strip()
            results.append(
                {"id": id, "img": imgs, "title": title, "updated_on": updated_on}
            )

        if len(results) != 0:
            SEARCH_CACHE["query"][query] = results
        return results

    async def anime(self, anime):
        if (await self.isCloudflareUP()) is True:
            return "Cloudflare is up on the site. Please try again later."
        global ANIME_CACHE

        if anime in ANIME_CACHE:
            if time.time() - ANIME_CACHE.get(anime, {}).get("time", 0) < 60 * 60:
                print("from cache")
                return ANIME_CACHE[anime]["results"]

        async with self.session.get(f"https://{self.host}/" + anime) as resp:
            soup = bs(
                await resp.text(),
                "html.parser",
            )

        title = soup.find("h1", "entry-title").text
        img = soup.find("div", "herald-post-thumbnail").find("img")
        img = img.get("srcset") or img.get("data-srcset")

        imgs = {}
        for q in img.split(","):
            x, y = q.strip().split(" ")
            imgs[y.replace("w", "")] = x

        data = {"id": anime, "title": title, "img": imgs}

        info = soup.find("div", "entry-content").find_all("p")
        a = False
        z = False

        for i in info:
            i = i.text.strip()

            if a is False:
                if "name" in i.lower():
                    a = True
                else:
                    continue

            x = i.split(":")[0].strip().lower()
            print(x)

            y = " ".join(i.split(":")[1:]).strip(" -,")
            if z is True:
                x = "synopsis"
                data[x] = i
                break
            else:
                data[x] = y

            if x == "genre":
                z = True

        if len(data) != 0:
            ANIME_CACHE[anime] = {"time": time.time(), "results": data}
        return data

    async def bypass(self, url):
        err = 0
        while err < 10:
            try:
                async with self.session.get(url) as resp:
                    html = await resp.text()

                url = re.search(
                    r".*?document\.location\.href\s*=\s*\'([^']+)\'", html
                ).group(1)
                bypassed = PyBypass.bypass(url)
                return bypassed
            except Exception as e:
                print(e)
                err += 1
                continue

    async def isCloudflareUP(self):
        global CLOUDFLARE_CACHE

        if time.time() - CLOUDFLARE_CACHE.get("time", 0) < 60 * 10:
            return CLOUDFLARE_CACHE["status"]

        async with self.session.get(
            "https://api.github.com/repos/TechShreyash/TechShreyash/contents/tpx.txt"
        ) as resp:
            a = (await resp.json())["content"].strip()

        a = base64.b64decode(a).decode("utf-8")
        if "up" in a:
            CLOUDFLARE_CACHE = {"time": time.time(), "status": True}
            return True
        else:
            CLOUDFLARE_CACHE = {"time": time.time(), "status": False}
            return False


# async def main():
#     ses = aiohttp.ClientSession()
#     print(
#         (
#             await TPXAnime(ses).bypass(
#                 "https://links.hindisub.com/redirect/main2.php?url=f41616t5k40314s2v44646s2r5p5m4q4i4l4c444s216l434b4m5l494p4v214l303f3p3p323o3n2x3m4v5q5o524p4f5r2v374q4q33414e3k3b3p2k4g4y2g5i4p5j4o5s4"
#             )
#         )
#     )
#     await ses.close()


# print(asyncio.run(main()))
