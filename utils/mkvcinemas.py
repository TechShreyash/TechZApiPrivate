from concurrent.futures.thread import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
import requests
from bs4 import BeautifulSoup as bs
from time import sleep

from string import ascii_letters, digits
import random
import asyncio

import logging

logging.basicConfig(
    filename="logs.txt",
    filemode="a",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)

logger = logging.getLogger("Mkv")


executor = ThreadPoolExecutor(10)


tasks = {}
hash_list = []


def total_links(url):
    r = requests.get(url)
    soup = bs(r.content, "html.parser")

    mealob = (
        soup.find("div", "sp-body").find_all("a", "gdlink")
        if soup.find("div", "sp-body")
        else soup.find_all("a", "gdlink")
    )
    if len(mealob) == 0:
        mealob = soup.find_all("a", "button")

    return len(mealob)


users_queue = []


def is_user_in_queue(api):
    if api in users_queue:
        return True
    return False


def get_queue_pos(hash):
    for i in queue:
        if i.get("hash") == hash:
            return queue.index(i) + 1
    return len(queue)


def add_task(api_key, url, max):
    while True:
        hash = "".join(random.choices(ascii_letters + digits, k=10))
        if hash in hash_list:
            continue
        tasks[hash] = {
            "url": url,
            "status": "pending",
            "max": max,
            "api_key": api_key,
        }
        logger.info(f"Added task to queue : {hash} {url} {tasks[hash]}")
        queue.append(
            {
                "hash": hash,
                "url": url,
                "status": "pending",
                "max": max,
                "api_key": api_key,
            }
        )
        users_queue.append(api_key)
        return {"success": True, "hash": hash, "queue": len(queue)}


def get_task(hash):
    task = tasks.get(hash)
    if task.get("status") == "pending":
        return {
            "success": True,
            "status": "pending",
            "queue": get_queue_pos(hash),
        }
    if task.get("status") == "processing":
        return {
            "success": True,
            "status": "processing",
            "scrapped": task.get("scrapped"),
        }
    if task.get("status") == "failed":
        return {"success": True, "status": "failed", "error": task.get("error")}
    if task.get("status") == "completed":
        return {
            "success": True,
            "status": "completed",
            "results": task.get("results"),
        }
    return {"success": False, "error": "Invalid hash"}


queue = []


async def scrapper_task(loop):
    global queue
    driver = None
    while True:
        if len(queue) > 0:
            if not driver:
                driver = getDriver()

            task = queue.pop(0)
            hash = task.get("hash")

            tasks[hash]["status"] = "processing"
            logger.info(
                f'Scrapping task : {task.get("hash")} {task.get("url")}')

            try:
                results = await loop.run_in_executor(
                    executor,
                    scrap_mkv,
                    (
                        driver,
                        task.get("url"),
                        task.get("max"),
                        hash,
                        task.get("api_key"),
                    ),
                )
                tasks[hash]["status"] = "completed"
                tasks[hash]["results"] = results
                try:
                    users_queue.remove(task.get("api_key"))
                except:
                    pass
            except Exception as e:
                logger.info(f"Error while scrapping : {e}")
                tasks[hash]["status"] = "failed"
                tasks[hash]["error"] = str(e)
                try:
                    users_queue.remove(task.get("api_key"))
                except:
                    pass
        else:
            if driver:
                driver.close()
                driver = None
            await asyncio.sleep(10)


def getDriver() -> webdriver.Chrome:

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_experimental_option(
        "excludeSwitches", ["enable-logging"])
    myDriver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )

    return myDriver


def scrap_mkv(x):
    wd, link, max, hash, api_key = x
    r = requests.get(link)
    soup = bs(r.content, "html.parser")

    mealob = (
        soup.find("div", "sp-body").find_all("a", "gdlink")
        if soup.find("div", "sp-body")
        else soup.find_all("a", "gdlink")
    )
    if len(mealob) == 0:
        mealob = soup.find_all("a", "button")

    generater = '//*[@id="generater"]'
    showlink = '//*[@id="showlink"]'
    landing = '//*[@id="landing"]/div/center/img'

    gdtot = []

    pos = 1
    mealob = mealob[:max]

    for i in mealob:
        try:
            i = i.replace('ww2.mkvcinemas.lat', 'ww3.mkvcinemas.lat')
            print('Scraping', i)
            wd.get(i)
            sleep(3)
            WebDriverWait(wd, 10).until(
                ec.element_to_be_clickable((By.XPATH, b1))
            ).click()
            sleep(10)
            WebDriverWait(wd, 10).until(
                ec.element_to_be_clickable((By.XPATH, generater))
            ).click()
            sleep(5)
            WebDriverWait(wd, 10).until(
                ec.element_to_be_clickable((By.XPATH, showlink))
            ).click()
            IItab = wd.window_handles[1]
            wd.close()
            wd.switch_to.window(IItab)
            title = (
                wd.title.replace("GDToT", "")
                .split("mkvCinemas")[0]
                .rstrip("- ")
                .lstrip(" |")
                .strip()
            )
            size = wd.find_element(By.TAG_NAME, "tr").text.replace(
                "File Size", "").strip()
            info = {"title": title, "gdtot": wd.current_url, "size": size}
            gdtot.append(info)
            tasks[hash]["scrapped"] = f"{pos}/{len(mealob)}"
            pos += 1
        except Exception as e:
            print(e)
            pass

    try:
        users_queue.remove(api_key)
    except:
        pass
    return gdtot
