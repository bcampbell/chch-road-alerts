from bson.json_util import loads
from pymongo import MongoClient
import json
from pprint import pprint

# load test.json into a mongodb, a simulation of Patrick's value-added
# traffic congestion data

DBNAME = "chchroads"
COLLECTION = "traffic"

conn= MongoClient()
db = conn[DBNAME]


with open("test.json") as f:
    raw = f.read()
data = json.loads(raw)


db[COLLECTION].remove()

for item in data:
    pprint(item)
    db[COLLECTION].insert(item)


#items.insert(loads(line))

