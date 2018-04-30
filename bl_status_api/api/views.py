# REST API Libraries
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

# MongoDB Client Libraries
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from bson import json_util
from bson.objectid import ObjectId # MongoDB native _id parsing support

# Misc. Django Libraries
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings

# Misc. Python Libraries
import re # regular expression support
import ast # literal evaluation support (e.g. string to dictionary)
import pprint
import json
import logging
import os
import collections

# Python Date/Time Libraries
from datetime import datetime, timedelta
import pytz

# Password Hashing & Web Token Authentication Libraies
from passlib.hash import pbkdf2_sha256
import jwt

# BSON/JSON formatting Libraries
from bson.codec_options import CodecOptions
from bson import json_util

#
# GLOBAL VARIABLES
#
mongo_server_connection = 'mongodb://172.16.168.110:27017/' # prod db server
database = 'test_database' # test database
collection = 'status_test' # test collection (table)
user_collection = 'status_test_users' # test user collection (table)
log_collection = 'status_test_log' # test log collection (table)
file_cat_collection = 'status_test_file_cat' # test file catalog collection (table)

# JWT (JSON Web Token) CONFIG VARIABLES
JWT_SECRET = "#ThisIsASecret!"  # private encryption key
JWT_ALGORITHM = "HS256"         # encryption algorithm
JWT_EXP_DELTA_SECONDS = 3600    # token expiration time (in seconds)
#JWT_EXP_DELTA_SECONDS = 600    # token expiration time (in seconds)

#
# CONFIGURE LOGGING
#
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('bl-status-api.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

#
# API DEFAULT/WELCOME RESPONSE
#
@api_view(['GET'])
def root(request):
    """
    Return Generic/Default Welcome Text Response.
    """
    logger.info("Request: root")

    data = 'Welcome to the EMS bl-status REST API. Unauthorized Access is Prohibited. 2017 - Executive Mailing Service'
    return HttpResponse(data)

#
# GET ALL STATUS RECORDS/DOCUMENTS
#
@api_view(['GET'])
def all_statuses(request):
    """
    Return All Status Documents
    """
    logger.info("Request: all_statuses")

    data = [] # JSON data array (query results)

    # open/verify the db connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        data = [{"database error": str(e)}]
        return Response(data)

    # get all the status records in the database and return to client (w/ JSON Serialization)
    db = connection[database]
    data = json_util.dumps(db[collection].find({}))
    # close db connection
    connection.close()
    return HttpResponse(data, content_type='application/json')

#
# GET STATUS RECORD (DOCUMENT) COUNT
#
@api_view(['GET'])
def status_count(request):
    """
    Return Current Status Document (Record) Count
    """
    logger.info("Request: status_count")

    data = [] # JSON data array (query results)

    # open/verify the db connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        data = [{"database error": str(e)}]
        return Response(data)

    # get a count of the number of documents in the database and return to client
    db = connection[database]
    data = db[collection].count()
    # close db connection
    connection.close()
    return HttpResponse(data, content_type='application/json')

#
# FIND/GET A SINGLE DOCUMENT BY PATTERN CODE
#
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

    # open/verify the db connection
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

    # close db connection
    connection.close()
    
    return HttpResponse(data, content_type='application/json')

#
# FIND/GET MULTIPLE DOCUMENTS BY PARTIAL PATTERN CODE
#
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

    # open/verify the db connection
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

    # close db connection
    connection.close()

    return HttpResponse(data, content_type='application/json')

#
# DELETE A SINGLE DOCUMENT BY PATTERN CODE
#
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

    # open/verify the db connection
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

    # close db connection
    connection.close()

    return Response(data)

#
# DELETE ALL MATCHING DOCUMENTS BY A PARTIAL PATTERN CODE
#
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

    # open/verify the db connection
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

    # close db connection
    connection.close()

    return Response(data)

#
# INSERT A SINGLE NEW STATUS DOCUMENT
#
@api_view(['POST'])
def insert_one(request):
    """
    Insert a Single New Status Document and Return the New id
    """
    logger.info("Request: insert_one: --")
    
    try:
        status_data = request.data
    except Exception:
        status_data = ""

    id = {} # storage new id after insert

    # parse/verify/reformat incoming data from client
    d = collections.OrderedDict() # storage for reformatted document w/ appended fields

    # - qualID
    if ('qualID' in status_data):
        d['qualID'] = status_data['qualID']
        logger.info("Request: insert_one: [qualID] key value: " + str(status_data['qualID']))
        #print("Request: insert_one: [qualID] key value: " + str(status_data['qualID']))
    else:
        logger.info("Request: insert_one: missing [qualID] key value")
        #print("Request: insert_one: missing [qualID] key value")

    # - projectID
    if ('projectID' in status_data):
        d['projectID'] = status_data['projectID']
        logger.info("Request: insert_one: [projectID] key value: " + str(status_data['projectID']))
        #print("Request: insert_one: [projectID] key value: " + str(status_data['projectID']))
    else:
        logger.info("Request: insert_one: missing [projectID] key value")
        #print("Request: insert_one: missing [projectID] key value")

    # - pattern
    if ('pattern' in status_data):
        d['pattern'] = status_data['pattern']
        logger.info("Request: insert_one: [pattern] key value: " + str(status_data['pattern']))
        #print("Request: insert_one: [pattern] key value: " + str(status_data['pattern']))
    else:
        logger.info("Request: insert_one: missing [pattern] key value")
        #print("Request: insert_one: missing [pattern] key value")

    # - total
    if ('total' in status_data):
        d['total'] = status_data['total']
        logger.info("Request: insert_one: [total] key value: " + str(status_data['total']))
        #print("Request: insert_one: [total] key value: " + str(status_data['total']))
    else:
        logger.info("Request: insert_one: missing [total] key value")
        #print("Request: insert_one: missing [total] key value")
    
    # - presort
    if ('presort' in status_data):
        d['presort'] = status_data['presort']
        logger.info("Request: insert_one: [presort] key value: " + str(status_data['presort']))
        #print("Request: insert_one: [presort] key value: " + str(status_data['presort']))
    else:
        logger.info("Request: insert_one: missing [presort] key value")
        #print("Request: insert_one: missing [presort] key value")
    
    # - fail
    if ('fail' in status_data):
        d['fail'] = status_data['fail']
        logger.info("Request: insert_one: [fail] key value: " + str(status_data['fail']))
        #print("Request: insert_one: [fail] key value: " + str(status_data['fail']))
    else:
        logger.info("Request: insert_one: missing [fail] key value")
        #print("Request: insert_one: missing [fail] key value")

    # - spr
    if ('spr' in status_data):
        d['spr'] = status_data['spr']
        logger.info("Request: insert_one: [spr] key value: " + str(status_data['spr']))
        #print("Request: insert_one: [spr] key value: " + str(status_data['spr']))
    else:
        logger.info("Request: insert_one: missing [spr] key value")
        #print("Request: insert_one: missing [spr] key value")

    # - mailClass
    if ('mailClass' in status_data):
        d['mailClass'] = status_data['mailClass']
        logger.info("Request: insert_one: [mailClass] key value: " + str(status_data['mailClass']))
        #print("Request: insert_one: [mailClass] key value: " + str(status_data['mailClass']))
    else:
        logger.info("Request: insert_one: missing [mailClass] key value")
        #print("Request: insert_one: missing [mailClass] key value")

    # - type
    if ('type' in status_data):
        d['type'] = status_data['type']
        logger.info("Request: insert_one: [type] key value: " + str(status_data['type']))
        #print("Request: insert_one: [type] key value: " + str(status_data['type']))
    else:
        logger.info("Request: insert_one: missing [type] key value")
        #print("Request: insert_one: missing [type] key value")

    # - specs
    if ('specs' in status_data):
        d['specs'] = status_data['specs']
        logger.info("Request: insert_one: [specs] key value: " + str(status_data['specs']))
        #print("Request: insert_one: [specs] key value: " + str(status_data['specs']))
    else:
        logger.info("Request: insert_one: missing [specs] key value")
        #print("Request: insert_one: missing [specs] key value")

    # - counts
    if ('counts' in status_data):
        d['counts'] = status_data['counts']
        logger.info("Request: insert_one: [counts] key value: " + str(status_data['counts']))
        #print("Request: insert_one: [counts] key value: " + str(status_data['counts']))
    else:
        logger.info("Request: insert_one: missing [counts] key value")
        #print("Request: insert_one: missing [counts] key value")
    
    # - isCurrent
    if ('isCurrent' in status_data):
        d['isCurrent'] = status_data['isCurrent']
        logger.info("Request: insert_one: [isCurrent] key value: " + str(status_data['isCurrent']))
        #print("Request: insert_one: [isCurrent] key value: " + str(status_data['isCurrent']))
    else:
        logger.info("Request: insert_one: missing [isCurrent] key value")
        #print("Request: insert_one: missing [isCurrent] key value")
    
    # - fileStamp
    if ('fileStamp' in status_data):
        d['fileStamp'] = status_data['fileStamp']
        logger.info("Request: insert_one: [fileStamp] key value: " + str(status_data['fileStamp']))
        #print("Request: insert_one: [fileStamp] key value: " + str(status_data['fileStamp']))
    else:
        logger.info("Request: insert_one: missing [fileStamp] key value")
        #print("Request: insert_one: missing [fileStamp] key value")
    
    # - timeStamp
    if ('timeStamp' in status_data):
        d['timeStamp'] = status_data['timeStamp']
        logger.info("Request: insert_one: [timeStamp] key value: " + str(status_data['timeStamp']))
        #print("Request: insert_one: [timeStamp] key value: " + str(status_data['timeStamp']))
    else:
        logger.info("Request: insert_one: missing [timeStamp] key value")
        #print("Request: insert_one: missing [timeStamp] key value")
    
    # - isSampleComplete
    if ('isSampleComplete' in status_data):
        d['isSampleComplete'] = status_data['isSampleComplete']
        logger.info("Request: insert_one: [isSampleComplete] key value: " + str(status_data['isSampleComplete']))
        #print("Request: insert_one: [isSampleComplete] key value: " + str(status_data['isSampleComplete']))
    else:
        logger.info("Request: insert_one: missing [isSampleComplete] key value")
        #print("Request: insert_one: missing [isSampleComplete] key value")
    
    # - sampleStamp
    if ('sampleStamp' in status_data):
        d['sampleStamp'] = status_data['sampleStamp']
        logger.info("Request: insert_one: [sampleStamp] key value: " + str(status_data['sampleStamp']))
        #print("Request: insert_one: [sampleStamp] key value: " + str(status_data['sampleStamp']))
    else:
        logger.info("Request: insert_one: missing [sampleStamp] key value")
        #print("Request: insert_one: missing [sampleStamp] key value")

    # - isAcctcomplete
    if ('isAcctcomplete' in status_data):
        d['isAcctcomplete'] = status_data['isAcctcomplete']
        logger.info("Request: insert_one: [isAcctcomplete] key value: " + str(status_data['isAcctcomplete']))
        #print("Request: insert_one: [isAcctcomplete] key value: " + str(status_data['isAcctcomplete']))
    else:
        logger.info("Request: insert_one: missing [isAcctcomplete] key value")
        #print("Request: insert_one: missing [isAcctcomplete] key value")
    
    # - AcctStamp
    if ('AcctStamp' in status_data):
        d['AcctStamp'] = status_data['AcctStamp']
        logger.info("Request: insert_one: [AcctStamp] key value: " + str(status_data['AcctStamp']))
        #print("Request: insert_one: [AcctStamp] key value: " + str(status_data['AcctStamp']))
    else:
        logger.info("Request: insert_one: missing [AcctStamp] key value")
        #print("Request: insert_one: missing [AcctStamp] key value")
    
    # - trayMax
    if ('trayMax' in status_data):
        d['trayMax'] = status_data['trayMax']
        logger.info("Request: insert_one: [trayMax] key value: " + str(status_data['trayMax']))
        #print("Request: insert_one: [trayMax] key value: " + str(status_data['trayMax']))
    else:
        logger.info("Request: insert_one: missing [trayMax] key value")
        #print("Request: insert_one: missing [trayMax] key value")
    
    # - dpUser
    if ('dpUser' in status_data):
        d['dpUser'] = status_data['dpUser']
        logger.info("Request: insert_one: [dpUser] key value: " + str(status_data['dpUser']))
        #print("Request: insert_one: [dpUser] key value: " + str(status_data['dpUser']))
    else:
        logger.info("Request: insert_one: missing [dpUser] key value")
        #print("Request: insert_one: missing [dpUser] key value")
    
    # - sasUser
    if ('sasUser' in status_data):
        d['sasUser'] = status_data['sasUser']
        logger.info("Request: insert_one: [sasUser] key value: " + str(status_data['sasUser']))
        #print("Request: insert_one: [sasUser] key value: " + str(status_data['sasUser']))
    else:
        logger.info("Request: insert_one: missing [sasUser] key value")
        #print("Request: insert_one: missing [sasUser] key value")
    
    # - acctUser
    if ('acctUser' in status_data):
        d['acctUser'] = status_data['acctUser']
        logger.info("Request: insert_one: [acctUser] key value: " + str(status_data['acctUser']))
        #print("Request: insert_one: [acctUser] key value: " + str(status_data['acctUser']))
    else:
        logger.info("Request: insert_one: missing [acctUser] key value")
        #print("Request: insert_one: missing [acctUser] key value")
    
    # - isEpop
    if ('isEpop' in status_data):
        d['isEpop'] = status_data['isEpop']
        logger.info("Request: insert_one: [isEpop] key value: " + str(status_data['isEpop']))
        #print("Request: insert_one: [isEpop] key value: " + str(status_data['isEpop']))
    else:
        logger.info("Request: insert_one: missing [isEpop] key value")
        #print("Request: insert_one: missing [isEpop] key value")
    
    # - isTagsComplete
    if ('isTagsComplete' in status_data):
        d['isTagsComplete'] = status_data['isTagsComplete']
        logger.info("Request: insert_one: [isTagsComplete] key value: " + str(status_data['isTagsComplete']))
        #print("Request: insert_one: [isTagsComplete] key value: " + str(status_data['isTagsComplete']))
    else:
        logger.info("Request: insert_one: missing [isTagsComplete] key value")
        #print("Request: insert_one: missing [isTagsComplete] key value")
    
    # - TagsStamp
    if ('TagsStamp' in status_data):
        d['TagsStamp'] = status_data['TagsStamp']
        logger.info("Request: insert_one: [TagsStamp] key value: " + str(status_data['TagsStamp']))
        #print("Request: insert_one: [TagsStamp] key value: " + str(status_data['TagsStamp']))
    else:
        logger.info("Request: insert_one: missing [TagsStamp] key value")
        #print("Request: insert_one: missing [TagsStamp] key value")
    
    # - tagsUser
    if ('tagsUser' in status_data):
        d['tagsUser'] = status_data['tagsUser']
        logger.info("Request: insert_one: [tagsUser] key value: " + str(status_data['tagsUser']))
        #print("Request: insert_one: [tagsUser] key value: " + str(status_data['tagsUser']))
    else:
        logger.info("Request: insert_one: missing [tagsUser] key value")
        #print("Request: insert_one: missing [tagsUser] key value")
    
    # - hasCRRT
    if ('hasCRRT' in status_data):
        d['hasCRRT'] = status_data['hasCRRT']
        logger.info("Request: insert_one: [hasCRRT] key value: " + str(status_data['hasCRRT']))
        #print("Request: insert_one: [hasCRRT] key value: " + str(status_data['hasCRRT']))
    else:
        logger.info("Request: insert_one: missing [hasCRRT] key value")
        #print("Request: insert_one: missing [hasCRRT] key value")
    
    # - hasOrigin
    if ('hasOrigin' in status_data):
        d['hasOrigin'] = status_data['hasOrigin']
        logger.info("Request: insert_one: [hasOrigin] key value: " + str(status_data['hasOrigin']))
        #print("Request: insert_one: [hasOrigin] key value: " + str(status_data['hasOrigin']))
    else:
        logger.info("Request: insert_one: missing [hasOrigin] key value")
        #print("Request: insert_one: missing [hasOrigin] key value")
    
    # - projectName
    if ('projectName' in status_data):
        d['projectName'] = status_data['projectName']
        logger.info("Request: insert_one: [projectName] key value: " + str(status_data['projectName']))
        #print("Request: insert_one: [projectName] key value: " + str(status_data['projectName']))
    else:
        logger.info("Request: insert_one: missing [projectName] key value")
        #print("Request: insert_one: missing [projectName] key value")
    
    # - client
    if ('client' in status_data):
        d['client'] = status_data['client']
        logger.info("Request: insert_one: [client] key value: " + str(status_data['client']))
        #print("Request: insert_one: [client] key value: " + str(status_data['client']))
    else:
        logger.info("Request: insert_one: missing [client] key value")
        #print("Request: insert_one: missing [client] key value")
     
    # - EstDropDate
    if (('EstDropDate' in status_data) and (str(status_data['EstDropDate']) != "None")):
        #d['dropDate'] = status['EstDropDate']
        d['dropDate'] = datetime.strptime(str(status_data['EstDropDate']),'%Y-%m-%dT%H:%M:%S').strftime('%m/%d/%y')
        logger.info("Request: insert_one: [EstDropDate] key value: " + str(status_data['EstDropDate']))
        #print("Request: insert_one: [EstDropDate] key value: " + str(status_data['EstDropDate']))
    else:
        d['dropDate'] = None
        logger.info("Request: insert_one: missing [EstDropDate] key value")
        #print("Request: insert_one: missing [EstDropDate] key value")
    
    # Appended Fields (bl-status)
    d['sampleStatus'] = "New" 
    d['paperworkStatus'] = "New" 
    d['palletTagFileUser'] = ""
    d['palletTagFileDownloadCount'] = 0
    d['currentPalletTagFile'] = " "
    d['palletTagFileUploadDateTime'] = ""
    d['palletWorksheetFileUser'] = ""
    d['palletWorksheetFileDownloadCount'] = 0
    d['palletWorksheetFileUploadDateTime'] = ""
    d['currentPalletWorksheetFile'] = ""
    d['palletTagReplacementCount'] = 0
    d['palletWorksheetReplacementCount'] = 0
    d['postalAccountingNotes'] = ""
    d['sampleRoomNotes'] = ""

    if (status_data['isEpop'] == True):
        logger.info("Request: insert_one: EPOP Pattern Detected - Bypassing Database Insert")
        #print("Request: insert_one: EPOP Pattern Detected - Bypassing Database Insert")

    # open/verify the db connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        data = [{"database error": str(e)}]
        return Response(data)
    
    # insert the new document (only if it's not blank and not EPOP)
    db = connection[database]
    if ((status_data != "") and (status_data['isEpop'] != True)):
        #id = json_util.dumps(db[collection].insert_one(status_data).inserted_id)
        id = json_util.dumps(db[collection].insert_one(d).inserted_id)
    else:
        id = {}
    
    # close db connection
    connection.close()

    # convert response to dictionary (for JSON response serialization)
    if ((status_data != "") and (status_data['isEpop'] != True)):
        id_dict = ast.literal_eval(id)
        oid = id_dict['$oid']
        return Response({'inserted_id': oid })
    else:
        return Response({'inserted_id': "EPOP" })

#    
# INSERT MANY NEW STATUS DOCUMENTS
#
@api_view(['POST'])
def insert_many(request):
    """
    Insert Many New Status Documents and Return an Array of the New id's
    """
    logger.info("Request: insert_many: --")

    try:
        status_data = request.data
    except Exception:
        status_data = ""

    ids = "" # new id's

    # open/verify the db connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        data = [{"database error": str(e)}]
        return Response(data)
    
    # parse/verify/reformat incoming data (array of many documents) from client
    m = [] # storage for the array of many documents
    i = 1  # document counter

    # - loop through documents (many) and append reformatted documents to document array (m)
    for status in status_data:
        d = collections.OrderedDict() # storage for reformatted document w/ appended fields
        
        logger.info("Request: insert_many: *** Document #: " + str(i))
        #print("Request: insert_many: *** Document #: " + str(i))

        # - qualID
        if ('qualID' in status):
            d['qualID'] = status['qualID']
            logger.info("Request: insert_many: [qualID] key value: " + str(status['qualID']))
            #print("Request: insert_many: [qualID] key value: " + str(status['qualID']))
        else:
            logger.info("Request: insert_many: missing [qualID] key value")
            #print("Request: insert_many: missing [qualID] key value")

        # - projectID
        if ('projectID' in status):
            d['projectID'] = status['projectID']
            logger.info("Request: insert_many: [projectID] key value: " + str(status['projectID']))
            #print("Request: insert_many: [projectID] key value: " + str(status['projectID']))
        else:
            logger.info("Request: insert_many: missing [projectID] key value")
            #print("Request: insert_many: missing [projectID] key value")

        # - pattern
        if ('pattern' in status):
            d['pattern'] = status['pattern']
            logger.info("Request: insert_many: [pattern] key value: " + str(status['pattern']))
            #print("Request: insert_many: [pattern] key value: " + str(status['pattern']))
        else:
            logger.info("Request: insert_many: missing [pattern] key value")
            #print("Request: insert_many: missing [pattern] key value")

        # - total
        if ('total' in status):
            d['total'] = status['total']
            logger.info("Request: insert_many: [total] key value: " + str(status['total']))
            #print("Request: insert_many: [total] key value: " + str(status['total']))
        else:
            logger.info("Request: insert_many: missing [total] key value")
            #print("Request: insert_many: missing [total] key value")
        
        # - presort
        if ('presort' in status):
            d['presort'] = status['presort']
            logger.info("Request: insert_many: [presort] key value: " + str(status['presort']))
            #print("Request: insert_many: [presort] key value: " + str(status['presort']))
        else:
            logger.info("Request: insert_many: missing [presort] key value")
            #print("Request: insert_many: missing [presort] key value")
        
        # - fail
        if ('fail' in status):
            d['fail'] = status['fail']
            logger.info("Request: insert_many: [fail] key value: " + str(status['fail']))
            #print("Request: insert_many: [fail] key value: " + str(status['fail']))
        else:
            logger.info("Request: insert_many: missing [fail] key value")
            #print("Request: insert_many: missing [fail] key value")

        # - spr
        if ('spr' in status):
            d['spr'] = status['spr']
            logger.info("Request: insert_many: [spr] key value: " + str(status['spr']))
            #print("Request: insert_many: [spr] key value: " + str(status['spr']))
        else:
            logger.info("Request: insert_many: missing [spr] key value")
            #print("Request: insert_many: missing [spr] key value")

        # - mailClass
        if ('mailClass' in status):
            d['mailClass'] = status['mailClass']
            logger.info("Request: insert_many: [mailClass] key value: " + str(status['mailClass']))
            #print("Request: insert_many: [mailClass] key value: " + str(status['mailClass']))
        else:
            logger.info("Request: insert_many: missing [mailClass] key value")
            #print("Request: insert_many: missing [mailClass] key value")

        # - type
        if ('type' in status):
            d['type'] = status['type']
            logger.info("Request: insert_many: [type] key value: " + str(status['type']))
            #print("Request: insert_many: [type] key value: " + str(status['type']))
        else:
            logger.info("Request: insert_many: missing [type] key value")
            #print("Request: insert_many: missing [type] key value")

        # - specs
        if ('specs' in status):
            d['specs'] = status['specs']
            logger.info("Request: insert_many: [specs] key value: " + str(status['specs']))
            #print("Request: insert_many: [specs] key value: " + str(status['specs']))
        else:
            logger.info("Request: insert_many: missing [specs] key value")
            #print("Request: insert_many: missing [specs] key value")

        # - counts
        if ('counts' in status):
            d['counts'] = status['counts']
            logger.info("Request: insert_many: [counts] key value: " + str(status['counts']))
            #print("Request: insert_many: [counts] key value: " + str(status['counts']))
        else:
            logger.info("Request: insert_many: missing [counts] key value")
            #print("Request: insert_many: missing [counts] key value")
        
        # - isCurrent
        if ('isCurrent' in status):
            d['isCurrent'] = status['isCurrent']
            logger.info("Request: insert_many: [isCurrent] key value: " + str(status['isCurrent']))
            #print("Request: insert_many: [isCurrent] key value: " + str(status['isCurrent']))
        else:
            logger.info("Request: insert_many: missing [isCurrent] key value")
            #print("Request: insert_many: missing [isCurrent] key value")
        
        # - fileStamp
        if ('fileStamp' in status):
            d['fileStamp'] = status['fileStamp']
            logger.info("Request: insert_many: [fileStamp] key value: " + str(status['fileStamp']))
            #print("Request: insert_many: [fileStamp] key value: " + str(status['fileStamp']))
        else:
            logger.info("Request: insert_many: missing [fileStamp] key value")
            #print("Request: insert_many: missing [fileStamp] key value")
        
        # - timeStamp
        if ('timeStamp' in status):
            d['timeStamp'] = status['timeStamp']
            logger.info("Request: insert_many: [timeStamp] key value: " + str(status['timeStamp']))
            #print("Request: insert_many: [timeStamp] key value: " + str(status['timeStamp']))
        else:
            logger.info("Request: insert_many: missing [timeStamp] key value")
            #print("Request: insert_many: missing [timeStamp] key value")
        
        # - isSampleComplete
        if ('isSampleComplete' in status):
            d['isSampleComplete'] = status['isSampleComplete']
            logger.info("Request: insert_many: [isSampleComplete] key value: " + str(status['isSampleComplete']))
            #print("Request: insert_many: [isSampleComplete] key value: " + str(status['isSampleComplete']))
        else:
            logger.info("Request: insert_many: missing [isSampleComplete] key value")
            #print("Request: insert_many: missing [isSampleComplete] key value")
        
        # - sampleStamp
        if ('sampleStamp' in status):
            d['sampleStamp'] = status['sampleStamp']
            logger.info("Request: insert_many: [sampleStamp] key value: " + str(status['sampleStamp']))
            #print("Request: insert_many: [sampleStamp] key value: " + str(status['sampleStamp']))
        else:
            logger.info("Request: insert_many: missing [sampleStamp] key value")
            #print("Request: insert_many: missing [sampleStamp] key value")

        # - isAcctcomplete
        if ('isAcctcomplete' in status):
            d['isAcctcomplete'] = status['isAcctcomplete']
            logger.info("Request: insert_many: [isAcctcomplete] key value: " + str(status['isAcctcomplete']))
            #print("Request: insert_many: [isAcctcomplete] key value: " + str(status['isAcctcomplete']))
        else:
            logger.info("Request: insert_many: missing [isAcctcomplete] key value")
            #print("Request: insert_many: missing [isAcctcomplete] key value")
        
        # - AcctStamp
        if ('AcctStamp' in status):
            d['AcctStamp'] = status['AcctStamp']
            logger.info("Request: insert_many: [AcctStamp] key value: " + str(status['AcctStamp']))
            #print("Request: insert_many: [AcctStamp] key value: " + str(status['AcctStamp']))
        else:
            logger.info("Request: insert_many: missing [AcctStamp] key value")
            #print("Request: insert_many: missing [AcctStamp] key value")
        
        # - trayMax
        if ('trayMax' in status):
            d['trayMax'] = status['trayMax']
            logger.info("Request: insert_many: [trayMax] key value: " + str(status['trayMax']))
            #print("Request: insert_many: [trayMax] key value: " + str(status['trayMax']))
        else:
            logger.info("Request: insert_many: missing [trayMax] key value")
            #print("Request: insert_many: missing [trayMax] key value")
        
        # - dpUser
        if ('dpUser' in status):
            d['dpUser'] = status['dpUser']
            logger.info("Request: insert_many: [dpUser] key value: " + str(status['dpUser']))
            #print("Request: insert_many: [dpUser] key value: " + str(status['dpUser']))
        else:
            logger.info("Request: insert_many: missing [dpUser] key value")
            #print("Request: insert_many: missing [dpUser] key value")
        
        # - sasUser
        if ('sasUser' in status):
            d['sasUser'] = status['sasUser']
            logger.info("Request: insert_many: [sasUser] key value: " + str(status['sasUser']))
            #print("Request: insert_many: [sasUser] key value: " + str(status['sasUser']))
        else:
            logger.info("Request: insert_many: missing [sasUser] key value")
            #print("Request: insert_many: missing [sasUser] key value")
        
        # - acctUser
        if ('acctUser' in status):
            d['acctUser'] = status['acctUser']
            logger.info("Request: insert_many: [acctUser] key value: " + str(status['acctUser']))
            #print("Request: insert_many: [acctUser] key value: " + str(status['acctUser']))
        else:
            logger.info("Request: insert_many: missing [acctUser] key value")
            #print("Request: insert_many: missing [acctUser] key value")
        
        # - isEpop
        if ('isEpop' in status):
            d['isEpop'] = status['isEpop']
            #print("Request: insert_many: [isEpop] key value: " + str(status['isEpop']))
        else:
            logger.info("Request: insert_many: missing [isEpop] key value")
            #print("Request: insert_many: missing [isEpop] key value")
        
        # - isTagsComplete
        if ('isTagsComplete' in status):
            d['isTagsComplete'] = status['isTagsComplete']
            logger.info("Request: insert_many: [isTagsComplete] key value: " + str(status['isTagsComplete']))
            #print("Request: insert_many: [isTagsComplete] key value: " + str(status['isTagsComplete']))
        else:
            logger.info("Request: insert_many: missing [isTagsComplete] key value")
            #print("Request: insert_many: missing [isTagsComplete] key value")
        
        # - TagsStamp
        if ('TagsStamp' in status):
            d['TagsStamp'] = status['TagsStamp']
            logger.info("Request: insert_many: [TagsStamp] key value: " + str(status['TagsStamp']))
            #print("Request: insert_many: [TagsStamp] key value: " + str(status['TagsStamp']))
        else:
            logger.info("Request: insert_many: missing [TagsStamp] key value")
            #print("Request: insert_many: missing [TagsStamp] key value")
        
        # - tagsUser
        if ('tagsUser' in status):
            d['tagsUser'] = status['tagsUser']
            logger.info("Request: insert_many: [tagsUser] key value: " + str(status['tagsUser']))
            #print("Request: insert_many: [tagsUser] key value: " + str(status['tagsUser']))
        else:
            logger.info("Request: insert_many: missing [tagsUser] key value")
            #print("Request: insert_many: missing [tagsUser] key value")
        
        # - hasCRRT
        if ('hasCRRT' in status):
            d['hasCRRT'] = status['hasCRRT']
            logger.info("Request: insert_many: [hasCRRT] key value: " + str(status['hasCRRT']))
            #print("Request: insert_many: [hasCRRT] key value: " + str(status['hasCRRT']))
        else:
            logger.info("Request: insert_many: missing [hasCRRT] key value")
            #print("Request: insert_many: missing [hasCRRT] key value")
        
        # - hasOrigin
        if ('hasOrigin' in status):
            d['hasOrigin'] = status['hasOrigin']
            logger.info("Request: insert_many: [hasOrigin] key value: " + str(status['hasOrigin']))
            #print("Request: insert_many: [hasOrigin] key value: " + str(status['hasOrigin']))
        else:
            logger.info("Request: insert_many: missing [hasOrigin] key value")
            #print("Request: insert_many: missing [hasOrigin] key value")
        
        # - projectName
        if ('projectName' in status):
            d['projectName'] = status['projectName']
            logger.info("Request: insert_many: [projectName] key value: " + str(status['projectName']))
            #print("Request: insert_many: [projectName] key value: " + str(status['projectName']))
        else:
            logger.info("Request: insert_many: missing [projectName] key value")
            #print("Request: insert_many: missing [projectName] key value")
        
        # - client
        if ('client' in status):
            d['client'] = status['client']
            logger.info("Request: insert_many: [client] key value: " + str(status['client']))
            #print("Request: insert_many: [client] key value: " + str(status['client']))
        else:
            logger.info("Request: insert_many: missing [client] key value")
            #print("Request: insert_many: missing [client] key value")
        
        # - EstDropDate
        if (('EstDropDate' in status) and (str(status['EstDropDate']) != "None")):
            #d['dropDate'] = status['EstDropDate']
            d['dropDate'] = datetime.strptime(str(status['EstDropDate']),'%Y-%m-%dT%H:%M:%S').strftime('%m/%d/%y')
            logger.info("Request: insert_many: [EstDropDate] key value: " + str(status['EstDropDate']))
            #print("Request: insert_many: [EstDropDate] key value: " + str(status['EstDropDate']))
        else:
            d['dropDate'] = None
            logger.info("Request: insert_many: missing [EstDropDate] key value")
            #print("Request: insert_many: missing [EstDropDate] key value")
        
        # Appended Fields (bl-status)
        d['sampleStatus'] = "New" 
        d['paperworkStatus'] = "New" 
        d['palletTagFileUser'] = ""
        d['palletTagFileDownloadCount'] = 0
        d['currentPalletTagFile'] = " "
        d['palletTagFileUploadDateTime'] = ""
        d['palletWorksheetFileUser'] = ""
        d['palletWorksheetFileDownloadCount'] = 0
        d['palletWorksheetFileUploadDateTime'] = ""
        d['currentPalletWorksheetFile'] = ""
        d['palletTagReplacementCount'] = 0
        d['palletWorksheetReplacementCount'] = 0
        d['postalAccountingNotes'] = ""
        d['sampleRoomNotes'] = ""

        # append the reformatted document to the array (only if it's not EPOP)
        if (status['isEpop'] != True):
            m.append(d)
            # increment document counter
            i += 1
        else:
            logger.info("Request: insert_many: EPOP Pattern Detected - Bypassing Database Insert")
            #print("Request: insert_many: EPOP Pattern Detected - Bypassing Database Insert")
        
    # insert the new documents (if there are any Non-EPOP status documents)
    db = connection[database]
    if (m != []):
        #ids = json_util.dumps(db[collection].insert_many(status_data).inserted_ids)
        ids = json_util.dumps(db[collection].insert_many(m).inserted_ids)
    else:
        ids = ""
    
    connection.close()

    # convert response (array of inserted id's) to dictionary list (for JSON response serialization)
    if (m != []):
        ids_dict = ast.literal_eval(ids)
        oids = []
        
        for id in ids_dict:
            oids.append(id['$oid'])

        return Response({'inserted_ids': oids })
    else:
        return Response({'inserted_ids': [] })

#
# UPDATE A SINGLE STATUS DOCUMENT (BY ID)
#
@api_view(['PUT'])
def update_one(request):
    """
    Update a Single Status Document (by Id) and Return a Result Object
    """
    logger.info("Request: update_one")

    try:
        update_id = request.data['update_id']
        update_data = request.data['update_data']
    except Exception:
        update_id = ""
        update_data = ""

    # open/verify the db connection
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
    
    # close db connection
    connection.close()

    return Response(update_object.raw_result)

#
# UPDATE MANY STATUS DOCUMENTS (BY PATTERN)
#
@api_view(['PUT'])
def update_many_by_pattern(request):
    """
    Update Status Document (by Pattern) and Return a Result Object
    """
    logger.info("Request: update_many_by_pattern")

    try:
        update_pattern = request.data['update_pattern']
        update_data = request.data['update_data']
    except Exception:
        update_pattern = ""
        update_data = ""

    # open/verify the db connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        data = [{"database error": str(e)}]
        return Response(data)
    
    # update the document and return the Result Object
    db = connection[database]
    if ((update_pattern != "") and (update_data != "")):
        update_object = db[collection].update_many({'pattern' : update_pattern}, {'$set': update_data}, upsert=False)
    else:
        update_object = {}
    
    # close db connection
    connection.close()

    return Response(update_object.raw_result)

#
# VERIFY USER NAME IN THE DATABASE AND VERIFY THE PASSWORD, & RETURN AUTHENTICATION TOKEN
#
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

    # open/verify the db connection
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
#
# CHECK AN EXISTING JWT TOKEN FOR EXPIRATION
#
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

#
# RECEIVE AND STORE PDF/TEXT FILES FROM CONNECTED WEB CLIENTS
#
@api_view(['POST'])
@parser_classes((MultiPartParser, FormParser,)) # process/remove http header/footer data
@renderer_classes((PDFRenderer,)) # render binary PDF data for storage
def file_upload(request):
    """
    Receive and store PDF/Text files from connected web clients 
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

    # open/verify the db connection
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
        rc = cat_data['replacementCount']
        if (cat_data['fileType'] == "Pallet Tags"):
            db[collection].update_many({"pattern": pt },{"$set":{"currentPalletTagFile": fl, "palletTagFileUploadDateTime": tm, "palletTagFileUser": us, "palletTagFileDownloadCount": 0, "palletTagReplacementCount": rc}})
        else:
            db[collection].update_many({"pattern": pt },{"$set":{"currentPalletWorksheetFile": fl, "palletWorksheetFileUploadDateTime": tm,"palletWorksheetFileUser": us, "palletWorksheetFileDownloadCount": 0, "palletWorksheetReplacementCount": rc}})
    else:
        id = {}

    # update status
    data = db[collection].find_one({"pattern": pt })
    #print ("update data: " + json_util.dumps(data))
    if (data != "null"):
        if(data['paperworkStatus'] != "Issue"):
            if ((data['currentPalletTagFile'] != "") and (data['currentPalletTagFile'] != " ") and (data['currentPalletWorksheetFile'] != "") and (data['currentPalletWorksheetFile'] != " ")): 
                db[collection].update_many({"pattern": pt },{"$set":{"paperworkStatus": "Complete" }})
            else:
                db[collection].update_many({"pattern": pt },{"$set":{"paperworkStatus": "In Process" }})

    # close db connection
    connection.close()

    # convert response to dictionary (for JSON response serialization)
    id_dict = ast.literal_eval(id)
    oid = id_dict['$oid']

    logger.info("File Upload id for: " + cat_data['clientFilePath'] + ": " + json_util.dumps({'inserted_id': oid }))
    return Response({'inserted_id': oid })
    
# - store the rendered data (PDF) in a file on the local file system
def handle_uploaded_file(file, file_name):
    logger.info("File Upload: writting file [ " + file_name + " ]...")
    #print("File Upload: writting file [ " + file_name + " ]...")
    destination = open("uploaded_files/" + file_name, 'wb+')
    for chunk in file.chunks():
        destination.write(chunk)
    destination.close()
    logger.info("File Upload: file saved!")
    #print("File Upload: file saved!")

#
# RECIEVE AND STORE LOGGED EVENTS FROM CONNECTED WEB CLIENTS 
#
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

    # open/verify the db connection
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
        # add time stamp
        central_time = pytz.timezone('US/Central')
        tz_aware_datetime = central_time.localize(datetime.utcnow())
        log_data["timeStamp"] = tz_aware_datetime
        # DB insert
        id = json_util.dumps(db[log_collection].insert_one(log_data).inserted_id)
    else:
        id = {}
    
    # close db connection
    connection.close()

    # convert response to dictionary (for JSON response serialization)
    id_dict = ast.literal_eval(id)
    oid = id_dict['$oid']

    return Response({'inserted_id': oid })

#
# RETRIEVE LOG DATA FOR CLIENT APP OR SERVER
#
@api_view(['GET'])
def log_view(request):
    """
    Retrieve Log data and return to client
    """
    logger.info("Request: log_view")
    data = [{}] # JSON data array (query results)

    # get parameters
    try:
        log_type = request.GET['logType']  # log type for
    except Exception:
        log_type = ""
    
    try:
        start_date = request.GET['startDate']  # log start date range
    except Exception:
        start_date = ""

    try:
        end_date = request.GET['endDate']  # log end date range
    except Exception:
        end_date = ""
    
    # open/verify the db connection
    try:
        connection = MongoClient(mongo_server_connection)
    except Exception as e:
        data = [{"database error": str(e)}]
        return Response(data)
    
    # get log data and return it
    db = connection[database]
    if ((log_type != "") and (start_date != "") and (end_date != "")):
        # convert incoming date range to date/time format
        dt_start = datetime.strptime(start_date,"%m/%d/%y")
        dt_end = datetime.strptime(end_date,"%m/%d/%y")

        # get client application log
        if(log_type == "app"):
            # prepare for date range query (w/ timezone)
            s_year = dt_start.year
            s_month = dt_start.month
            s_day = dt_start.day
            #
            e_year = dt_end.year
            e_month = dt_end.month
            e_day = dt_end.day
            #
            qry_start_date = datetime(s_year, s_month, s_day)
            qry_start_date = qry_start_date.replace(tzinfo=pytz.timezone('US/Central'))
            qry_end_date = datetime(e_year, e_month, e_day)
            qry_end_date = qry_end_date + timedelta(days=1)
            qry_end_date = qry_end_date.replace(tzinfo=pytz.timezone('US/Central'))

            #print("start date: " + qry_start_date.strftime("%B %d, %Y, %H:%M:%S"))
            #print("end_date: " + qry_end_date.strftime("%B %d, %Y, %H:%M:%S"))

            # query database (apply timezone options)
            tz_aware_logs = db[log_collection].with_options(codec_options=CodecOptions(tz_aware=True,tzinfo=pytz.timezone('US/Central')))
            data = json_util.dumps(tz_aware_logs.find({ '$and': [{'timeStamp': {'$gte': qry_start_date}}, {'timeStamp': {'$lt': qry_end_date}}]}).sort("timeStamp", -1))

        # get server log
        if(log_type == "server"):
            data = [{"server data": "coming soon!"}]

        # close database connection and return data to client    
        connection.close()
        return HttpResponse(data, content_type='application/json')

    # invalid parms - return emtpy array
    else:
        data = [{}]
        connection.close()
        return HttpResponse(data, content_type='application/json')

#
# DELETE PDF FILE FOR A GIVEN PATTERN & UPDATE STATUS
#
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
    
    # open/verify the db connection
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
        if(data['paperworkStatus'] != "Issue"):
            if ((data['currentPalletTagFile'] != "") and (data['currentPalletTagFile'] != " ") and (data['currentPalletWorksheetFile'] != "") and (data['currentPalletWorksheetFile'] != " ")): 
                db[collection].update_many({"pattern": pattern },{"$set":{"paperworkStatus": "Complete" }})
            else:
                db[collection].update_many({"pattern": pattern },{"$set":{"paperworkStatus": "In Process" }})
    
    # remove metadata info from the file catalog
    db[file_cat_collection].delete_many({"pattern": pattern, "serverFilePath": file_name, "fileType": file_type})

    # close db connection
    connection.close()

    # delete the file from server folder
    try:
        if ((pattern != "") and (file_name != "") and (file_type != "")):
            destination = "uploaded_files/" + file_name
            os.remove(destination)
            logger.info("File: " + destination + " Deleted!")
            #print("File: " + destination + " Deleted!")
    except Exception as e:
        data = [{"file deletion error": str(e)}]
        return Response(data)

    return Response(update_object.raw_result)

#
# PDF FILE DOWNLOAD API ENDPOINT
#
@api_view(['POST'])
def file_download(request):
    """
    Download a given pattern's associated PDF file from server repository 
    and update status document 
    """
    logger.info("Request: file_download")
    logger.info("File Download MetaData: " + json_util.dumps(request.POST))

    # get the request body data (processing parameters)
    try:
        path = request.data['file']
        pattern = request.data['pattern']
        file_type = request.data['fileType']
    except Exception as e:
        logger.info("file download - url error")
        #print("file download - url error") 
        data = [{"file download url error": str(e)}]
        path = ""
        pattern = ""
        return Response(data)

    # read the file from the folder and return it to the client
    file_path = os.path.join("uploaded_files/", path)
    logger.info("file download - file_path: " + file_path)
    #print("file download - file_path: " + file_path) 
    if os.path.exists(file_path):
        # get file from the local filesystem
        with open(file_path, 'rb') as fh:
            # add the file to the http response
            response = HttpResponse(fh.read(), content_type="application/pdf")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            #print("file download - file path: " + file_path)
            logger.info("file download - file path: " + file_path + "pattern: " + pattern)
            # open/verify the db connection
            try:
                connection = MongoClient(mongo_server_connection)
            except Exception as e:
                data = [{"database error": str(e)}]
                #print("file download - database connection error: " + str(e))
                logger.error("file - download database connection error: " + str(e))
                return Response(data)
            # update the file download count
            db = connection[database]
            if(file_type == "Pallet Tags"):
                db[collection].update_many({"pattern": pattern },{"$inc":{"palletTagFileDownloadCount": 1}})
                #print("file download - updated Pallet Tag Download Count")
                logger.info("file download - updated Pallet Tag Download Count - Pattern: " + pattern)
            if(file_type == "Pallet Worksheet"):
                db[collection].update_many({"pattern": pattern },{"$inc":{"palletWorksheetFileDownloadCount": 1}})
                #print("file download - updated Pallet Worksheet Download Count")
                logger.info("file download - updated Pallet Worksheet Count - Pattern: " + pattern)
            # close db connection
            connection.close()
            # return http response (w/ file data)
            return response

