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

logger = logging.getLogger(__name__)

from concurrent.futures.thread import ThreadPoolExecutor

executor = ThreadPoolExecutor(10)


tasks = []
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


def add_task(url, max):
    global queue
    while True:
        hash = "".join(random.choices(ascii_letters + digits, k=10))
        if hash in hash_list:
            continue
        tasks.append(
            {
                "hash": hash,
                "url": url,
                "status": "pending",
                "max": max,
            }
        )
        logger.info("Added task to queue :", hash, url)
        return {
            "success": True,
            "hash": hash,
            "status": "pending",
            "queue": len(queue),
        }


def get_task(hash):
    pos = 1
    for i in queue:
        if i.get("hash") == hash:
            break
        pos += 1
    for task in tasks:
        if task.get("hash") == hash:
            if task.get("status") == "pending":
                return {"success": True, "status": "pending", "queue": pos}
            if task.get("status") == "processing":
                return {"success": True, "status": "processing"}
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
    while True:
        for i in tasks:
            if i.get("status") == "pending":
                queue.append(i)

        if len(queue) > 0:
            for i in queue:
                task = i
                pos = 0
                for i in tasks:
                    if i == task:
                        index = pos
                        break
                    pos += 1

                tasks[index]["status"] = "processing"

                logger.info("Scrapping task :", task.get("hash"), task.get("url"))

                driver = getDriver()
                try:
                    results = await loop.run_in_executor(
                        executor, scrap_mkv, (driver, task.get("url"))
                    )
                    tasks[index]["status"] = "completed"
                    tasks[index]["results"] = results
                except Exception as e:
                    logger.error("Error while scrapping :", e)
                    tasks[index]["status"] = "failed"
                    tasks[index]["error"] = str(e)

        await asyncio.sleep(30)


web_driver = None


def getDriver() -> webdriver.Chrome:
    global web_driver
    if web_driver:
        return web_driver

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

    prefs = {"profile.managed_default_content_settings.images": 2}

    chrome_options.add_experimental_option("prefs", prefs)
    myDriver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )

    return myDriver


def scrap_mkv(x):
    wd, link = x
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

    gdtot = {}

    pos = 1

    for i in mealob[:1]:
        wd.get(i["href"])
        sleep(3)
        WebDriverWait(wd, 10).until(
            ec.element_to_be_clickable((By.XPATH, landing))
        ).click()
        WebDriverWait(wd, 10).until(
            ec.element_to_be_clickable((By.XPATH, generater))
        ).click()
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
        gdtot[title] = wd.current_url
        pos += 1

    return gdtot
