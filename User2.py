from pymongo.collection import Collection
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from mongoengine import Document, StringField, DateTimeField, IntField
import config
from flask import jsonify
from bson.json_util import dumps, loads
from bson import ObjectId
import random

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

def query_all_users():
    # Truy vấn cơ sở dữ liệu để lấy danh sách tất cả người dùng
    users_collection = db['User2']
    users = users_collection.find({}, {'_id': 0})
    return list(users)

def query_user_by_id(id):
    # Truy vấn cơ sở dữ liệu để lấy danh sách người có id là $id
    users_collection = db['User2']
    try:
      user = users_collection.find_one({'_id': id})
    except:
       user = users_collection.find_one({'_id': ObjectId(id)})
    return user

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
    if num_users is None:
      users = users_collection.find({'score': {'$gte': min_score, '$lte': max_score}}).sort('score', -1)
    else:
      users = users_collection.find({'score': {'$gte': min_score, '$lte': max_score}}).sort('score', -1).limit(num_users)
    users = list(users)
    return users

def query_random_users_by_score(min_score=1, max_score=100, num_users=None):
    users_collection = db['User2']

    users = []
    users = users_collection.find({'score': {'$gte': min_score, '$lte': max_score}}).sort('score', -1)
    users = list(users)
    random.shuffle(users)

    if num_users is not None:
        users = users[:num_users]

    return users

def find_users(condition):
  # Tìm người dùng thỏa mãn điều kiện $condition
  users_collection = db['User2']
  users = users_collection.find(condition)
  return list(users)

def find_examiner(min_score, max_score, need_examiner=5):
    #  2 user => min_score     -> mid
    #  3 user => mid -> max_score

    min_score = min(min_score + 1, 100)
    mid = (min_score + max_score) // 2  

    list_examiner = []

    list_a = query_random_users_by_score(min_score, mid, 3)
    list_b = query_random_users_by_score( mid + 1, max_score , 2) 
    need_examiner -= len(list_a) + len(list_b)
    list_examiner += list_a
    list_examiner += list_b

    if(len(list_examiner) == 0):
        return []

    list_add = []
    temp = []
    while need_examiner > 0:
        if len(temp) == 0:
          temp = list_examiner.copy()
        pos = random.randint(0, len(temp))
        pos = max(pos, 0)
        pos = min(pos, len(temp) - 1)
        list_add.append(temp[pos])
        temp.pop(pos)
        need_examiner -= 1
  
    list_examiner += list_add
    list_examiner.sort(key=lambda x: x['score'])
    list_examiner.reverse()
    return list_examiner