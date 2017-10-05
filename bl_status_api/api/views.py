from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import renderers
from rest_framework.decorators import parser_classes
from rest_framework.decorators import renderer_classes
from rest_framework.parsers import FileUploadParser
from rest_framework.parsers import MultiPartParser
from rest_framework.parsers import FormParser
from rest_framework.views import APIView
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from bson import json_util
from django.http import HttpResponse
from bson.objectid import ObjectId # MongoDB native _id parsing support
#
import re # regular expression support
import ast # literal evaluation support (e.g. string to dictionary)
#
from datetime import datetime, timedelta
from passlib.hash import pbkdf2_sha256
from bson import json_util
import jwt
import pprint
import json
#
import logging
import os

# Global variables
mongo_server_connection = 'mongodb://172.16.168.110:27017/' # prod db server
database = 'test_database' # test database
collection = 'status_test' # test collection (table)
user_collection = 'status_test_users' # test user collection (table)
log_collection = 'status_test_log' # test log collection (table)
file_cat_collection = 'status_test_file_cat' # test file catalog collection (table)

# JWT (JSON Web Token) config variables
JWT_SECRET = "#ThisIsASecret!"  # private encryption key
JWT_ALGORITHM = "HS256"         # encryption algorithm
#JWT_EXP_DELTA_SECONDS = 3600    # token expiration time (in seconds)
JWT_EXP_DELTA_SECONDS = 60    # token expiration time (in seconds)

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
    logger.info("Request: root")

    data = 'Welcome to the EMS bl-status REST API. Unauthorized Access is Prohibited. 2017 - Executive Mailing Service'
    return HttpResponse(data)

# Get All Status Records/Documents
@api_view(['GET'])
def all_statuses(request):
    """
    Return All Status Documents
    """
    logger.info("Request: all_statuses")

    data = [] # JSON data array (query results)

    # verify the connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        data = [{"database error": str(e)}]
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
    logger.info("Request: status_count")

    data = [] # JSON data array (query results)

    # verify the connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        data = [{"database error": str(e)}]
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
    logger.info("Request: find_one_by_pattern")

    try:
        pattern = request.GET['pattern']  # pattern to search for
    except Exception:
        pattern = ""

    data = [{}] # JSON data array (query results)

    # verify the connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        data = [{"database error": str(e)}]
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
    logger.info("Request: find_many_by_pattern")

    try:
        pattern = request.GET['pattern']  # pattern to search for
    except Exception:
        pattern = ""

    data = [{}] # JSON data array (query results)

    # verify the connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        data = [{"database error": str(e)}]
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
    logger.info("Request: delete_one_by_pattern")

    try:
        pattern = request.GET['pattern']  # pattern code to search for
    except Exception:
        pattern = ""

    data = {} # result object

    # verify the connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        data = [{"database error": str(e)}]
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
    logger.info("Request: delete_many_by_pattern")

    try:
        pattern = request.GET['pattern']  # pattern to delete by
    except Exception:
        pattern = ""

    data = {} # result object

    # verify the connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        data = [{"database error": str(e)}]
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
    logger.info("Request: insert_one")
    
    try:
        status_data = request.data
    except Exception:
        status_data = ""

    id = {} # new id

    # verify the connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        data = [{"database error": str(e)}]
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
    logger.info("Request: insert_many")

    try:
        status_data = request.data
    except Exception:
        status_data = ""

    ids = "" # new id's

    # verify the connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        data = [{"database error": str(e)}]
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
    logger.info("Request: update_one")

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
        data = [{"database error": str(e)}]
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
@api_view(['POST'])
def authenticate(request):
    """
    Verify User Name in the Database and Verify the Password, & Return Authentication Token
    """
    logger.info("Request: authenticate")

    user = {} # user document (from database)
    data = {} # response object - returned to client
    
    logger.info("authentication processing...")
    try:
        request_username = ""
        request_username = request.data["username"] 
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
        request_password = request.data["password"]
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
            "message": "Database connection error!",
            "token": "",
            "user": {""}
        }
        logger.info("Authentication error: Database connection error: " + str(e))
        return Response(data)

    # find the user name and verify the password
    logger.info("Authentication: request: " + json_util.dumps(request.data))
    if (request.data["username"]):
        db = connection[database]
        user = db[user_collection].find_one({"username": request.data["username"]})

    if(user):
        # verify password against hash
        if (pbkdf2_sha256.verify(request.data["password"], user["password"])):
            payload = {
                "user_id": user["username"],
                "exp": datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
            }
            jwt_token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
        else:
            data = {
                "success": False,
                "message": "Invalid password!",
                "token": "",
                "user": {""}
            }
            logger.info("Authentication error: JWT token generation error: Invalid password")
            connection.close()
            return Response(data)
    else:
        data = {
                "success": False,
                "message": "User does not exist!",
                "token": "",
                "user": {""}
        }
        logger.info("Authentication error: User does not exist")
        connection.close()
        return Response(data)

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
    connection.close()
    return Response(data)

# Check an existing JWT token for expiration
@api_view(['POST'])
def check_token_exp(request):
    """
    Check an existing JWT token for expiration
    """
    logger.info("Request: check_token_exp")
    logger.info("request: " + json_util.dumps(request.data))

    user = request.data
    data = {
        "expired": ""
    }
    try:
        logger.info("decode token: " + user["user"]["token"])
        jwt.decode(user["user"]["token"], JWT_SECRET)
        data["expired"] = False
        return Response(data)
    except jwt.ExpiredSignatureError:
        data["expired"] = True
        return Response(data)

# Receive and store files from connected web clients
# - define a custom renderer to handle PDF (Binary) data
class PDFRenderer(renderers.BaseRenderer):
    media_type = 'application/pdf'
    format = 'pdf'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data

# - define the PDF file upload API endpoint
@api_view(['POST'])
@parser_classes((MultiPartParser, FormParser,)) # process/remove http header/footer data
@renderer_classes((PDFRenderer,)) # render binary PDF data for storage
def file_upload(request):
    """
    Receive and store files from connected web clients 
    """
    logger.info("Request: file_upload")
    logger.info("File Upload MetaData: " + json_util.dumps(request.POST))

    # extract file catalog metadata from the request (to be stored in database)
    cat_data = {
        'pattern': request.data['pattern'],
        'fileType': request.data['fileType'],
        'user': request.data['user'],
        'serverFilePath': request.data['serverFilePath'],
        'clientFilePath': request.data['clientFilePath'],
        'filePostDateTime': request.data['filePostDateTime'],
        'downloadCount': request.data['downloadCount'],
        'replacementCount': request.data['replacementCount'],
    }
    
    # write uploaded file data to the local filesystem
    handle_uploaded_file(request.data['file'], cat_data['clientFilePath']) 

    # verify the db connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        data = [{"database error": str(e)}]
        return Response(data)
    
    # insert the new file catalog document & update Status file information
    db = connection[database]
    if (request.data['file'] != ""):
        # add the local stored path
        cat_data["serverFilePath"] = cat_data['clientFilePath']
        # DB insert
        id = json_util.dumps(db[file_cat_collection].insert_one(cat_data).inserted_id)
        # update file information in Status document for the pattern
        pt = cat_data['pattern']
        fl = cat_data['clientFilePath']
        us = cat_data['user']
        tm = cat_data['filePostDateTime']
        if (cat_data['fileType'] == "Pallet Tags"):
            db[collection].update_many({"pattern": pt },{"$set":{"currentPalletTagFile": fl, "palletTagFileUploadDateTime": tm, "palletTagFileUser": us, "palletTagFileDownloadCount": 0}})
        else:
            db[collection].update_many({"pattern": pt },{"$set":{"currentPalletWorksheetFile": fl, "palletWorksheetFileUploadDateTime": tm,"palletWorksheetFileUser": us, "palletWorksheetFileDownloadCount": 0}})
    else:
        id = {}

    # update status
    data = db[collection].find_one({"pattern": pt })
    # print ("update data: " + json_util.dumps(data))
    if (data != "null"):
        if ((data['currentPalletTagFile'] != "") and (data['currentPalletTagFile'] != " ") and (data['currentPalletWorksheetFile'] != "") and (data['currentPalletWorksheetFile'] != " ")): 
            db[collection].update_many({"pattern": pt },{"$set":{"paperworkStatus": "Complete" }})
        else:
            db[collection].update_many({"pattern": pt },{"$set":{"paperworkStatus": "In Process" }})

    connection.close()

    # convert response to dictionary (for JSON response serialization)
    id_dict = ast.literal_eval(id)
    oid = id_dict['$oid']

    logger.info("File Upload id for: " + cat_data['clientFilePath'] + ": " + json_util.dumps({'inserted_id': oid }))
    return Response({'inserted_id': oid })
    
# - store the rendered data (PDF) in a file on the local file system
def handle_uploaded_file(file, file_name):
    logger.info("File Upload: writting file [ " + file_name + " ]...")
    print("File Upload: writting file [ " + file_name + " ]...")
    destination = open("uploaded_files/" + file_name, 'wb+')
    for chunk in file.chunks():
        destination.write(chunk)
    destination.close()
    logger.info("File Upload: file saved!")
    print("File Upload: file saved!")

# Receive and store logged events from connected web clients 
@api_view(['POST'])
def client_logs(request):
    """
    Receive and store logged events from connected web clients 
    """
    logger.info("Request: client_logs")
    logger.info("request: " + json_util.dumps(request.data))
    
    try:
        log_data = request.data
        ip_address = request.META.get('REMOTE_ADDR', None)
    except Exception:
        log_data = ""

    id = {} # new id

    # verify the connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        data = [{"database error": str(e)}]
        return Response(data)
    
    # insert the new log document
    db = connection[database]
    if (log_data != ""):
        # add the source IP address
        log_data["ipAddress"] = ip_address
        # DB insert
        id = json_util.dumps(db[log_collection].insert_one(log_data).inserted_id)
    else:
        id = {}
    
    connection.close()

    # convert response to dictionary (for JSON response serialization)
    id_dict = ast.literal_eval(id)
    oid = id_dict['$oid']

    return Response({'inserted_id': oid })

# - define the PDF file delete API endpoint
@api_view(['POST'])
def file_delete(request):
    """
    Delete a given pattern's associated PDF file from server repository 
    and update status document 
    """
    logger.info("Request: file_delete")
    logger.info("File Delete MetaData: " + json_util.dumps(request.POST))

    try:
        pattern = request.data['pattern']
        file_name = request.data['fileName']
        file_type = request.data['fileType']
    except Exception:
        pattern = ""
        file_name = ""
        file_type = ""
    
    # verify the connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        data = [{"database error": str(e)}]
        return Response(data)

    # update the status document - PDF file information
    db = connection[database]
    if ((pattern != "") and (file_name != "") and (file_type != "")):
        if (file_type == "Pallet Tags"):
            update_object = db[collection].update_many({"pattern": pattern },{"$set":{"currentPalletTagFile": "", "palletTagReplacementCount": 0, "palletTagFileUploadDateTime": "", "palletTagFileUser": "", "palletTagFileDownloadCount": 0}})
        else:
            update_object = db[collection].update_many({"pattern": pattern },{"$set":{"currentPalletWorksheetFile": "", "palletWorksheetReplacementCount": 0, "palletWorksheetFileUploadDateTime": "", "palletWorksheetFileUser": "", "palletWorksheetFileDownloadCount": 0}})
    else:
        update_object = {}
    
    # update status document - Paperwork status
    data = db[collection].find_one({"pattern": pattern })
    if (data != "null"):
        if ((data['currentPalletTagFile'] != "") and (data['currentPalletTagFile'] != " ") and (data['currentPalletWorksheetFile'] != "") and (data['currentPalletWorksheetFile'] != " ")): 
            db[collection].update_many({"pattern": pattern },{"$set":{"paperworkStatus": "Complete" }})
        else:
            db[collection].update_many({"pattern": pattern },{"$set":{"paperworkStatus": "In Process" }})
    
    # remove metadata info from the file catalog
    db[file_cat_collection].delete_many({"pattern": pattern, "serverFilePath": file_name, "fileType": file_type})

    connection.close()

    # delete the file from server folder
    try:
        if ((pattern != "") and (file_name != "") and (file_type != "")):
            destination = "uploaded_files/" + file_name
            os.remove(destination)
            print("File: " + destination + " Deleted!")
    except Exception as e:
        data = [{"file deletion error": str(e)}]
        return Response(data)

    return Response(update_object.raw_result)