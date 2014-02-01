#!/usr/bin/env python

import urllib2
import json
import datetime
import time
from pprint import pprint
from pymongo import MongoClient

import dateutil.parser

# Traffic problem notification tool
#
# users have routes of interest (eg the daily school run)
# system takes a feed of traffic data
#   - congestion info
#   - roadworks
#
# system checks incoming traffic data against the users routes.
# Users are sent alerts if their routes ()are affected.
#  eg "There are roadworks on the school run
#    - best leave 10 minutes earlier today!", sent 1 hour before their
#    usual departure time.
#  eg "Send me an email at 7am on weekdays if my route is congested"
#

# Notes
#
# users input routes
#   via website, using interactive map, waypoints etc...
#   via on-handset app (collects lat/lon traces)
#
# Use OSM node ids as the common identifier.
#   - routes stored as OSM node ids
#   - incoming data/events related to OSM node ids
#
# detecting problems on a route:
# compare node ids
# maybe need some fuzz, depending on type of event...
# use lat/lon + fuzz radius
# Time is important. eg Congestion measures good for an hour or two...
#  roadwork data has set start/finish dates.
#
# User wants:
#  notification in advance of setting out, if route is slow/blocked whatever...
#
# ISSUES:
# osm nodeids can change as the map is edited.
#  idea: keep the route dat around in raw form (eg gps trace) around,
#  and do the raw->osm_id transformation again from time to time.

class N(object):
    """ OSM node. A point of interest - can just be id """
    def __init__(self,id,lat=None,lon=None,tags=None):
        self.id = id
        self.lat=lat
        self.long=long
        self.tags=tags

    def desc(self):
        """ a friendly human-readable description of this location """
        return describeNode(self.id)

class User(object):
    """ A user, watching a bunch of nodes

    Actually, we really want users and routes as separate things in the system,
    so a user can have multiple routes etc etc etc... but for now who cares?
    """
    
    def __init__(self, name,nodes):
        self.name = name
        # index by node id
        self.nodes = dict(zip([n.id for n in nodes], nodes))


    def __str__(self):
        return self.name + "["+",".join([str(n.id) for n in self.nodes.values()]) + "]";

    def checkum(self, incoming):
        notes = []
        now = datetime.datetime.now()
        for dat in incoming:
            node_id = dat['osm_id']
            # is the data relevant to this user?

            # one of the nodes we're interested in?
            if node_id not in self.nodes:
                continue    # nope

            # congested?
            if dat['avg_ds'] < 1.0:
                continue    # nope, intersection is clear

            # is the data fresh?
            if now - dat['updated_at'] > datetime.timedelta(hours=8):
                continue    # nope, too old

            node = self.nodes[node_id]
            notes.append("Congestion at %s" % (node.desc(),))
        return notes


def slurpDB():
    """ grab latest data from mongodb """
    data =  [doc for doc in db.traffic.find()]
    # parse the timestamps
    for d in data:
        d['updated_at'] = dateutil.parser.parse(d['updated_at'])
    return data


def slurp():
    #   with urllib2.urlopen("http://example.com/foo/bar") as resp:
    #       foo = resp.read()
    with open('test.json') as f:
        foo = f.read()
    data = json.loads(foo)

    # parse the timestamps
    for d in data:
        d['updated_at'] = dateutil.parser.parse(d['updated_at'])

    return data


def describeNode(node_id):
    """ return a nice human-readable description of a node """

    # perform clever lookup against OSM api:
    foo = {
        1: "Corner of First & Thingy",
        2: "Credability St Pedestrian crossing",
        3: "Intersection of 3rd and Main",
        4: "Intersection of Fourth and Forth"
    }
    if node_id in foo:
        return foo[node_id]
    return "Node%d St" % (node_id,)




alice = User("Alice", [N(id) for id in [1,2,3,4,5]])
bob = User("Bob", [N(id) for id in [4,5,6,7,8,9,10]])
users = [alice,bob]

conn = MongoClient()
db = conn['foooooooook']


def main():
    foo = slurp()
#    pprint( foo)

    for u in users:
#        print(u)
        notes = u.checkum(foo)
        if notes:
            print( "ALERT! " + u.name + ":")
            for n in notes:
                print("  " + n)

if __name__ == "__main__":
    main()


