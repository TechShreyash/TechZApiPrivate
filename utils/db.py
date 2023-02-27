from motor.motor_asyncio import AsyncIOMotorClient as MongoClient

MONGO_DB_URI = (
    "mongodb+srv://techz:bots@cluster0.uzrha.mongodb.net/?retryWrites=true&w=majority"
)

mongo_client = MongoClient(MONGO_DB_URI)
db = mongo_client.techzapi
userdb = db.userdb


class DB:
    async def get_user(api_key):
        return await userdb.find_one({"api_key": api_key})

    async def is_user(api_key):
        if await userdb.find_one({"api_key": api_key}):
            return True
        else:
            return False

    async def reduce_credits(api_key, amount):
        user = await DB.get_user(api_key)
        if user["credits"] < amount:
            raise Exception("Not enough credits")
        await userdb.update_one(
            {"api_key": api_key}, {"$inc": {"credits": -amount, "used": amount}}
        )
