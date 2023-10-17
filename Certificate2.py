# from flask import jsonify
from pymongo.collection import Collection
from pymongo.mongo_client import MongoClient
# from pymongo.server_api import ServerApi
# from mongoengine import Document, StringField, DateTimeField, IntField
# from Keypair.hash import sha256_hash
from datetime import datetime, timedelta
import config
# import random
from bson.objectid import ObjectId
from bson.json_util import dumps, loads
from User2 import *

uri = f"mongodb+srv://{config.USER}:{config.PASSWORD}@cluster0.becqcta.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri)

# Choose database
db = client['Insight']

class Certificate2_room:
  def __init__(self, user_id, user_name):
      self.user_id = user_id
      self.username = user_name 
      self.certificates = []

class Certificate:
  def __init__(self, old_score, new_score, data_room, room_hash, signature):
      self.old_score = old_score
      self.new_score = new_score
      self.room_byte = data_room
      self.room_hash = room_hash
      self.signature = signature
      self.date      = datetime.now()
  
def create_certificate(old_score, new_score, room_byte, room_hash, signature):
  return Certificate(old_score, new_score, room_byte, room_hash, signature)

def creat_certificate_2(user_id = None, user_name = None):
  if user_id is None:
    user_id = query_user_by_username(user_name)['_id']
  if user_name is None:
    user_name = query_user_by_id(user_id)['username']

  certificate_room = Certificate2_room(user_id=user_id, user_name=user_name)
  certificate_collection = db['Certificate2']
  certificate_collection.insert_one(certificate_room.__dict__)

def add_certificate_2_by_userid(user_id, certificate):
  certificate_collection = db['Certificate2']
  certificate_room = query_certificate_2_by_userid(user_id)
  if(certificate is None):
    creat_certificate_2(user_id, certificate)
  certificate_collection.update_one({'user_id': ObjectId(user_id)}, {'$push': {'certificates': certificate.__dict__}})

def add_certificate_2_by_username(user_name, certificate):
  certificate_collection = db['Certificate2']
  certificate_room = query_certificate_2_by_username(user_name)
  if certificate_room is None:
    creat_certificate_2(user_name=user_name)
  certificate_collection.update_one({'username': user_name}, {'$push': {'certificates': certificate.__dict__}})
  new_certificate = query_certificate_2_by_username(user_name)
  return new_certificate

def query_certificate_2_by_userid(user_id):
  certificate_collection = db['Certificate2']
  try:
    certificate = certificate_collection.find_one({'user_id': user_id})
  except:
    certificate = certificate_collection.find_one({'user_id': ObjectId(user_id)})
  return certificate

def query_certificate_2_by_username(username):
  certificate_collection = db['Certificate2']
  certificate = certificate_collection.find_one({'username': username})
  return certificate
