from motor.motor_asyncio import AsyncIOMotorClient as MongoClient

MONGO_DB_URI = (
    "mongodb+srv://techz:bots@cluster0.uzrha.mongodb.net/?retryWrites=true&w=majority"
)

mongo_client = MongoClient(MONGO_DB_URI)
db = mongo_client.techzapi
userdb = db.userdb


async def animedex_stats():
    li = []

    async for user in userdb.find():
        if not user.get("animedex"):
            continue
        view = sum(user.get("animedex", {}).values())
        li.append([user["user_id"], view])
        print(len(user.get("animedex", {}).values()))

    li.sort(key=lambda x: x[1], reverse=True)
    print(li)


import asyncio

asyncio.run(animedex_stats())
