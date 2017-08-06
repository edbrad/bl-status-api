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

import re # Regular Expression support
import ast # Literal Evaluation support (e.g. string to dictionary)

# Global variables
mongo_server_connection = 'mongodb://172.16.168.110:27017/' # prod db server
database = 'test_database' # test database
collection = 'status_test' # test collection (table)

# API Default/Welcome Text Response
@api_view(['GET'])
def root(request):
    """
    Return Generic/Default Welcome Text Response.
    """
    data = 'Welcome to the EMS bl-status REST API. Unauthorized Access is Prohibited. 2017 - Executive Mailing Service'
    return HttpResponse(data)

# Get All Status Records/Documents
@api_view(['GET'])
def all_statuses(request):
    """
    Return All Status Documents
    """
    data = [] # JSON data array (query results)

    # Verify the connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        data = [{"database error":' + e + '}]
        return Response(data)

    # Get all the status records in the database and return to client (w/ JSON Serialization)
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
    data = [] # JSON data array (query results)

    # Verify the connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        data = [{"database error":' + e + '}]
        return Response(data)

    # Get a count of the number of documents in the database and return to client
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
    try:
        pattern = request.GET['pattern']  # pattern to search for
    except Exception:
        pattern = ""

    data = [{}] # JSON data array (query results)

    # Verify the connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        data = '[{"database error":' + e + '}]'
        return Response(data)

    # Find a document database with the matching pattern and return to client (w/ JSON Serialization)
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
    try:
        pattern = request.GET['pattern']  # pattern to search for
    except Exception:
        pattern = ""

    data = [{}] # JSON data array (query results)

    # Verify the connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        data = [{"database error":' + e + '}]
        return Response(data)

    # Find the documents in the database where the pattern starts with "x" and return to client (w/ JSON Serialization)
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

    try:
        pattern = request.GET['pattern']  # pattern code to search for
    except Exception:
        pattern = ""

    data = {} #  result object

    # Verify the connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        data = [{"database error":' + e + '}]
        return Response(data)

    # Delete a single document database with the matching pattern code and return a result object to client
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
    try:
        pattern = request.GET['pattern']  # pattern to delete by
    except Exception:
        pattern = ""

    data = {} #  result object

    # Verify the connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        data = [{"database error":' + e + '}]
        return Response(data)

    # Delete the documents in the database where the pattern code starts with "x" 
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
    try:
        status_data = request.data
    except Exception:
        status_data = ""

    id = {} # new id

    # Verify the connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        data = [{"database error":' + e + '}]
        return Response(data)
    
    # Insert the new document
    db = connection[database]
    if (status_data != ""):
        id = json_util.dumps(db[collection].insert_one(status_data).inserted_id)
    else:
        id = {}
    
    connection.close()

    # Convert response to dictionary (for JSON response serialization)
    id_dict = ast.literal_eval(id)
    oid = id_dict['$oid']

    return Response({'inserted_id': oid })
    
# Insert Many New Status Documents
@api_view(['POST'])
def insert_many(request):
    """
    Insert Many New Status Documents and Return an Array of the New id's
    """
    try:
        status_data = request.data
    except Exception:
        status_data = ""

    ids = "" # new id's

    # Verify the connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        data = [{"database error":' + e + '}]
        return Response(data)
    
    # Insert the new documents
    db = connection[database]
    if (status_data != ""):
        ids = json_util.dumps(db[collection].insert_many(status_data).inserted_ids)
    else:
        ids = ""
    
    connection.close()

    # Convert response (array of inserted id's) to dictionary list (for JSON response serialization)
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
    try:
        update_id = request.data['update_id']
        update_data = request.data['update_data']
    except Exception:
        update_id = ""
        update_data = ""

    # Verify the connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        data = [{"database error":' + e + '}]
        return Response(data)
    
    # Update the document and return the Result Object
    db = connection[database]
    if ((update_id != "") and (update_data != "")):
        update_object = db[collection].update_one({'_id' : ObjectId(str(update_id))}, {'$set': update_data}, upsert=False)
    else:
        update_object = {}
    
    connection.close()

    return Response(update_object.raw_result)
