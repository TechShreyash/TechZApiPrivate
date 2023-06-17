from bs4 import BeautifulSoup as bs
import PyBypass
import time
import asyncio
import aiohttp
import base64
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os


def bypass(url):
    return PyBypass.bypass(url)


LATEST_CACHE = {}
SEARCH_CACHE = {"query": {}}
ANIME_CACHE = {}
CLOUDFLARE_CACHE = {}


class TPXAnime:
    def __init__(self, session) -> None:
        self.host = "hindisub.com"
        self.session = session

    async def latest(self, page=1):
        global LATEST_CACHE

        if page in LATEST_CACHE:
            if time.time() - LATEST_CACHE.get(page, {}).get("time", 0) < 60 * 5:
                print("from cache")
                return LATEST_CACHE[page]["results"]

        if await self.isCloudflareUP():
            chrome_options = Options()
            chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            driver = uc.Chrome(
                executable_path=os.environ.get("CHROMEDRIVER_PATH"),
                options=chrome_options,
            )
            driver.get(f"https://{self.host}/page/{page}")
            try:
                WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".herald-mod-title"))
                )
            except:
                pass
            driver.save_screenshot("image.png")
            html = driver.page_source
            driver.quit()
        else:
            async with self.session.get(f"https://{self.host}/page/{page}") as resp:
                html = await resp.read()

        soup = bs(html, "html.parser")

        animes = soup.find_all("article")

        results = []
        for i in animes:
            id = i.find("a").get("href").split("/")[3]
            img = i.find("img").get("data-lazy-srcset").strip()

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
        print(soup)
        for i in animes:
            id = i.find("a").get("href").split("/")[3]
            img = i.find("img").get("data-lazy-srcset").strip()

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

    async def isCloudflareUP(self):
        global CLOUDFLARE_CACHE

        if time.time() - CLOUDFLARE_CACHE.get("time", 0) < 60 * 60:
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


async def main():
    ses = aiohttp.ClientSession()
    print((await TPXANIME(ses).latest()))
    await ses.close()


print(asyncio.run(main()))
