import random
from bs4 import BeautifulSoup as bs
import aiohttp


class Unsplash:
    async def search(query, max=10):
        link = "https://unsplash.com/s/photos/" + query.replace(" ", "-")

        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                soup = bs(await resp.text(), "html.parser")
                div = soup.find_all("div", class_="mef9R")

        images = []
        div = div[:max]

        for i in div:
            a = i.find("a").get("href")
            images.append(a)

        random.shuffle(images)
        return {"success": "True", "results": images}
