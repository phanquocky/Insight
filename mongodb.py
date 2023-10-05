from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from mongoengine import Document, StringField, DateTimeField, IntField
from datetime import datetime
import config

uri = f"mongodb+srv://{config.USER}:{config.PASSWORD}@cluster0.becqcta.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri)

# Choose database
db = client['Insight']

class User:
    def __init__(self, name, password, date_of_birth, metamask_id, public_key, score = 0):
        self.name = name
        self.password = password
        self.create_date = datetime.now()
        self.date_of_birth = date_of_birth
        self.metamask_id = metamask_id
        self.public_key = public_key
        self.score = score

def createUser():
    newUser = User(
        name = "John Doe",
        password = "password123",
        date_of_birth = "11/08/2003",
        metamask_id = "0x123abc",
        public_key = "0x456def",
        score = 0
    )
    users_collection = db['User']
    users_collection.insert_one(newUser.__dict__) 
    print("User created successfully!")

def query_users_by_name(name):
    # Truy vấn cơ sở dữ liệu để lấy danh sách người có tên là $name
    users_collection = db['User']
    users = users_collection.find({'name': name})

    listUser = []

    # In ra màn hình danh sách 
    for user in users:
        userProfile = {
            "id": user['_id'],
            "name": user['name'],
            "DoB": user['date_of_birth']
        }
        listUser.append(userProfile)
    
    print(listUser)
    return listUser

def query_all_users():
    # Truy vấn cơ sở dữ liệu để lấy danh sách tất cả người dùng
    users_collection = db['User']
    users = users_collection.find({})

    listUser = []

    # In ra màn hình danh sách 
    for user in users:
        userProfile = {
            "id": user['_id'],
            "name": user['name'],
            "public_key": user['public_key'],
            "score": user['score']
        }
        listUser.append(userProfile)
    
    print("all users: ")
    print("number of users: ", len(listUser))
    print(listUser)
    return listUser

def query_users_by_score(min_score = 0, max_score = 100, num_users = 20): 
    # Truy vấn cơ sở dữ liệu để lấy danh sách người dùng có điểm số trong khoảng $min_score và $max_score
    users_collection = db['User']
    users = users_collection.find({'score': {'$gt': min_score, '$lt': max_score}}).limit(num_users)

    listUser = []

    # In ra màn hình danh sách 
    for user in users:
        userProfile = {
            "id": user['_id'],
            "name": user['name'],
            "public_key": user['public_key'],
            "score": user['score']
        }
        listUser.append(userProfile)
    
    print("users with score in range: ", min_score, " - ", max_score)  
    print("number of users: ", len(listUser))
    print(listUser)
    return listUser

def update_user_score(id, score):
    # Cập nhật điểm số của người dùng có id là $id
    users_collection = db['User']
    users_collection.update_one({'_id': id}, {'$set': {'score': score}})
    print("Update user score successfully!")