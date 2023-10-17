from pymongo.collection import Collection
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from mongoengine import Document, StringField, DateTimeField, IntField
import config
from flask import jsonify
from bson.json_util import dumps, loads

uri = f"mongodb+srv://{config.USER}:{config.PASSWORD}@cluster0.becqcta.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri)

# Choose database
db = client['Insight']



class User:
    def __init__(self, username = None, metamask_id = None, score = 0, former = False):
        self.username = username
        self.metamask_id = metamask_id
        self.score = score
        self.former = former
    def addToDB(self):
        users_collection = db['User2']
        users_collection.insert_one(self.__dict__)

def query_user_by_username(username):
    # Truy vấn cơ sở dữ liệu để lấy danh sách người có username là $username
    users_collection = db['User2']
    # find only one user
    user = users_collection.find_one({'username': username})
    return user

def update_user_score(username, score):
    # Tìm và cập nhật thông tin người dùng
    users_collection = db['User2']
    result = users_collection.update_one({'username': username}, {'$set': {'score': score}})
    
    if result.modified_count > 0:
        return jsonify({'message': 'Metamask của người dùng được cập nhật thành công.'})
    else:
        return jsonify({'message': 'Không tìm thấy người dùng hoặc không có sự thay đổi nào.'}, 404)
    
def query_users_by_score(min_score=1, max_score=100, num_users=None):
    users_collection = db['User2']
    users = []
    if (num_users == None):
        users = users_collection.find({'score': {'$gte': min_score, '$lte': max_score}}).sort('score', 1)
    else:
        users = users_collection.find({'score': {'$gte': min_score, '$lte': max_score}}).sort('score', 1).limit(num_users)

    listUser = []
    for user in users:
        listUser.append(user)

    listUser.reverse()
    # sort giảm dần
    return listUser, min_score, max_score
