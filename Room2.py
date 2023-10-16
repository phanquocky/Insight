# from flask import jsonify
# from pymongo.collection import Collection
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
  def __init__(self, mentors=None, tests=None, contestant=None, final_result=None, updated_score=None):
      self.mentors = mentors
      self.tests = tests
      self.contestant = contestant
      self.final_result = final_result
      self.updated_score = updated_score  

def create_room_2(contestant, mentors):
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
  
  room = Room2(mentors=new_mentors, tests=tests, contestant=new_contestant, final_result=None, updated_score=None)

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


def encode_to_byte_room_2(room_id):
  room_collection = db['Room2']
  result = room_collection.find_one({"_id": ObjectId(room_id)})
  return dumps(result)  

def decode_to_dict_room_2(room_byte):
  return loads(room_byte)