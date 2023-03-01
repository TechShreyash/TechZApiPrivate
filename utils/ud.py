import aiohttp


async def get_urbandict(session, word, max=10):
    async with session.get(
        f"http://api.urbandictionary.com/v0/define?term={word}"
    ) as r:
        r = await r.json()

    z = []
    for x in r["list"]:
        a = {}
        a["count"] = x["thumbs_up"] - x["thumbs_down"]
        a["data"] = x
        z.append(a)

    z = z[:max]

    def hhh(e):
        return e["count"]

    z.sort(key=hhh)
    z.reverse()

    results = []

    for i in z:
        ndict = {}
        ndict["definition"] = i["data"]["definition"]
        ndict["example"] = i["data"]["example"]
        results.append(ndict)

    json = {}
    json["success"] = True
    json["results"] = results
    return json
