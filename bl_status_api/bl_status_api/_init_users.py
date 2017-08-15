from datetime import datetime, timedelta
from passlib.hash import pbkdf2_sha256
from pymongo import MongoClient
from bson import json_util
import jwt
import pprint
import json

"""
Initialize bl-status user database
"""

# Global variables
mongo_server_connection = 'mongodb://172.16.168.110:27017/' # prod db server
database = 'test_database' # test database
collection = 'status_test_users' # test User collection (table)

# JWT (JSON Web Token) config variables
JWT_SECRET = "#ThisIsASecret!"  # private encryption key
JWT_ALGORITHM = "HS256"         # encryption algorithm
JWT_EXP_DELTA_SECONDS = 20      # token expiration time (in seconds)

# Raw list of User dictionaries
users = [
    {
        "username" : "admin",
        "password" : "set@pass1",
        "roles" : ["Administrator"]
    },
    {
        "username" : "sampleroom",
        "password" : "set@pass1",
        "roles" : ["SampleRoom"]
    },
    {
        "username" : "accounting",
        "password" : "set@pass1",
        "roles" : ["Accounting"]
    },
    {
        "username" : "dropshipping",
        "password" : "set@pass1",
        "roles" : ["Dropshipping"]
    }
]

# Encrypt users' passwords
print("Encrypt Users' Passwords:\n")
for user in users:
    print("[BEFORE]: " + "user: " + user["username"] + " password: " + user["password"])
    user["password"] = pbkdf2_sha256.encrypt(user["password"], rounds=200000, salt_size=16)
    print(" [AFTER]: " + "user: " + user["username"] + " password: " + user["password"] + "\n")

# Delete ALL existing users
print("Delete Existing Users:\n")
result = ""

# verify the connection
try:
    connection = MongoClient(mongo_server_connection)
except Exception as e:
    print("database error: " + e)

db = connection[database] 
result = db.drop_collection(collection)
print("Delete Result: " + json.dumps(result))
connection.close()

print("\n")

# Store Users in database
print("Store Users in Database:\n")
for user in users: 
    id = {} # new id

    # verify the connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        print("database error: " + e)
        continue

    # insert the new document
    db = connection[database]
    id = json_util.dumps(db[collection].insert_one(user).inserted_id)

    print("User: " + user["username"] + " database id: " + id)
    connection.close()

print("\n")

# Get Users from database, verify passwords, and generate a JWT (JSON Web Token)
print("Verify Users and Generate JWT Tokens:\n")
for user in users:
    data = {} # user data returned from database

    # Verify the connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        print("database error: " + e)
        continue

    # Find a user database with the matching username, verify password, & generate token
    db = connection[database]
    data = json_util.dumps(db[collection].find_one({"username": user["username"]}))
    if (pbkdf2_sha256.verify("set@pass1", user["password"])):
        print(user["username"] + " password ok!")
        payload = {
            "user_id": user["username"],
            "exp": datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
        }
        jwt_token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
        print("--JWT Token--: " + jwt_token.decode("utf-8") + "\n")
    else:
        print(user["username"] + " PASSWORD ERROR!!!\n")

    connection.close()
    