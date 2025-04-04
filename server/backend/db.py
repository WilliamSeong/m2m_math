from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

import os

load_dotenv()
client = None

def connect_mongo():
    global client

    db_user = os.getenv("MONGODB_USER")
    db_password = os.getenv("MONGODB_PASSWORD")

    uri = f"mongodb+srv://{db_user}:{db_password}@young-by-nail.vhysf.mongodb.net/?retryWrites=true&w=majority&appName=young-by-nail"

    if client is None:
        client = MongoClient(uri, server_api=ServerApi('1'))

    try:
        client.admin.command('ping')
        print("MongoDB connection successful")
        return True
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        return False


def get_client():
    if client is None:
        connect_mongo()
    return client