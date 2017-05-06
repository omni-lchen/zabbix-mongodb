#!/usr/bin/env python

# Date: 03/01/2017
# Author: Long Chen
# Description: A script to get MongoDB metrics
# Requires: MongoClient in python

from pymongo import MongoClient
import json

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
            try:
                self.__conn = MongoClient(host=self.mongo_host, port=self.mongo_port)
            except Exception as e:
                print 'Error in MongoDB connection: %s' % str(e)

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
            print '- ' + zabbix_item_key + ' ' + zabbix_item_value

    # Get a list of DB names
    def getDBNames(self):
        if self.__conn is None:
            self.connect()
        db = self.__conn[self.mongo_db[0]]
        if self.mongo_user and self.mongo_password:
            db.authenticate(self.mongo_user, self.mongo_password)
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
        DBList = []
        if DBNames is not None:
            for db in DBNames:
                dict = {}
                dict['{#MONGODBNAME}'] = db
                DBList.append(dict)
        return {"data":DBList}

    # Get Server Status
    def getServerStatusMetrics(self):
        if self.__conn is None:
            self.connect()
        db = self.__conn[self.mongo_db[0]]
        if self.mongo_user and self.mongo_password:
            db.authenticate(self.mongo_user, self.mongo_password)
        ss = db.command('serverStatus')
        #print ss

        # db info
        self.addMetrics('mongodb.version', ss['version'])
        self.addMetrics('mongodb.storageEngine', ss['storageEngine']['name'])
        self.addMetrics('mongodb.uptime', int(ss['uptime']))
        self.addMetrics('mongodb.okstatus', int(ss['ok']))

        # asserts
        for k, v in ss['asserts'].items():
            self.addMetrics('mongodb.asserts.' + k, v)

        # background flushing
        self.addMetrics('mongodb.backgroundFlushing.flushes', ss['backgroundFlushing']['flushes'])
        self.addMetrics('mongodb.backgroundFlushing.total_ms', ss['backgroundFlushing']['total_ms'])

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
        self.addMetrics('mongodb.heap.size', ss['extra_info']['heap_usage_bytes'])
        self.addMetrics('mongodb.page.faults', ss['extra_info']['page_faults'])

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
                if self.mongo_user and self.mongo_password:
                    self.__conn[self.mongo_db[0]].authenticate(self.mongo_user, self.mongo_password)
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
    MongoDB_LLD = str(json.dumps(MongoDB.getMongoDBLLD()))
    print '- mongodb.discovery ' + MongoDB_LLD
    MongoDB.getServerStatusMetrics()
    MongoDB.getDBStatsMetrics()
    MongoDB.printMetrics()
    MongoDB.close()
