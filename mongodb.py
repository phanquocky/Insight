from flask import jsonify
from pymongo.collection import Collection
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from mongoengine import Document, StringField, DateTimeField, IntField
from Keypair.hash import sha256_hash
from datetime import datetime, timedelta
import config
import random
from bson.objectid import ObjectId
from bson.json_util import dumps, loads

from Room2 import *

uri = f"mongodb+srv://{config.USER}:{config.PASSWORD}@cluster0.becqcta.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri)

# Choose database
db = client['Insight']


class User:
    def __init__(self, name=None, username=None, password=None, date_of_birth=None, metamask_id=None, public_key=None,
                 score=0, mentor_state=False):
        self.name = name
        self.username = username
        self.password = password
        self.create_date = datetime.now()
        self.date_of_birth = date_of_birth
        self.metamask_id = metamask_id
        self.public_key = public_key
        self.score = score
        self.mentor_state = mentor_state

    def addToDB(self):
        users_collection = db['User']
        self.password = sha256_hash(self.password)
        users_collection.insert_one(self.__dict__)


class Room:
    def __init__(self, mentor=None, test=None, test_sign=None, judges=None, contestant=None, submission=None,
                 submission_sign=None, level=None, final_result=None, status=None):
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


class Mail:
    def __init__(self, addr_from, addr_to, subject, content, date_end, is_read=False) -> None:
        self.addr_from = addr_from
        self.addr_to = addr_to
        self.subject = subject
        self.content = content
        self.date_send = datetime.now()
        self.date_end = date_end
        self.is_read = is_read

    def addToDB(self):
        users_collection = db['Mail']
        users_collection.insert_one(self.__dict__)

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

    room = Room(mentor=mentor['public_key'],
                test="9899799",
                test_sign="8hh7g6gf5f",
                judges=list_judges_data,
                contestant=contestant['public_key'],
                submission="98978ed",
                submission_sign="788u8h8e",
                level=random.randint(1, 100),
                final_result=final_result,
                status=random.randint(0, 6))

    room_collection = db['Room']
    room_collection.insert_one(room.__dict__)

    print('Phong thi created successfully!')


def createUser():
    newUser = User(
        name="John Doe",
        username="haha",
        password="password123",
        date_of_birth="11/08/2003",
        metamask_id="0x123abc",
        public_key="0x456def",
        score=0
    )
    users_collection = db['User']
    users_collection.insert_one(newUser.__dict__)
    print("User created successfully!")


def find_users(condition):
    # Tìm người dùng thỏa mãn điều kiện $condition
    users_collection = db['User']
    users = users_collection.find(condition)
    return list(users)


def update_user_metamask(username, metamaskID):
    # Tìm và cập nhật thông tin người dùng
    users_collection = db['User']
    result = users_collection.update_one({'username': username}, {'$set': {'metamask_id': metamaskID}})

    if result.modified_count > 0:
        return jsonify({'message': 'Metamask của người dùng được cập nhật thành công.'})
    else:
        return jsonify({'message': 'Không tìm thấy người dùng hoặc không có sự thay đổi nào.'}, 404)


def query_user_by_public_key(key):
    # Truy vấn cơ sở dữ liệu để lấy danh sách người có public key là $key
    users_collection = db['User']
    # find only one user
    user = users_collection.find_one({'public_key': key})
    return user


def query_users_by_username(username):
    # Truy vấn cơ sở dữ liệu để lấy danh sách người có tên là $name
    users_collection = db['User']
    # find only one user
    user = users_collection.find_one({'username': username})
    return user


def query_users_by_name(name, count):
    # Truy vấn cơ sở dữ liệu để lấy danh sách người có tên là $name
    users_collection = db['User']
    users = users_collection.find({'name': name}).limit(count)

    return list(users)


def query_all_users():
    # Truy vấn cơ sở dữ liệu để lấy danh sách tất cả người dùng
    users_collection = db['User']
    users = list(users_collection.find({}).sort('score', 1))
    return users


def query_users_by_score(min_score=1, max_score=100, num_users=None):
    users_collection = db['User']
    users = []
    if (num_users == None):
        users = users_collection.find({'score': {'$gte': min_score, '$lte': max_score}},
                                      {"_id": 0, "create_date": 0}).sort('score', 1)
    else:
        users = users_collection.find({'score': {'$gte': min_score, '$lte': max_score}},
                                      {"_id": 0, "create_date": 0}).sort('score', 1).limit(num_users)

    listUser = []

    # In ra màn hình danh sách 
    for user in users:
        listUser.append(user)

    listUser.reverse()
    return listUser, min_score, max_score


def query_examiners_by_score(min_score=0, max_score=100, num_users=20):
    # Truy vấn cơ sở dữ liệu để lấy danh sách người dùng có điểm số trong khoảng $min_score và $max_score
    # Sort by score tăng dần
    users_collection = db['User']
    users = users_collection.find({'score': {'$gte': min_score, '$lte': max_score}}).sort('score', 1).limit(num_users)
    return list(users)


def update_user_judge_state(username, judge_state):
    users_collection = db['User']
    users_collection.update_one({'username': username}, {'$set': {'judge_state': judge_state}})
    print("Update user judge state successfully!")


def update_user_score(_id, score):
    # Cập nhật điểm số của người dùng có id là $id
    users_collection = db['User']
    users_collection.update_one({'_id': _id}, {'$set': {'score': score}})
    print("Update user score successfully!")


def find_examiner(min_score, max_score, need_examiner=5):
    #  2 user => min_score     -> mid
    #  3 user => mid -> max_score

    min_score = min(min_score + 1, 100)
    mid = (min_score + max_score) // 2

    list_examiner = []

    list_a = query_examiners_by_score(min_score, mid, 2)
    list_b = query_examiners_by_score(mid, max_score, 3)
    need_examiner -= len(list_a) + len(list_b)
    list_examiner = list_a + list_b

    if (len(list_examiner) == 0):
        return []

    list_add = []
    temp = []
    while need_examiner > 0:
        if len(temp) == 0:
            temp = list_examiner
        pos = random.randint(0, len(temp))
        list_add.append(temp[pos])
        temp.pop(pos)
        need_examiner -= 1

    list_examiner += list_add
    list_examiner.sort(key=lambda x: x['score'])
    list_examiner.reverse()
    return list_examiner


def find_rooms(condition):
    # Tìm phòng thi thỏa mãn điều kiện $condition
    room_collection = db['Room']
    rooms = room_collection.find(condition)
    return list(rooms)


def create_room(mentor, challenger, examiners):
    room = Room(mentor=mentor,
                judges=examiners,
                contestant=challenger,
                status=0)

    room_collection = db['Room']
    room_collection.insert_one(room.__dict__)
    print('Phong thi created successfully!')
    return room


def delete_room(condition):
    # Xóa phòng thi thỏa mãn điều kiện $condition
    room_collection = db['Room']
    room_collection.delete_one(condition)
    print("Delete room successfully!")


def update_room_status_by_id(room_id, status):
    # Cập nhật trạng thái của phòng thi có id là $room_id
    print("room_id = ", room_id)
    print("room_id = ", room_id['$oid'])
    room_collection = db['Room']
    room_collection.update_one({'_id': ObjectId(room_id['$oid'])}, {'$set': {'status': status}})
    print("Update room status successfully!")


def update_room_mentor_sign(room_id, mentor_sign):
    # Cập nhật chữ kí của mentor cho phòng thi có id là $room_id
    room_collection = db['Room']
    room_collection.update_one({'_id': ObjectId(room_id)}, {'$set': {'test_sign': mentor_sign}})
    print("Update room mentor sign successfully!")


def update_room_contestant_sign(room_id, contestant_sign):
    # Cập nhật chữ kí của mentor cho phòng thi có id là $room_id
    room_collection = db['Room']
    room_collection.update_one({'_id': ObjectId(room_id)}, {'$set': {'submission_sign': contestant_sign}})
    print("Update room mentor sign successfully!")


def update_mail_status(id: str, is_read: bool) -> None:
    mail_collection = db['Mail']
    mail_collection.update_one({'_id': ObjectId(id)}, {'$set': {'is_read': is_read}})
    return None


def query_mail_by_addrto(add_to: str, count: int = None) -> list:
    mail_collection = db['Mail']
    mail = mail_collection.find({'addr_to': add_to}).limit(count)
    return dumps(list(mail))


def createMail(sender='', receiver='', mailsubject='', mailcontent='', end=10) -> str:
    newMail = Mail(
        addr_from=sender,
        addr_to=receiver,
        subject=mailsubject,
        content=mailcontent,
        date_end=0
    )
    mail_collection = db['Mail']
    result = mail_collection.insert_one(newMail.__dict__)
    mail = loads(query_mail_by_id(str(result.inserted_id)))
    date = mail[0]['date_send'] + timedelta(end)
    mail_collection.update_one({'_id': result.inserted_id}, {'$set': {'date_end': date}})
    print("Mail created successfully!")
    return str(result.inserted_id)


def query_mail_by_addrfrom(add_from: str, count: int = None) -> list:
    mail_collection = db['Mail']
    mail = mail_collection.find({'addr_from': add_from}).limit(count)
    return dumps(list(mail))


def query_mail_by_id(id: str) -> list:
    mail_collection = db['Mail']
    mail = mail_collection.find({'_id': ObjectId(id)})
    return dumps(list(mail))


def send_mail_to_user(From, To, subject, content, time):
    date_end = datetime.now() + timedelta(days=time)
    id = createMail(From, To, content, date_end)
    response = query_mail_by_id(id)
    # print("mail :", response)
    return id


def update_mentor(mentor, contestant):
    # Connect to MongoDB
    room_collection = db['Room']

    # Find the room with the specified mentor and contestant
    room = room_collection.find_one({"mentor": mentor, "contestant": contestant})

    if room:
        # Check if the status is already 1, if not, update it to 1
        if room["status"] != 1:
            room_collection.update_one({"_id": room["_id"]}, {"$set": {"status": 1}})
            client.close()
            return True
        else:
            # Room status is already 1, nothing to update
            client.close()
            return True
    else:
        # Room not found
        client.close()
        return False


def save_test_to_db(room_id, file):
    rooms_collection: Collection = db['Room']
    room = rooms_collection.find_one({'_id': ObjectId(room_id)})

    if room:
        # Đọc nội dung của file PDF và chuyển đổi thành bytes
        file_content = file.read()
        file_bytes = bytes(file_content)

        # Cập nhật trường test của đối tượng Room với dữ liệu dưới dạng bytes
        rooms_collection.update_one({'_id': ObjectId(room_id)}, {'$set': {'test': file_bytes}})
        print("Test uploaded successfully!")
    else:
        print("Room not found.")


def upload_test_to_db(room_id, uploaded_file, mentor_id):
    print('room_id')
    print(room_id)
    print('mentor_id')
    print(mentor_id)

    rooms_collection: Collection = db['Room2']
    room = rooms_collection.find_one({'_id': ObjectId(room_id)})
    print(room)

    if room:
        # Đọc nội dung của file PDF và chuyển đổi thành bytes
        file_content = uploaded_file.read()
        file_bytes = bytes(file_content)

        # Tìm và cập nhật phần tử đúng trong mảng tests với mentor_id tương ứng
        for test in room['tests']:
            print(test)
            print('\n')
            if test['mentor_id'] == ObjectId(mentor_id):
                test['test'] = file_bytes
                rooms_collection.update_one({'_id': ObjectId(room_id)}, {'$set': {'tests': room['tests']}})
                print("Test uploaded successfully!")
                return

        print("Mentor not found in tests array.")
    else:
        print("Room not found.")


def get_test_from_db(room_id):
    rooms_collection: Collection = db['Room']
    room = rooms_collection.find_one({'_id': ObjectId(room_id)})

    if room and 'test' in room:
        # Trả về nội dung của file PDF từ trường 'test' trong đối tượng Room
        return room['test']
    else:
        # Trường hợp không tìm thấy đề thi hoặc không có nội dung, trả về None
        return None


def query_mentor_rooms(public_key):
    rooms_collection: Collection = db['Room']
    # status >= 0
    mentor_rooms = rooms_collection.find({'mentor': public_key, 'status': {'$gte': 0}})
    return list(mentor_rooms)


def query_contestant_rooms(public_key):
    rooms_collection: Collection = db['Room']
    contestant_rooms = rooms_collection.find({'contestant': public_key})
    return list(contestant_rooms)


def query_contestant_room2(username):
    rooms_collection: Collection = db['Room2']
    rooms_data = rooms_collection.find({'contestant.username': username})
    return list(rooms_data)

def save_submit_to_db(room_id, file):
    rooms_collection: Collection = db['Room']
    room = rooms_collection.find_one({'_id': ObjectId(room_id)})

    if room:
        # Đọc nội dung của file PDF và chuyển đổi thành bytes
        file_content = file.read()
        file_bytes = bytes(file_content)

        # Cập nhật trường test của đối tượng Room với dữ liệu dưới dạng bytes
        rooms_collection.update_one({'_id': ObjectId(room_id)}, {'$set': {'submission': file_bytes}})
        print("Test uploaded successfully!")
    else:
        print("Room not found.")


def get_submit_from_db(room_id):
    rooms_collection: Collection = db['Room']
    room = rooms_collection.find_one({'_id': ObjectId(room_id)})

    if room and 'test' in room:
        # Trả về nội dung của file PDF từ trường 'test' trong đối tượng Room
        return room['submission']
    else:
        # Trường hợp không tìm thấy đề thi hoặc không có nội dung, trả về None
        return None


def query_mentor_rooms2(username):
    room_collection = db['Room2']
    rooms_data = room_collection.find({'mentors.username': username})

    mentor_rooms = []
    for room_data in rooms_data:
        mentors = [mentor for mentor in room_data['mentors'] if mentor['username'] == username]
        if mentors:
            mentor = mentors[0]
            tests = [test for test in room_data['tests'] if test['mentor_id'] == ObjectId(mentor['id'])]
            if tests:
                room_data['mentors'] = mentor
                room_data['tests'] = tests
                mentor_rooms.append(room_data)

    return mentor_rooms
