from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from bson import json_util
from django.http import HttpResponse
import re

# Global variables
mongo_server_connection = 'mongodb://172.16.168.110:27017/' # prod db server
database = 'test_database' # test database
collection = 'status_test' # test collection (table)

# API Default/Welcome Response
@api_view(['GET'])
def root(request):
    """
    Return Generic/Default Text Response.
    """
    data = 'Welcome to the EMS bl-status REST API'
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
        connection = MongoClient(mongo_server_connection, serverSelectionTimeoutMS=30)
    except Exception as e:
        data = '[{"database error":' + e + '}]'
        return JsonResponse(data, content_type='application/json')

    # Get all the status records in the database and return to client
    db = connection[database]
    data = json_util.dumps(db[collection].find({}))
    connection.close()
    return HttpResponse(data, content_type='application/json')

# Get Status Record/Document Count
@api_view(['GET'])
def status_count(request):
    """
    Return Status Document Count
    """
    data = [] # JSON data array (query results)

    # Verify the connection
    try:
        connection = MongoClient(mongo_server_connection, serverSelectionTimeoutMS=30)
    except Exception as e:
        data = '[{"database error":' + e + '}]'
        return HttpResponse(data, content_type='application/json')

    # Get a count of the number of documents in the database and return to client
    db = connection[database]
    data = db[collection].count()
    connection.close()
    return HttpResponse(data, content_type='application/json')

# Find/Get A Single Document By Pattern
@api_view(['GET'])
def find_one_by_pattern(request):
    """
    Find And Return A Single Status Document Using Pattern (9999-99X)
    """
    try:
        pattern = request.GET['pattern']  # pattern to search for
    except Exception:
        pattern = ""

    data = [] # JSON data array (query results)

    # Verify the connection
    try:
        connection = MongoClient(mongo_server_connection, serverSelectionTimeoutMS=30)
    except Exception as e:
        data = '[{"database error":' + e + '}]'
        return HttpResponse(data, content_type='application/json')

    # Find a document database with the matching pattern and return to client
    db = connection[database]
    if (pattern != ""):
        data = json_util.dumps(db[collection].find_one({"pattern": pattern}))
    else:
        data = [{}]

    connection.close()
    return HttpResponse(data, content_type='application/json')

# Find/Get Multiple Documents By Partial Pattern
@api_view(['GET'])
def find_many_by_pattern(request):
    """
    Find And Return Multiple Status Documents Using Partial Pattern (999*)
    """
    try:
        pattern = request.GET['pattern']  # pattern to search for
    except Exception:
        pattern = ""

    data = [] # JSON data array (query results)

    # Verify the connection
    try:
        connection = MongoClient(mongo_server_connection, serverSelectionTimeoutMS=30)
    except Exception as e:
        data = '[{"database error":' + e + '}]'
        return HttpResponse(data, content_type='application/json')

    # Find the documents in the database where the pattern starts with "x" and return to client
    db = connection[database]
    if (pattern != ""):
        search_pattern = "^" + pattern
        data = json_util.dumps(db[collection].find({ "pattern": re.compile(search_pattern, re.IGNORECASE)}))
    else:
        data = [{}]

    connection.close()
    return HttpResponse(data, content_type='application/json')

# Delete A Single Document By Pattern
@api_view(['DELETE'])
def delete_one_by_pattern(request):
    """
    Delete A Single Status Document Using Pattern (9999-99X)
    """
    try:
        pattern = request.GET['pattern']  # pattern to search for
    except Exception:
        pattern = ""

    data = [] # JSON data array (query results)

    # Verify the connection
    try:
        connection = MongoClient(mongo_server_connection, serverSelectionTimeoutMS=30)
    except Exception as e:
        data = '[{"database error":' + e + '}]'
        return HttpResponse(data, content_type='application/json')

    # Find a document database with the matching pattern and return to client
    db = connection[database]
    if (pattern != ""):
        data = json_util.dumps(db[collection].find_one({"pattern": pattern}))
    else:
        data = [{}]

    connection.close()
    return HttpResponse(data, content_type='application/json')
