import asyncio
import requests
import feedparser
import aiohttp
from bs4 import BeautifulSoup as bs


class Nyaasi:
    def __init__(self, session):
        self.session = session

    async def get_nyaa_info(self, code):
        r = self.session
        x = await r.get(f"https://nyaa.si/view/{code}")
        x = (await x.text()).replace("\t", "").replace("\n", "")
        s = bs(x, "html.parser")
        title = s.find_all("h3", attrs={"class": "panel-title"})[0]
        link = s.find_all("a", attrs={"class": "card-footer-item"})[0].get("href")
        d1 = s.find_all("div", attrs={"class": "col-md-1"})
        d2 = s.find_all("div", attrs={"class": "col-md-5"})
        title = str(title.string)
        title = title[4:]
        inf = []
        for t in d1:
            num = d1.index(t)
            t = t.string
            t = t[:-1]
            y = d2[num]
            if y.span:
                y = y.span.string
            elif y.a:
                y = y.a.string
            else:
                y = y.string
            sq = [t, y]
            inf.append(sq)
            try:
                if "Information" in t:
                    inf.remove([t, y])
                else:
                    pass
            except:
                pass
        json = {}
        json["success"] = True
        results = {}
        results["title"] = title
        for a in inf:
            results[f"{a[0]}"] = a[1].strip()
        results["magnet"] = link
        json["results"] = results
        return json

    async def get_nyaa_latest(max=10):
        data = feedparser.parse("https://nyaa.si/?page=rss")
        data = data.entries[:max]
        json = {}
        json["success"] = True
        result = []

        for i in data:
            dict = {}

            code = str(i.get("link")).replace(".torrent", "").split("/")[-1]
            dict["title"] = i.get("title")
            dict["seeders"] = i.get("nyaa_seeders")
            dict["leechers"] = i.get("nyaa_leechers")
            dict["downloads"] = i.get("nyaa_downloads")
            dict["infohash"] = i.get("nyaa_infohash")
            dict["category"] = i.get("nyaa_category")
            dict["size"] = i.get("nyaa_size")
            dict["link"] = i.get("id")
            dict["torrent"] = i.get("link")
            dict["published"] = i.get("published")

            result.append(dict)

        json["results"] = result
        return json
