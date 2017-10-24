from datetime import datetime, timedelta
from pymongo import MongoClient
from bson import json_util
import json

"""
Update/Change the shape of Status documents
"""

# Global variables
mongo_server_connection = 'mongodb://172.16.168.110:27017/' # prod db server
database = 'test_database' # test database
collection = 'status_test' # test Status collection (table)

data = {} # user data returned from database

# Verify the connection
try:
    connection = MongoClient(mongo_server_connection)
except Exception as e:
    print("database error: " + e)

# Update
db = connection[database]
db[collection].update_many({},{"$set":{"currentPalletTagFile": " ","palletTagFileUploadDateTime": "","palletTagFileUser": " ","palletTagFileDownloadCount": 0}})
db[collection].update_many({},{"$set":{"currentPalletWorksheetFile": " ","palletWorksheetFileUploadDateTime": "","palletWorksheetFileUser": " ","palletWorksheetFileDownloadCount": 0}})
db[collection].update_many({},{"$set":{"palletTagReplacementCount": 0, "palletWorksheetReplacementCount": 0}})
db[collection].update_many({},{"$set":{"postalAccountingNotes": ""}})
db[collection].update_many({},{"$set":{"sampleRoomNotes": ""}})

connection.close()
