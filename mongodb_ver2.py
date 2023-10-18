from pymongo.collection import Collection
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from mongoengine import Document, StringField, DateTimeField, IntField
import config
from flask import jsonify
from bson.json_util import dumps, loads

from Room2 import *
# class Room2:
#   def __init__(self, mentors=None, tests=None, contestant=None, final_result=None, updated_score=None):
#       self.mentors = mentors
#       self.tests = tests
#       self.contestant = contestant
#       self.final_result = final_result
#       self.updated_score = updated_score  


from User2 import *
# class User:
#     def __init__(self, username = None, metamask_id = None, score = 0, former = False):
#         self.username = username
#         self.metamask_id = metamask_id
#         self.score = score
#         self.former = former
#     def addToDB(self):
#         users_collection = db['User2']
#         users_collection.insert_one(self.__dict__)

from Certificate2 import *
# class Certificate:
#   def __init__(self, old_score, new_score, data_room, room_hash, signature):
#       self.old_score = old_score
#       self.new_score = new_score
#       self.room_byte = data_room
#       self.room_hash = room_hash
#       self.signature = signature
#       self.date      = datetime.now()