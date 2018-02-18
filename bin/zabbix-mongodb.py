#!/usr/bin/env python
# Date: 03/01/2017
# Author: Long Chen
# Description: A script to get MongoDB metrics
# Requires: MongoClient in python

from pymongo import MongoClient
from calendar import timegm
from time import gmtime

class MongoDB(object):
    def __init__(self):
        self.mongo_host = "127.0.0.1"
        self.mongo_port = 27017
        self.mongo_db = ["admin", ]
        self.mongo_user = None
        self.mongo_password = None
        self.__conn = None
        self.__dbnames = None
        self.__metrics = []

    # Connect to MongoDB
    def connect(self):
        if self.__conn is None:
            if self.mongo_user is None:
                try:
                    self.__conn = MongoClient('mongodb://%s:%s' % (self.mongo_host, self.mongo_port))
                except Exception as e:
                    print ('Error in MongoDB connection: %s' % str(e))
            else:
                try:
                    self.__conn = MongoClient('mongodb://%s:%s@%s:%s' % (self.mongo_user, self.mongo_password, self.mongo_host, self.mongo_port))
                except Exception as e:
                    print ('Error in MongoDB connection: %s' % str(e))

    # Add each mectrics to the metrics list
    def addMetrics(self, k, v):
        dict = {}
        dict['key'] = k
        dict['value'] = v
        self.__metrics.append(dict)

    # Print out all metrics
    def printMetrics(self):
        metrics = self.__metrics
        for m in metrics:
            zabbix_item_key = str(m['key'])
            zabbix_item_value = str(m['value'])
            print ('- ' + zabbix_item_key + ' ' + zabbix_item_value)

    # Get a list of DB names
    def getDBNames(self):
        if self.__conn is None:
            self.connect()
        db = self.__conn[self.mongo_db[0]]

        master = db.command('isMaster')['ismaster']
        dict = {}
        dict['key'] = 'mongodb.ismaster'
        DBList = []
        if master:
            dict['value'] = 1
            DBNames = self.__conn.database_names()
            self.__dbnames = DBNames
        else:
            dict['value'] = 0
        self.__metrics.append(dict)

    # Print DB list in json format, to be used for mongo db discovery in zabbix
    def getMongoDBLLD(self):
        if self.__dbnames is None:
            DBNames = self.getDBNames()
        else:
            DBNames = self.__dbnames
        dictLLD = {}
        DBList = []
        dictLLD['key'] = 'mongodb.discovery'
        dictLLD['value'] = {"data": DBList}
        if DBNames is not None:
            for db in DBNames:
                dict = {}
                dict['{#MONGODBNAME}'] = db
                DBList.append(dict)
            dictLLD['value'] = {"data": DBList}
        self.__metrics.insert(0, dictLLD)

    def getOplog(self):
        if self.__conn is None:
            self.connect()
        db = self.__conn['local']

        coll = db.oplog.rs

        op_first = (coll.find().sort('$natural', 1).limit(1))
        op_last = (coll.find().sort('$natural', -1).limit(1))

        # if host is not a member of replica set, without this check we will raise StopIteration
        # as guided in http://api.mongodb.com/python/current/api/pymongo/cursor.html
        if op_first.count() > 0 and op_last.count() > 0:
            op_fst = (op_first.next())['ts'].time
            op_last_st = op_last[0]['ts']
            op_lst = (op_last.next())['ts'].time

            status = round(float(op_lst - op_fst), 1)
            self.addMetrics('mongodb.oplog', status)

            currentTime = timegm(gmtime())
            oplog = int(((str(op_last_st).split('('))[1].split(','))[0])
            self.addMetrics('mongodb.oplog-sync', (currentTime - oplog))


    def getMaintenance(self):
        if self.__conn is None:
            self.connect()
        db = self.__conn

        fsync_locked = int(db.is_locked)
	self.addMetrics('mongodb.fsync-locked', fsync_locked)

	try:
            config = db.admin.command("replSetGetConfig", 1)
            connstring = (self.mongo_host + ':' + str(self.mongo_port))

            for i in range(0, len(config['config']['members'])):
                if (connstring) in config['config']['members'][i]['host']:
                    priority = config['config']['members'][i]['priority']
                    hidden = int(config['config']['members'][i]['hidden'])

            self.addMetrics('mongodb.priority', priority)
            self.addMetrics('mongodb.hidden', hidden)
        except Exception:
            print ('Error while fetching replica set configuration. Not a member of replica set?')

    # Get Server Status
    def getServerStatusMetrics(self):
        if self.__conn is None:
            self.connect()
        db = self.__conn[self.mongo_db[0]]
        ss = db.command('serverStatus')

        # db info
        self.addMetrics('mongodb.version', ss['version'])
        self.addMetrics('mongodb.storageEngine', ss['storageEngine']['name'])
        self.addMetrics('mongodb.uptime', int(ss['uptime']))
        self.addMetrics('mongodb.okstatus', int(ss['ok']))

        # asserts
        for k, v in ss['asserts'].items():
            self.addMetrics('mongodb.asserts.' + k, v)

        # operations
        for k, v in ss['opcounters'].items():
            self.addMetrics('mongodb.operation.' + k, v)

        # memory
        for k in ['resident', 'virtual', 'mapped', 'mappedWithJournal']:
            self.addMetrics('mongodb.memory.' + k, ss['mem'][k])

        # connections
        for k, v in ss['connections'].items():
            self.addMetrics('mongodb.connection.' + k, v)

        # network
        for k, v in ss['network'].items():
            self.addMetrics('mongodb.network.' + k, v)

        # extra info
        self.addMetrics('mongodb.page.faults', ss['extra_info']['page_faults'])

        #wired tiger
        if ss['storageEngine']['name'] is 'wiredTiger':
            self.addMetrics('mongodb.used-cache', ss['wiredTiger']['cache']["bytes currently in the cache"])
            self.addMetrics('mongodb.total-cache', ss['wiredTiger']['cache']["maximum bytes configured"])
            self.addMetrics('mongodb.dirty-cache', ss['wiredTiger']['cache']["tracked dirty bytes in the cache"])

        # global lock
        lockTotalTime = ss['globalLock']['totalTime']
        self.addMetrics('mongodb.globalLock.totalTime', lockTotalTime)
        for k, v in ss['globalLock']['currentQueue'].items():
            self.addMetrics('mongodb.globalLock.currentQueue.' + k, v)
        for k, v in ss['globalLock']['activeClients'].items():
            self.addMetrics('mongodb.globalLock.activeClients.' + k, v)

    # Get DB stats for each DB
    def getDBStatsMetrics(self):
        if self.__conn is None:
            self.connect()
        if self.__dbnames is None:
            self.getDBNames()
        if self.__dbnames is not None:
            for mongo_db in self.__dbnames:
                db = self.__conn[mongo_db]
                dbs = db.command('dbstats')
                for k, v in dbs.items():
                    if k in ['storageSize','ok','avgObjSize','indexes','objects','collections','fileSize','numExtents','dataSize','indexSize','nsSizeMB']:
                        self.addMetrics('mongodb.stats.' + k + '[' + mongo_db + ']', int(v))
    # Close connection
    def close(self):
        if self.__conn is not None:
            self.__conn.close()

if __name__ == '__main__':
    MongoDB = MongoDB()
    MongoDB.getDBNames()
    MongoDB.getMongoDBLLD()
    MongoDB.getOplog()
    MongoDB.getMaintenance()
    MongoDB.getServerStatusMetrics()
    MongoDB.getDBStatsMetrics()
    MongoDB.printMetrics()
    MongoDB.close()
