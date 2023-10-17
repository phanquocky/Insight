# from flask import jsonify
from pymongo.collection import Collection
from pymongo.mongo_client import MongoClient
# from pymongo.server_api import ServerApi
# from mongoengine import Document, StringField, DateTimeField, IntField
# from Keypair.hash import sha256_hash
# from datetime import datetime, timedelta
import config
# import random
from bson.objectid import ObjectId
from bson.json_util import dumps, loads

uri = f"mongodb+srv://{config.USER}:{config.PASSWORD}@cluster0.becqcta.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri)

# Choose database
db = client['Insight']

class Room2:
  def __init__(self, mentors=None, tests=None, contestant=None, final_result=None, updated_score=None, prev_score = None, want_score = None):
      self.mentors = mentors
      self.tests = tests
      self.contestant = contestant
      self.is_finished = False
      self.final_result = final_result
      self.updated_score = updated_score  
      self.prev_score = prev_score
      self.want_score = want_score

def create_room_2(contestant, mentors, prev_score, want_score):
  new_contestant = {
     "id": contestant['_id'],
     "username": contestant['username']
  }

  new_mentors = []
  for mentor in mentors:
    new_mentors.append({
      "id": mentor['_id'],
      "username": mentor['username']
    })
  
  tests = []
  for mentor in mentors:
    test = {
      "mentor_id": mentor['_id'],
      "test": None,
      "test_sign": None,
      "submission": None,
      "submission_sign": None,
      "score": None,
      "score_sign": None
    }
    tests.append(test)
  
  room = Room2(mentors=new_mentors, tests=tests, prev_score=prev_score, want_score=want_score, contestant=new_contestant, final_result=None, updated_score=None)

  room_collection = db['Room2']
  result = room_collection.insert_one(room.__dict__)
  # print("result = ", result.inserted_id)

  room = find_room_2_by_id(result.inserted_id)
  # print("room = ", room)

  print('Phong thi created successfully!')
  return dumps(room)
  
def find_room_2_by_id(room_id):
  room_collection = db['Room2']
  result = room_collection.find_one({"_id": ObjectId(room_id)})
  return result

def update_room_2_mentor_sign(room_id, mentor_id, test_sign):
  room = find_room_2_by_id(room_id)
  tests = room['tests']
  for test in tests:
    if test['mentor_id'] == ObjectId(mentor_id):
      test['test_sign'] = test_sign
      break
  # print("tests = ", tests)
  # print("test_sign = ", test_sign)
  room_collection = db['Room2']
  result = room_collection.update_one({"_id": ObjectId(room_id)}, {"$set": {"tests": tests}})
  # print("update room 2 mentor sign successfully")  

def update_room_2_contestant_sign(room_id, mentor_id, signature):
  room = find_room_2_by_id(room_id)
  tests = room['tests']
  for test in tests:
    if test['mentor_id'] == ObjectId(mentor_id):
      test['submission_sign'] = signature
      break
  room_collection = db['Room2']
  result = room_collection.update_one({"_id": ObjectId(room_id)}, {"$set": {"tests": tests}})

def get_test_from_room_2(room_id, mentor_id):
  room = find_room_2_by_id(room_id)
  tests = room['tests']
  for test in tests:
    if test['mentor_id'] == ObjectId(mentor_id):
      return test['test']
  return None

def get_submit_from_room_2(room_id, mentor_id):
  room = find_room_2_by_id(room_id)
  tests = room['tests']
  for test in tests:
      return test['submission']
  return None

def encode_to_byte_room_2(room_id):
  room_collection = db['Room2']
  result = room_collection.find_one({"_id": ObjectId(room_id)}, {"_id": 0})
  return dumps(result)  

def decode_to_dict_room_2(room_byte):
  return loads(room_byte)

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

def upload_test_to_db(room_id, uploaded_file, mentor_id):
    # print('room_id')
    # print(room_id)
    # print('mentor_id')
    # print(mentor_id)

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