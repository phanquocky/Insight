from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from mongoengine import Document, StringField, DateTimeField, IntField
from datetime import datetime
import config
import random

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

class Room:
    def __init__(self, mentor, test, test_sign, judges, contestant, submission, submission_sign, level, final_result, status):
        self.mentor = mentor
        self.test = test
        self.test_sign = test_sign
        self.judges = judges  # Danh sách các giám khảo và điểm và chữ kí của họ
        self.contestant = contestant
        self.submission = submission
        self.submission_sign = submission_sign
        self.level = level
        self.final_result = final_result
        self.status = status

# Test room
def createRoomRandom():
    users_collection = db["User"]
    users = list(users_collection.find())

    mentor = contestant = None
    judges = []

    # Chọn mentor, người thi và giám khảo không trùng nhau
    while True:
        mentor = random.choice(users)
        contestant = random.choice(users)
        judges = random.sample(users, 5)  # Lấy ngẫu nhiên 5 giám khảo

        # Kiểm tra các users không trùng nhau
        if mentor != contestant and mentor not in judges and contestant not in judges:
            break
    
    final_result = 0
    list_judges_data = []
    for judge in judges:
        score = random.randint(0, 100)
        final_result += score
        judge_data = {
            "public_key": judge['public_key'],
            "score": score,
            "judge_sign": "hahahihiiii111000"
        }
        list_judges_data.append(judge_data)
    final_result //= len(list_judges_data)

    room = Room(mentor = mentor['public_key'], 
                test = "9899799", 
                test_sign = "8hh7g6gf5f", 
                judges = list_judges_data, 
                contestant = contestant['public_key'], 
                submission = "98978ed", 
                submission_sign = "788u8h8e", 
                level = random.randint(1, 100), 
                final_result = final_result, 
                status = random.randint(0, 6))
    

    room_collection = db['Room']
    room_collection.insert_one(room.__dict__)

    print('Phong thi created successfully!')

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
            "DoB": user['date_of_birth'],
            "public_key": user['public_key'],
            "score": user['score']
        }
        listUser.append(userProfile)
    
    print(listUser)
    return listUser

def query_all_users():
    # Truy vấn cơ sở dữ liệu để lấy danh sách tất cả người dùng
    users_collection = db['User']
    users = users_collection.find({}).sort('score', 1)

    listUser = []

    # In ra màn hình danh sách 
    for user in users:
        userProfile = {
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
    # Sort by score
    users_collection = db['User']
    users = users_collection.find({'score': {'$gte': min_score, '$lte': max_score}}).sort('score', 1).limit(num_users)

    listUser = []

    # In ra màn hình danh sách 
    for user in users:
        userProfile = {
            "name": user['name'],
            "public_key": user['public_key'],
            "score": user['score']
        }
        listUser.append(userProfile)
    
    listUser.reverse()
    print("users with score in range: ", min_score, " - ", max_score)  
    print("number of users: ", len(listUser))
    print(listUser)
    return listUser 

def update_user_score(id, score):
    # Cập nhật điểm số của người dùng có id là $id
    users_collection = db['User']
    users_collection.update_one({'_id': id}, {'$set': {'score': score}})
    print("Update user score successfully!")

def find_examiner_above(min_score, need_examiner = 5):
    #  2 user => min_score     -> min_score + 4
    #  2 user => min_score + 5 -> min_score + 9
    #  1 user => min_score + 10 -> 100

    min_score = min(min_score + 1, 100)
    list_examiner = []

    list_a = query_users_by_score(min_score, min_score + 4, 2)
    list_b = query_users_by_score(min_score + 5, min_score + 9, 2)
    need_examiner -= len(list_a) + len(list_b)
    list_examiner = list_a + list_b

    min_score += 10
    while min_score <= 100 and need_examiner > 0:
        list_c = query_users_by_score(min_score, min_score+9, need_examiner)
        list_c.reverse()
        print("\t list_c : ", list_c)
        list_examiner += list_c
        need_examiner -= len(list_c)
        min_score += 10

    print("list examiner: ")
    print(list_examiner)
    return list_examiner

def find_room_with_mentor_and_challenger(mentor_pubkey, challenger_pubkey) :
    # Solve Query
    print("Find room with mentor and challenger successfully!")
    return None

def update_room_with_examiners(room_id, examiners):
    # Update data to mongodb
    print("Update room with examiners successfully!")
    return None