# Zabbix-MongoDB
A Zabbix plugin for monitoring MongoDB.

# Installation
1. Import the mongodb template to zabbix and link it to the zabbix mongodb host.
2. cd /etc/zabbix && git clone https://github.com/denisgolius/zabbix-mongodb && cd zabbix-mongodb .
3. Copy mongodb zabbix agent configuration to /etc/zabbix-agent/zabbix_agentd.d and restart zabbix agent.

Note:
- Zabbix sender uses zabbix agent configuration to send the metrics, please check the hostname is set in the zabbix agent config /etc/zabbix/zabbix_agentd.conf, by default the hostname may be commented out.
Note:
- For using python3 you need to isntall some packages:

```sudo apt-get install build-essential python-dev python3-pip```
```sudo pip3 install pymongo```

- If your zabbix server was isntalled from official repository by apt, yum, dnf, rpm - just install zabbix_get, for ubuntu/debian run:

```sudo apt-get install zabbix-sender -y ```

or you can download package for your distro from http://repo.zabbix.com and install it by dpkg
for example in Ubuntu/Debian

```wget http://repo.zabbix.com/zabbix/4.0/ubuntu/pool/main/z/zabbix/zabbix-sender_4.0.8-1%2Bbionic_amd64.deb && dpkg -i zabbix-sender_4.0.8-1+bionic_amd64.deb ```

**Server Stats**
- mongodb.ismaster
- mongodb.version
- mongodb.storageEngine
- mongodb.uptime
- mongodb.okstatus
- mongodb.asserts.msg
- mongodb.asserts.rollovers
- mongodb.asserts.regular
- mongodb.asserts.warning
- mongodb.asserts.user
- mongodb.backgroundFlushing.flushes
- mongodb.backgroundFlushing.total_ms
- mongodb.operation.getmore
- mongodb.operation.insert
- mongodb.operation.update
- mongodb.operation.command
- mongodb.operation.query
- mongodb.operation.delete
- mongodb.memory.resident
- mongodb.memory.virtual
- mongodb.memory.mapped
- mongodb.memory.mappedWithJournal
- mongodb.connection.current
- mongodb.connection.available
- mongodb.connection.totalCreated
- mongodb.network.numRequests
- mongodb.network.bytesOut
- mongodb.network.bytesIn
- mongodb.heap.size
- mongodb.page.faults
- mongodb.globalLock.totalTime
- mongodb.globalLock.currentQueue.total
- mongodb.globalLock.currentQueue.writers
- mongodb.globalLock.currentQueue.readers
- mongodb.globalLock.activeClients.total
- mongodb.globalLock.activeClients.writers
- mongodb.globalLock.activeClients.readers

**DB Stats**
- mongodb.stats.storageSize[db]
- mongodb.stats.ok[db]
- mongodb.stats.avgObjSize[db]
- mongodb.stats.indexes[db]
- mongodb.stats.objects[db]
- mongodb.stats.collections[db]
- mongodb.stats.fileSize[db]
- mongodb.stats.numExtents[db]
- mongodb.stats.dataSize[db]
- mongodb.stats.indexSize[db]
- mongodb.stats.nsSizeMB[db]

# License
[MIT](/LICENSE.md)
