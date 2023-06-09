from bs4 import BeautifulSoup as bs
import requests
import time


def format_url(url):
    if not url.startswith("https"):
        url = "https:" + url
    return url.replace("mixdrop.co", "mixdrop.ch").replace("dood.wf", "dood.yt")


Gcookie = {}
LATEST_CACHE = {}
SEARCH_CACHE = {"query": {}}
ANIME_CACHE = {}


class GoGoApi:
    def __init__(self, session) -> None:
        self.host = "gogoanime.hu"
        self.session = session

    async def latest(self, page=1):
        global LATEST_CACHE

        if page in LATEST_CACHE:
            if time.time() - LATEST_CACHE.get(page, {}).get("time", 0) < 60 * 5:
                print("from cache")
                return LATEST_CACHE[page]["results"]

        async with self.session.get(f"https://{self.host}?page={page}") as resp:
            soup = bs(await resp.read(), "html.parser")
        div = soup.find("ul", "items")
        animes = div.find_all("li")

        results = []
        for i in animes:
            id = i.find("a").get("href").strip("/")
            img = i.find("img").get("src").strip()
            lang = i.find("div", "type").get("class")[1].replace("ic-", "").strip()
            title = i.find("a").get("title").strip()
            episode = i.find("p", "episode").text.replace("Episode", "").strip()
            results.append(
                {"id": id, "img": img, "title": title, "lang": lang, "episode": episode}
            )

        if len(results) != 0:
            LATEST_CACHE[page] = {"time": time.time(), "results": results}
        return results

    async def search(self, query):
        global SEARCH_CACHE

        if query in SEARCH_CACHE.get("query", {}):
            print("from cache")
            return SEARCH_CACHE["query"][query]

        if time.time() - SEARCH_CACHE.get("time", 0) < 60 * 60:
            SEARCH_CACHE = {"time": time.time(), "query": {}}

        async with self.session.get(
            f"https://{self.host}/search.html?keyword=" + query
        ) as resp:
            soup = bs(
                await resp.text(),
                "html.parser",
            )
        div = soup.find("ul", "items")
        animes = div.find_all("li")

        results = []
        for i in animes:
            id = i.find("a").get("href").replace("/category/", "").strip()
            img = i.find("img").get("src").strip()
            title = i.find("p", "name").text.strip()
            released = i.find("p", "released").text.replace("Released:", "").strip()
            results.append({"id": id, "img": img, "title": title, "year": released})

        if len(results) != 0:
            SEARCH_CACHE["query"][query] = results
        return results

    async def anime(self, anime):
        global ANIME_CACHE

        if anime in ANIME_CACHE:
            if time.time() - ANIME_CACHE.get(anime, {}).get("time", 0) < 60 * 60:
                print("from cache")
                return ANIME_CACHE[anime]["results"]

        async with self.session.get(f"https://{self.host}/category/" + anime) as resp:
            soup = bs(
                await resp.text(),
                "html.parser",
            )

        if soup.find("title").text == "Pages not found":
            raise Exception("Anime not found")

        title = soup.find("h1").text

        total, episodes = await self._get_episodes(anime)

        img = soup.find("div", "anime_info_body_bg").find("img").get("src")

        if "dub" in anime.lower():
            dub = "DUB"
        else:
            dub = "SUB"

        data = {
            "id": anime,
            "title": title,
            "img": img,
            "lang": dub,
            "total_ep": total,
            "episodes": episodes,
        }

        types = soup.find_all("p", "type")
        for i in types:
            i = i.text.strip()
            x = i.split(":")[0].strip().lower()

            if x == "plot summary":
                x = "summary"
            if x == "released":
                x = "year"

            y = " ".join(i.split(":")[1:]).strip()
            data[x] = y

        if len(data) != 0:
            ANIME_CACHE[anime] = {"time": time.time(), "results": data}
        return data

    async def _get_episodes(self, anime):
        async with self.session.get(f"https://{self.host}/category/{anime}") as resp:
            soup = bs(await resp.read(), "html.parser")
            anime_id = soup.find("input", "movie_id").get("value")

        async with self.session.get(
            f"https://ajax.gogo-load.com/ajax/load-list-episode?ep_start=0&ep_end=100000&id={anime_id}"
        ) as resp:
            html = bs(
                await resp.read(),
                "html.parser",
            )

        li = html.find_all("li")
        eps = []
        for i in li:
            a = i.find("a").get("href").strip()[1:]
            eps.append(a)
        eps.reverse()
        return len(li), eps

    async def episode(self, id, lang):
        global Gcookie
        if "cookie" not in Gcookie:
            Gcookie = {
                "time": time.time(),
                "cookie": self.get_gogo_cookie(
                    "qwertytechz123@gmail.com", "P@8eqB7@YpJz5ea"
                ),
            }

        if time.time() - Gcookie["time"] > 60 * 10:
            Gcookie = {
                "time": time.time(),
                "cookie": self.get_gogo_cookie(
                    "qwertytechz123@gmail.com", "P@8eqB7@YpJz5ea"
                ),
            }
        auth_gogo = Gcookie["cookie"]

        data = {}
        data["DL"] = {}

        async with self.session.get(
            f"https://{self.host}/{id}", cookies={"auth": auth_gogo}
        ) as resp:
            soup = bs(await resp.read(), "html.parser")

        div = soup.find("div", "anime_muti_link")
        a = div.find_all("a")
        embeds = []

        for i in a:
            url = i.get("data-video")
            url = format_url(url)
            embeds.append(url)

        dlinks = soup.find("div", "cf-download").find_all("a")
        dlink = {}
        for i in dlinks:
            x = i.text.split("x")[1].strip() + "p"
            y = i.get("href").strip()
            dlink[x] = y

        if lang == "any":
            return {"embeds": embeds, "dlinks": dlink}

        if "dub" in id:
            if lang == "dub" or lang == "both":
                data["DUB"] = embeds
                data["DL"]["DUB"] = dlink

            if lang == "dub":
                return data

            id = id.replace("-dub", "")

            async with self.session.get(
                f"https://{self.host}/{id}", cookies={"auth": auth_gogo}
            ) as resp:
                soup = bs(await resp.read(), "html.parser")

            error = soup.find("h1", "entry-title")
            if error:
                return data
            div = soup.find("div", "anime_muti_link")
            a = div.find_all("a")
            embeds = []

            for i in a:
                url = i.get("data-video")
                url = format_url(url)
                embeds.append(url)

            dlinks = soup.find("div", "cf-download").find_all("a")
            dlink = {}
            for i in dlinks:
                x = i.text.split("x")[1].strip() + "p"
                y = i.get("href").strip()
                dlink[x] = y

            if lang == "sub" or lang == "both":
                data["SUB"] = embeds
                data["DL"]["SUB"] = dlink
            return data

        else:
            if lang == "sub" or lang == "both":
                data["SUB"] = embeds
                data["DL"]["SUB"] = dlink

            if lang == "sub":
                return data

            id = (
                id.split("-episode-")[0]
                + "-dub"
                + "-episode-"
                + id.split("-episode-")[1]
            )
            print(id)

            async with self.session.get(
                f"https://{self.host}/{id}", cookies={"auth": auth_gogo}
            ) as resp:
                soup = bs(await resp.read(), "html.parser")
            error = soup.find("h1", "entry-title")
            if error:
                return data
            div = soup.find("div", "anime_muti_link")
            a = div.find_all("a")
            embeds = []
            for i in a:
                url = i.get("data-video")
                url = format_url(url)
                embeds.append(url)

            dlinks = soup.find("div", "cf-download").find_all("a")
            dlink = {}
            for i in dlinks:
                x = i.text.split("x")[1].strip() + "p"
                y = i.get("href").strip()
                dlink[x] = y

            if lang == "dub" or lang == "both":
                data["DUB"] = embeds
                data["DL"]["DUB"] = dlink
            return data

    def get_gogo_cookie(self, email, password):
        s = requests.session()
        animelink = "https://gogoanime.hu/login.html"
        response = s.get(animelink)
        response_html = response.text
        soup = bs(response_html, "html.parser")
        source_url = soup.select('meta[name="csrf-token"]')
        token = source_url[0].attrs["content"]

        data = f"email={email}&password={password}&_csrf={token}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 9; vivo 1916) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Mobile Safari/537.36",
            "authority": "gogo-cdn.com",
            "referer": f"https://gogoanime.hu/",
            "content-type": "application/x-www-form-urlencoded",
        }
        s.headers = headers

        r = s.post(animelink, data=data, headers=headers)

        if r.status_code == 200:
            s.close()
            print("Gogoanime cookie generated successfully")
            return s.cookies.get_dict().get("auth")
