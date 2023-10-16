from pymongo.collection import Collection
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from mongoengine import Document, StringField, DateTimeField, IntField
import config
from bson.json_util import dumps, loads

uri = f"mongodb+srv://{config.USER}:{config.PASSWORD}@cluster0.becqcta.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri)

# Choose database
db = client['Insight']


class User:
    def __init__(self, username=None, metamask_id=None, score=0):
        self.username = username
        self.metamask_id = metamask_id
        self.score = score

def query_user_by_username(username):
    # Truy vấn cơ sở dữ liệu để lấy danh sách người có username là $username
    users_collection = db['User']
    # find only one user
    user = users_collection.find_one({'username': username})
    return user