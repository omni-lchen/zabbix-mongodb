#!/bin/bash

# Date:                 22/01/2017
# Author:               Long Chen
# Description:          A script to send MongoDB stats to zabbix server by using zabbix sender
# Requires:             Zabbix Sender, zabbix-mongodb.py

get_MongoDB_metrics(){
    python3 /etc/zabbix/zabbix-mongodb/bin/zabbix-mongodb.py
}

varA="$1 ~ /^info/ && match($1,/[0-9].*$/)"
varB="{sum+=substr($1,RSTART,RLENGTH)\} END \{print sum}"

# Send the results to zabbix server by using zabbix sender
result=$(get_MongoDB_metrics | /usr/bin/zabbix_sender -vv -c /etc/zabbix/zabbix_agentd.conf -i - 2>&1)
response=$(echo "$result" | awk -F ";" '$varA $varB')

if [ -n "$response" ]; then
        echo "$response"
else
        echo "$result"
fi
