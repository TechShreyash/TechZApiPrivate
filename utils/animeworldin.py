import json
from bs4 import BeautifulSoup as bs
import time

LATEST_CACHE = {}
SEARCH_CACHE = {"query": {}}
ANIME_CACHE = {}
EPISODE_CACHE = {}
EPISODE_LINK_CACHE = {}
STREAM_LINK_CACHE = {}


class AnimeWorldIN:
    def __init__(self, session) -> None:
        self.host = "anime-world.in"
        self.session = session

    async def search(self, query):
        global SEARCH_CACHE

        if query in SEARCH_CACHE.get("query", {}):
            print("from cache")
            return SEARCH_CACHE["query"][query]

        if time.time() - SEARCH_CACHE.get("time", 0) < 60 * 60:
            SEARCH_CACHE = {"time": time.time(), "query": {}}

        async with self.session.get(
            f"https://{self.host}/advanced-search/?s_keyword=" + query
        ) as resp:
            soup = bs(
                await resp.text(),
                "html.parser",
            )
        animes = soup.find_all("div", "col-span-1")

        results = []
        for i in animes:
            id = i.find("a").get("href").strip(" /").split("/")[-1].strip()
            img = "https://anime-world.in" + i.find("img").get("src").strip()
            title = i.find("a", "text-sm").text.strip()
            types, duration = i.find_all("span", "md:my-1")
            types = types.text.strip()
            duration = duration.text.strip()
            results.append(
                {
                    "id": id,
                    "img": img,
                    "title": title,
                    "type": types,
                    "duration": duration,
                }
            )

        if len(results) != 0:
            SEARCH_CACHE["query"][query] = results
        return results

    async def anime(self, anime):
        global ANIME_CACHE

        if anime in ANIME_CACHE:
            if time.time() - ANIME_CACHE.get(anime, {}).get("time", 0) < 60 * 60:
                print("from cache")
                return ANIME_CACHE[anime]["results"]

        async with self.session.get(f"https://{self.host}/series/" + anime) as resp:
            soup = bs(
                await resp.text(),
                "html.parser",
            )

        title = soup.find("h2", "text-4xl leading-tight font-medium mb-5").text.strip()
        img = "https://anime-world.in" + (
            soup.find("img", "lg:w-52 md:w-48 h-auto rounded-sm shadow-sm")
            .get("src")
            .strip()
        )

        div = soup.find(
            "section",
            "lg:absolute relative lg:top-0 lg:right-0 w-full py-5 lg:py-0 lgmax-w-xs bottom-0 bg-white bg-opacity-10 lg:w-79 space-y-1 flex flex-col justify-center text-sm font-medium px-7",
        )
        synopsis = div.find(
            "span",
            "block w-full max-h-24 overflow-scroll my-3 overflow-x-hidden text-xs text-gray-200",
        ).text

        data = {"id": anime, "title": title, "img": img, "synopsis": synopsis}

        info = div.find_all("li", "list-none mb-1")
        for i in info:
            x, y = i.find_all("span")
            data[x.text.strip()] = y.text.strip()

        genre = div.find(
            "li",
            "list-none py-2 my-4 border-t border-b border-white border-opacity-25",
        ).find_all("a")
        x = []
        for i in genre:
            x.append(i.text.strip())
        data["genre"] = x

        if len(data) != 0:
            ANIME_CACHE[anime] = {"time": time.time(), "results": data}
        return data

    async def get_episodes(self, anime):
        global EPISODE_CACHE

        if anime in EPISODE_CACHE:
            if time.time() - EPISODE_CACHE.get(anime, {}).get("time", 0) < 60 * 60:
                print("from cache")
                return EPISODE_CACHE[anime]["results"]

        async with self.session.get(f"https://{self.host}/series/{anime}") as resp:
            html = await resp.text()
            soup = bs(
                html,
                "html.parser",
            )

        img = (
            soup.find("img", "lg:w-52 md:w-48 h-auto rounded-sm shadow-sm")
            .get("src")
            .strip()
        )

        a = html.find("var season_list =") + 17
        b = html.find("var season_label =")
        html = '{"data":' + html[a:b].strip()[:-1] + "}"

        data = json.loads(html)["data"]

        for i in data:
            if i["featured"] == img:
                epdata = i["episodes"]["all"]
                if len(epdata) != 0:
                    EPISODE_CACHE[anime] = {"time": time.time(), "results": epdata}
                return epdata

    async def episode(self, id):
        global EPISODE_LINK_CACHE

        if id in EPISODE_LINK_CACHE:
            if time.time() - EPISODE_LINK_CACHE.get(id, {}).get("time", 0) < 60 * 10:
                print("from cache")
                return EPISODE_LINK_CACHE[id]["results"]

        async with self.session.get(
            f"https://anime-world.in/wp-json/kiranime/v1/episode?id={id}"
        ) as resp:
            data = (await resp.json())["players"]

        if len(data) != 0:
            EPISODE_LINK_CACHE[id] = {"time": time.time(), "results": data}
        return data

    async def stream(self, link):
        global STREAM_LINK_CACHE

        if link in STREAM_LINK_CACHE:
            if time.time() - STREAM_LINK_CACHE.get(id, {}).get("time", 0) < 60:
                print("from cache")
                return STREAM_LINK_CACHE[id]["results"]

        async with self.session.get(link) as resp:
            html = (await resp.text()).replace("\n", " ")

        while " " in html:
            html = html.replace(" ", "")

        html = html[html.find("$(document).ready(function(){sniff(") + 37 :]
        html = html[html.find('","') + 3 :]
        html = html[: html.find('",')]

        url = f"https://awstream.net/m3u8/{html}/master.txt?s=1&cache=1"
        data = {"m3u8": url, "stream": f"https://home.animedex.live/embed?file={url}"}

        if len(html) != 0:
            STREAM_LINK_CACHE[link] = {"time": time.time(), "results": data}
        return data


# import asyncio, aiohttp


# async def main():
#     ses = aiohttp.ClientSession()
#     print((await AnimeWorldIN(ses).stream("https://awstream.net/watch?v=h3XUMNUw0w")))
#     await ses.close()


# print(asyncio.run(main()))
