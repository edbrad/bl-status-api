from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import parser_classes
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from bson import json_util
from django.http import HttpResponse
from bson.objectid import ObjectId # For find-by-mongoID
#
import re # Regular Expression support
import ast # Literal Evaluation support (e.g. string to dictionary)
#
from datetime import datetime, timedelta
from passlib.hash import pbkdf2_sha256
from bson import json_util
import jwt
import pprint
import json
#
import logging

# Global variables
mongo_server_connection = 'mongodb://172.16.168.110:27017/' # prod db server
database = 'test_database' # test database
collection = 'status_test' # test collection (table)
user_collection = 'status_test_users' # test user collection (table)

# JWT (JSON Web Token) config variables
JWT_SECRET = "#ThisIsASecret!"  # private encryption key
JWT_ALGORITHM = "HS256"         # encryption algorithm
JWT_EXP_DELTA_SECONDS = 3600    # token expiration time (in seconds)

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('bl-status-api.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# API Default/Welcome Text Response
@api_view(['GET'])
def root(request):
    """
    Return Generic/Default Welcome Text Response.
    """
    logger.info("root Request")

    data = 'Welcome to the EMS bl-status REST API. Unauthorized Access is Prohibited. 2017 - Executive Mailing Service'
    return HttpResponse(data)

# Get All Status Records/Documents
@api_view(['GET'])
def all_statuses(request):
    """
    Return All Status Documents
    """
    logger.info("all_statuses Request")

    data = [] # JSON data array (query results)

    # verify the connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        data = [{"database error":' + e + '}]
        return Response(data)

    # get all the status records in the database and return to client (w/ JSON Serialization)
    db = connection[database]
    data = json_util.dumps(db[collection].find({}))
    connection.close()
    return HttpResponse(data, content_type='application/json')

# Get Status Document (Record) Count
@api_view(['GET'])
def status_count(request):
    """
    Return Current Status Document (Record) Count
    """
    logger.info("status_count Request")

    data = [] # JSON data array (query results)

    # verify the connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        data = [{"database error":' + e + '}]
        return Response(data)

    # get a count of the number of documents in the database and return to client
    db = connection[database]
    data = db[collection].count()
    connection.close()
    return HttpResponse(data, content_type='application/json')

# Find/Get A Single Document By Pattern Code
@api_view(['GET'])
def find_one_by_pattern(request):
    """
    Find and Return a Single Status Document by Pattern Code (9999-99X)
    """
    logger.info("find_one_by_pattern Request")

    try:
        pattern = request.GET['pattern']  # pattern to search for
    except Exception:
        pattern = ""

    data = [{}] # JSON data array (query results)

    # verify the connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        data = '[{"database error":' + e + '}]'
        return Response(data)

    # find a document database with the matching pattern and return to client (w/ JSON Serialization)
    db = connection[database]
    if (pattern != ""):
        data = json_util.dumps(db[collection].find_one({"pattern": pattern}))
        if data == "null":
            data = [{}]
    else:
        data = [{}]

    connection.close()
    
    return HttpResponse(data, content_type='application/json')

# Find/Get Multiple Documents By Partial Pattern Code
@api_view(['GET'])
def find_many_by_pattern(request):
    """
    Find and Return Multiple Status Documents by Partial Pattern Code (999*)
    """
    logger.info("find_many_by_pattern Request")

    try:
        pattern = request.GET['pattern']  # pattern to search for
    except Exception:
        pattern = ""

    data = [{}] # JSON data array (query results)

    # verify the connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        data = [{"database error":' + e + '}]
        return Response(data)

    # find the documents in the database where the pattern starts with "x" and return to client (w/ JSON Serialization)
    db = connection[database]
    if (pattern != ""):
        search_pattern = "^" + pattern
        data = json_util.dumps(db[collection].find({ "pattern": re.compile(search_pattern, re.IGNORECASE)}))
        if data == "null":
            data = [{}]
    else:
        data = [{}]

    connection.close()

    return HttpResponse(data, content_type='application/json')

# Delete A Single Document By Pattern Code
@api_view(['DELETE'])
def delete_one_by_pattern(request):
    """
    Delete a Single Status Document by Pattern Code (9999-99X) and Return a Result Object
    """
    logger.info("delete_one_by_pattern Request")

    try:
        pattern = request.GET['pattern']  # pattern code to search for
    except Exception:
        pattern = ""

    data = {} #  result object

    # verify the connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        data = [{"database error":' + e + '}]
        return Response(data)

    # delete a single document database with the matching pattern code and return a result object to client
    db = connection[database]
    if (pattern != ""):
        delete_result  = db[collection].delete_one({"pattern": pattern})
        data = delete_result.raw_result
    else:
        data = {}

    connection.close()

    return Response(data)

# Delete All Matching Documents By A Partial Pattern Code
@api_view(['DELETE'])
def delete_many_by_pattern(request):
    """
    Delete All Documents by a Partial Pattern Code (999*) and Return a Result Object
    """
    logger.info("delete_many_by_pattern Request")

    try:
        pattern = request.GET['pattern']  # pattern to delete by
    except Exception:
        pattern = ""

    data = {} #  result object

    # verify the connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        data = [{"database error":' + e + '}]
        return Response(data)

    # delete the documents in the database where the pattern code starts with "x" 
    db = connection[database]
    if (pattern != ""):
        search_pattern = "^" + pattern
        delete_result = db[collection].delete_many({ "pattern": re.compile(search_pattern, re.IGNORECASE)})
        data = delete_result.raw_result
    else:
        data = {}

    connection.close()

    return Response(data)

# Insert A Single New Status Document
@api_view(['POST'])
def insert_one(request):
    """
    Insert a Single New Status Document and Return the New id
    """
    logger.info("insert_one Request")
    
    try:
        status_data = request.data
    except Exception:
        status_data = ""

    id = {} # new id

    # verify the connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        data = [{"database error":' + e + '}]
        return Response(data)
    
    # insert the new document
    db = connection[database]
    if (status_data != ""):
        id = json_util.dumps(db[collection].insert_one(status_data).inserted_id)
    else:
        id = {}
    
    connection.close()

    # convert response to dictionary (for JSON response serialization)
    id_dict = ast.literal_eval(id)
    oid = id_dict['$oid']

    return Response({'inserted_id': oid })
    
# Insert Many New Status Documents
@api_view(['POST'])
def insert_many(request):
    """
    Insert Many New Status Documents and Return an Array of the New id's
    """
    logger.info("insert_many Request")

    try:
        status_data = request.data
    except Exception:
        status_data = ""

    ids = "" # new id's

    # verify the connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        data = [{"database error":' + e + '}]
        return Response(data)
    
    # insert the new documents
    db = connection[database]
    if (status_data != ""):
        ids = json_util.dumps(db[collection].insert_many(status_data).inserted_ids)
    else:
        ids = ""
    
    connection.close()

    # convert response (array of inserted id's) to dictionary list (for JSON response serialization)
    ids_dict = ast.literal_eval(ids)
    oids = []
    for id in ids_dict:
        oids.append(id['$oid'])

    return Response({'inserted_ids': oids })

# Update A Single Status Document
@api_view(['PUT'])
def update_one(request):
    """
    Update a Single Status Document and Return a Result Object
    """
    logger.info("update_one Request")

    try:
        update_id = request.data['update_id']
        update_data = request.data['update_data']
    except Exception:
        update_id = ""
        update_data = ""

    # verify the connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        data = [{"database error":' + e + '}]
        return Response(data)
    
    # update the document and return the Result Object
    db = connection[database]
    if ((update_id != "") and (update_data != "")):
        update_object = db[collection].update_one({'_id' : ObjectId(str(update_id))}, {'$set': update_data}, upsert=False)
    else:
        update_object = {}
    
    connection.close()

    return Response(update_object.raw_result)

# Verify User Name in the Database and Verify the Password, & Return Authentication Token
@api_view(['GET'])
def authenticate(request):
    """
    Verify User Name in the Database and Verify the 
    Password, & Return Authentication Token
    """
    logger.info("authenticate Request")

    user = {} # user document (from database)
    data = {} # response object - returned to client
    
    logger.info("Authentication processing...")
    try:
        request_username = ""
        request_username = request.GET["username"] 
    except Exception as e:
        data = {
            "success": False,
            "message": "Authentication error: Missing username",
            "token": "",
            "user": {""}
        }
        logger.info("Authentication error: Missing username " + str(e))
        return Response(data)

    try:
        request_password = ""
        request_password = request.GET["password"]
    except Exception as e:
        data = {
            "success": False,
            "message": "Authentication error: Missing password",
            "token": "",
            "user": {""}
        }
        logger.info("Authentication error: Missing password " + str(e))
        return Response(data)

    # verify the connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        data = {
            "success": False,
            "message": "Database connection error",
            "token": "",
            "user": {""}
        }
        logger.info("Authentication error: Database connection error: " + str(e))
        return Response(data)

    # find the user name and verify the password
    print("Authentication: request: " + json_util.dumps(request.GET))
    logger.info("Authentication: request: " + json_util.dumps(request.GET))
    if (request.GET["username"]):
        db = connection[database]
        user = db[user_collection].find_one({"username": request.GET["username"]})

    if(user):
        print("user:  " + json_util.dumps(user))
        # verify password againt hash
        if (pbkdf2_sha256.verify(request.GET["password"], user["password"])):
            payload = {
                "user_id": user["username"],
                "exp": datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
            }
            jwt_token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
        else:
            data = {
                "success": False,
                "message": "JWT token generation error: Invalid password",
                "token": "",
                "user": {""}
            }
            logger.info("Authentication error: JWT token generation error: Invalid password")
            return Response(data)
    else:
        data = {
                "success": False,
                "message": "User does not exist",
                "token": "",
                "user": {""}
        }
        logger.info("Authentication error: User does not exist")
        return Response(data)

    connection.close()

    data = {
        "success": True,
        "message": "Authentication successful",
        "token": jwt_token,
        "user": {
            "username": user['username'],
            "roles": user['roles']
        }
    }
    logger.info("Authentication successful for: " + user['username'])
    return Response(data)
