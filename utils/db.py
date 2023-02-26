from motor.motor_asyncio import AsyncIOMotorClient as MongoClient

MONGO_DB_URI = "mongodb+srv://techz:bots@cluster0.uzrha.mongodb.net/?retryWrites=true&w=majority"

mongo_client = MongoClient(MONGO_DB_URI)
db = mongo_client.techzapi

