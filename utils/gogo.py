from bs4 import BeautifulSoup as bs
import aiohttp


def format_url(url):
    if not url.startswith("https"):
        url = "https:" + url
    return url.replace("mixdrop.co", "mixdrop.ch").replace("dood.wf", "dood.yt")


class GoGoApi:
    def __init__(self, session) -> None:
        self.host = "www1.gogoanime.bid"
        self.session = session

    async def latest(self, page=1):
        async with self.session.get(f"https://{self.host}?page={page}") as resp:
            soup = bs(await resp.read(), "html.parser")
        div = soup.find("ul", "items")
        animes = div.find_all("li")

        results = []
        for i in animes:
            id = i.find("a").get("href").replace("/category/", "").strip(" /")
            img = i.find("img").get("src").strip()
            lang = i.find("div", "type").get("class")[1].replace("ic-", "").strip()
            title = i.find("a").get("title").strip()
            episode = i.find("p", "episode").text.replace("Episode", "").strip()
            results.append(
                {"id": id, "img": img, "title": title, "lang": lang, "episode": episode}
            )

        return results

    async def search(self, query):
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
        return results

    async def anime(self, anime):
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

    async def episode(self, id):
        data = {}
        async with self.session.get(f"https://{self.host}/{id}") as resp:
            soup = bs(await resp.read(), "html.parser")

        div = soup.find("div", "anime_muti_link")
        a = div.find_all("a")
        embeds = []

        for i in a:
            url = i.get("data-video")
            url = format_url(url)
            embeds.append(url)

        dlink = soup.find("li", "dowloads").find("a").get("href")

        if "dub" in id:
            data["DUB"] = embeds
            data["DL"] = {}
            data["DL"]["DUB"] = dlink
            id = id.replace("-dub", "")

            async with self.session.get(f"https://{self.host}/{id}") as resp:
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

            dlink = soup.find("li", "dowloads").find("a").get("href")
            data["SUB"] = embeds
            data["DL"]["SUB"] = dlink
            return data

        else:
            data["SUB"] = embeds
            data["DL"] = {}
            data["DL"]["SUB"] = dlink
            id = (
                id.split("-episode-")[0]
                + "-dub"
                + "-episode-"
                + id.split("-episode-")[1]
            )

            async with self.session.get(f"https://{self.host}/{id}") as resp:
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
            dlink = soup.find("li", "dowloads").find("a").get("href")
            data["DUB"] = embeds
            data["DL"]["DUB"] = dlink
            return data
