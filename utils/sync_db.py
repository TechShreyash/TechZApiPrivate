MONGO_DB_URI = (
    "mongodb+srv://techz:bots@cluster0.uzrha.mongodb.net/?retryWrites=true&w=majority"
)
import pymongo

mongo_client = pymongo.MongoClient(MONGO_DB_URI)
db = mongo_client.techzapi
userdb = db.userdb


class DB:
    def get_user(api_key):
        return userdb.find_one({"api_key": api_key})

    def is_user(api_key):
        if userdb.find_one({"api_key": api_key}):
            return True
        else:
            return False

    def reduce_credits(api_key, amount):
        user = DB.get_user(api_key)
        if user["credits"] < amount:
            raise Exception("Not enough credits")
        userdb.update_one(
            {"api_key": api_key}, {"$inc": {"credits": -amount, "used": amount}}
        )
