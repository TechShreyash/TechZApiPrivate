import aiohttp
import random


async def download(session, url, f=False):
    img = "temp_files/" + str(random.randint(11111111, 99999999)) + ".jpg"
    if not url.endswith((".png", ".jpg", ".jpeg")) and not f:
        async with session.head(url) as resp:
            x = resp.headers
            print(x)
            image_formats = ("image/png", "image/jpeg", "image/jpg")
            if resp.status != 200 or not resp.headers.get("content-type"):
                raise Exception("Invalid url")
            if resp.headers["content-type"] not in image_formats:
                raise Exception("Invalid image url")
    async with session.get(url) as resp:
        with open(img, "wb") as f:
            f.write(await resp.read())
    return img
