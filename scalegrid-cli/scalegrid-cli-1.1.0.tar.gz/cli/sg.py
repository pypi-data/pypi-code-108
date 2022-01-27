#!/usr/bin/env python3

"""
    \r
    ScaleGrid CLI v1.1.0
    GPL License: https://www.gnu.org/licenses/agpl-3.0.en.html

    ScaleGrid Help Menu

    Usage:
        sg-cli [mongo | redis | mysql | postgresql] <command> [<args>...]

    Options:
        -v, --verbose  Increase verbosity
        -h, --help     Show this menu
        -V --version   Show version

    Commands:

            login
            logout

        Cloud Profiles:
            (mongo | redis | mysql | postgresql) create-cloud-profile
            list-cloud-profiles
            update-cloud-profile-keys
            delete-cloud-profile

        Clusters:
            (mongo | redis | mysql | postgresql) create-cluster
            (mongo | redis | mysql | postgresql) get-available-db-versions
            (mongo | redis | mysql | postgresql) list-clusters
            (mongo | redis | mysql | postgresql) get-cluster-credentials
            (mongo | redis | mysql | postgresql) reset-credentials
            (mongo | redis | mysql | postgresql) pause-cluster
            (mongo | redis | mysql | postgresql) refresh-cluster
            (mongo | redis | mysql | postgresql) resume-cluster
            (mongo | redis | mysql | postgresql) delete-cluster

        Firewall:
            (mongo | redis | mysql | postgresql) set-firewall-rules
            (mongo | redis | mysql | postgresql) get-firewall-rules

        Maintenance:
            (mongo | redis | mysql | postgresql) scale-up
            (mongo | redis | mysql | postgresql) patch-os
            (mongo | redis | mysql | postgresql) upgrade-agent

        Backup/Restore:
            (mongo | redis | mysql | postgresql) set-backup-schedule
            (mongo | redis | mysql | postgresql) get-backup-schedule
            (mongo | redis | mysql | postgresql) list-backups
            (mongo | redis | mysql | postgresql) start-backup
            (mongo | redis | mysql | postgresql) delete-backup
            (mongo | redis | mysql | postgresql) restore-backup
            (mongo | redis | mysql | postgresql) peek-at-backup

        Follower:
            (mongo | redis | mysql | postgresql) setup-follower
            (mongo | redis | mysql | postgresql) sync-follower
            (mongo | redis | mysql | postgresql) get-follower-status
            (mongo | redis | mysql | postgresql) stop-following
            

        Alerts:
            (mongo | redis | mysql | postgresql) create-alert-rule
            (mongo | redis | mysql | postgresql) list-alert-rules
            (mongo | redis | mysql | postgresql) delete-alert-rule
            (mongo | redis | mysql | postgresql) get-active-alerts
            (mongo | redis | mysql | postgresql) resolve-alerts

        Database Actions:
            (mysql | postgresql) get-config
            (redis | mysql | postgresql) update-config
            (mongo | mysql | postgresql) build-index
            (mongo) compact
            (mysql) add-column
            (mysql) add-index
            (postgresql) set-pgbouncer
            (postgresql) get-pgbouncer-config
            (postgresql) modify-pgbouncer-config

        Job Status:
            check-job-status
            wait-until-job-done

    Help commands:
            sg-cli -h
            sg-cli <command> -h
            sg-cli [mongo | redis | mysql | postgresql] <command> -h
"""

import sys

if sys.version_info[0] < 3:
    sys.stderr.write("Python 3 required\n")
    sys.exit(1)

import logging
import traceback
import os
from os import path
from os import listdir
from os.path import isfile, join
import http.client, ssl, urllib
import json
from pathlib import Path
from time import sleep
from datetime import datetime
import getpass
from stat import *
import io
from docopt import docopt, DocoptExit
import configparser

# set environment variable SGServerIP from the command line to change SERVER_IP
# SERVER_IP will be 'console.scalegrid.io' by default (if environment variable not assigned)

VERSION = '1.1.0'

# lists containing all the keys to display for list functions (used with print_obj)
# "created" is converted from an integer to a datetime timestamp
# first.second --> indicates the value of key 'first' is a dictionary, and 'second' is a key within the dictionary
# list within the list (instead of normal strings) --> first item in the list is the key that points to a list of dictionaries
    # Each subsequent item in the list is a value in each dictionary within the list of dictionaries
CLUSTER_VALS_MONGO = ["name", "id", "clusterType", "anyMPShared", "status", "size", "diskSizeGB", "usedDiskSizeGB", "versionStr", "displayMachinePoolName",
                      ["monitoringServerData", "id", "name", "shardName", "type"], "encryptionEnabled", "sslEnabled", "engine", "compressionAlgo"]
CLUSTER_VALS_REDIS = ["name", "id", "clusterType", "clusterMode", "shared", "status", "size" , "versionStr", "ramGB", "usedRamGB", ["shards", "name",
                      ["redisServers", "VM-addressableName", "VM-vmHost-machinePool-providerMachinePoolName", "master", "slave", "sentinel"]], "encryptionEnabled"]
CLUSTER_VALS_MYSQL = ["name", "id", "clusterType", "shared", "status", "size" , "versionStr", "diskSizeGB", "usedDiskSizeGB", ["shards", "name",
                      ["mySQLServers", "VM-addressableName", "VM-vmHost-machinePool-providerMachinePoolName", "isArbiter", "isMaster", "isSlave"]],
                      "sslEnabled", "encryptionEnabled"]
CLUSTER_VALS_POSTGRESQL = ["name", "id", "clusterType", "shared", "status", "size" , "versionStr", "diskSizeGB", "usedDiskSizeGB", ["shards", "name",
                      ["postgreSQLServers", "VM-addressableName", "VM-vmHost-machinePool-providerMachinePoolName", "VM-status", "master", "standby", "arbiter", "readReplica"]],
                      "sslEnabled", "encryptionEnabled", "isPgBouncerEnabled", "pgBouncerParams"]
FOLLOWER_STATUS_VALS = [["destinationCluster", "name", "id", "status", "size", "clusterType", "diskSizeGB", "usedDiskSizeGB", "encryptionEnabled", "sslEnabled"], ["sourceCluster", "name", "id", "status", "size", "clusterType", "diskSizeGB", "usedDiskSizeGB", "encryptionEnabled", "sslEnabled"], ["syncSchedule", "intervalInHours", "jobType", "nextRuntime"]]
BACKUP_VALS = ["name", "id", "object_id", "created", "type", "comment"]
SCHEDULE_VALS = ["backupHour", "backupIntervalInHours", "backupScheduledBackupLimit", "backupTarget"]
STATUS_VALS = ["name", "object_name", "object_type", "cancelled", "progress", "status", "run_by"]
PROFILE_VALS = ["providerMachinePoolName", "configJSON.region", "configJSON.regionDesc", "id", "dbType", "type", "status", "shared"]
ALERT_VALS = ["alertDescription", "clusterID", "created", "dismissComment", "dismissedDate", "id", "machineName", "state", "userAlertRuleId"]
RULE_VALS = ["alertRuleDescription", "averageType", "clusterId", "created", "databaseType", "enabled", "id", "metric", "notifications", "operator",
             "ruleMetricName", "threshold", "type"]
CONF_VALS_SQL = ["param_name", "current_val", "unit", "valid_vals", "editable"]

conn = None
header = None

params = None

def get_filepath(fileName):
    __location__ = os.path.join(str(Path.home()), ".sg")
    if not os.path.isdir(__location__):
        os.mkdir(__location__)
    return os.path.join(__location__, fileName)

logging.basicConfig(
    format="%(asctime)s %(funcName)s():%(lineno)s %(levelname)s %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p %Z",
    level="DEBUG",
    filename=get_filepath('sg.log')
)
logger = logging.getLogger(__name__)

class SGException(Exception):
    message = None
    recAction = None

    def __init__(self, msg, recommendation=""):
        self.message = msg
        self.recAction = recommendation
        super(SGException, self).__init__()

    def getMessage(self):
        return self.message

    def getRecAction(self):
        return self.recAction

    def __str__(self):
        return self.message

def create_handler():
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter("%(levelname)s %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

def set_server_ip():
    global SERVER_IP, PORT
    if os.path.exists(get_filepath("sgconf.ini")):    
        config = configparser.ConfigParser()
        config.read(get_filepath("sgconf.ini"))
        config.sections()
        if 'CUSTOM' in config:
            SERVER_IP=config['CUSTOM']['SERVER_IP']
            PORT=config['CUSTOM']['PORT']
        else:
            SERVER_IP = "console.scalegrid.io"
            PORT = 443
    else:
        SERVER_IP = "console.scalegrid.io"
        PORT = 443
    
    

def display_error_message(error, action=""):
    sys.stderr.write("Something went wrong. " + error)
    sys.stderr.write("\n")
    if action != "":
        sys.stderr.write("Recommended action: " + action)
        sys.stderr.write("\n")
    traceback.print_exc(file=open(get_filepath('sg.log'), 'a'))

def check_resp(expected):
    r2 = conn.getresponse()
    if r2.status != expected:
        raise SGException("Unexpected HTTP response - " + str(r2.status))
    return r2

def append_to_cookie(snippet, cookie):
    e = snippet.split(";", 1)
    a = e[0].split("=", 1)
    if not a[1]:
        logger.debug("Value of cookie %s is empty, ignoring it", a[0])
        return cookie

    separator = "; "
    if not cookie:
        separator = ""
    return cookie + separator + e[0]

def connect():
    global conn
    set_server_ip()
    if SERVER_IP == "console.scalegrid.io":
        conn = http.client.HTTPSConnection(
            SERVER_IP, PORT
        )
    else:
        conn = http.client.HTTPSConnection(
            SERVER_IP, PORT, context=ssl._create_unverified_context()
        )
    conn.connect()

def load_header():
    global header
    cookieFile = get_filepath("sg_cookie.txt")
    logger.debug("Loading cookie info")
    try:
        with open(cookieFile, "r") as f:
            content = f.read()
    except FileNotFoundError as e:
        params['--email'] = None
        login()
        load_header()
        return
    header = {"Cookie": content, "User-Agent": "ScaleGridCLI/" + VERSION}

def get_resp(url, reqType, body={}):
    conn.request(reqType, url, body=json.dumps(body), headers=header)
    r2 = check_resp(200)
    resp = json.loads(r2.read())
    if resp["error"]["code"] != "Success" and resp["error"]["code"] != "PostgreSQLRestartWarning" and resp["error"]["code"] != "MySQLRestartWarning":
        raise SGException(resp["error"]["errorMessageWithDetails"], resp["error"]["recommendedAction"])

    return resp

def get_status(url, reqType, body={}):
    conn.request(reqType, url, body=json.dumps(body), headers=header)
    r2 = check_resp(200)
    try:
        resp = json.loads(r2.read())
        if resp["error"]["code"] != "Success":
            raise SGException(resp["error"]["errorMessageWithDetails"], resp["error"]["recommendedAction"])
    except ValueError:
        return

def print_obj_helper(obj, argv):
    newObj = {}
    if isinstance(obj, list):
        innerList = []
        for i in obj:
            innerList += [print_obj_helper(i, argv)]
        return innerList
    for arg in argv:
        if arg=='all':
            newObj = obj
            break
        if isinstance(arg, list):
            key = arg[0]
            subArgs = print_obj_helper(obj[key], arg)
            temp = {key: subArgs}
            arg = key
        else:
            if arg.lower()=="notifications":
                obj[arg] = eval(obj[arg])
            if arg.lower()=="providermachinepoolname":
                newObj["name"] = obj[arg]
                continue
            if arg.lower()=="type":
                if obj[arg]=="EC2":
                    newObj["cloudType"] = "AWS"
                else:
                    newObj["cloudType"] = obj[arg]
                continue
            if arg.lower()=="anympshared" or arg.lower()=="shared":
                if obj[arg]:
                    newObj["planType"] = "Dedicated"
                else:
                    newObj["planType"] = "BYOC"
                continue
            if arg.lower()=="created" or (arg.lower()=="dismisseddate" and obj[arg] != None):
                newObj[arg] = str(datetime.fromtimestamp(int(obj[arg])/1000.0))
                continue
            elif "." in arg:
                arg = arg.split(".")
                temp = json.loads(obj[arg[0]])
                arg = arg[1]
            elif "-" in arg:
                arg = arg.split("-")
                temp = obj
                for i in range(0, len(arg)-1):
                    temp = temp[arg[i]]
                arg = arg[len(arg)-1]
                if arg.lower()=="errormessagewithdetails":
                    newObj["message"] = temp[arg]
                    continue
                if arg.lower()=="providermachinepoolname":
                    newObj["cloudProfileName"] = temp[arg]
                    continue
            else:
                temp = obj
        try:
            newObj[arg] = temp[arg]
        except KeyError as e:
            pass
    return newObj

def print_obj(obj, argv):
    sys.stdout.write(json.dumps(print_obj_helper(obj, argv), indent=4, separators=(',', ': ')))
    sys.stdout.write("\n")

def print_action_id(resp):
    sys.stdout.write("Action ID: " + str(resp["actionID"]))
    sys.stdout.write("\nTo track whether your action has completed, run:\n  sg-cli wait-until-job-done --action-id %s" % str(resp["actionID"]))
    sys.stdout.write("\n")

def print_id(id, objType):
    sys.stdout.write("New %s ID: %s. Keep this ID and use it to perform commands on your %s once it is created.\n" % (objType, id, objType))
    sys.stdout.write("To get more information about your %s once it is created, run the list-%ss command.\n" % (objType, objType.replace(' ', '-')))

def delete_cookie():
    if os.path.isfile(get_filepath("sg_cookie.txt")):
        os.chmod(get_filepath("sg_cookie.txt"), S_IWUSR)
        os.remove(get_filepath("sg_cookie.txt"))

def convert_mongo():
    if params['db-type'].lower() == "mongo":
        params['db-type'] = "mongodb"

def login():
    """
    \r
    Login to your ScaleGrid account

    Usage:
        sg-cli login [options]

    Options:
        --email [<email-address>]               Email address associated with your account
        --controller-ip <controller's ip>       Default: 'console.scalegrid.io'
                                                  IP-Address for ScaleGrid's controller
        --controller-port <controller's port>   Default: 443
                                                  Port Number for ScaleGrid's controller
        -v, --verbose                           Increase verbosity
    """
    config = configparser.ConfigParser()
    config['DEFAULT'] = {'SERVER_IP': 'console.scalegrid.io', 'PORT': '443'}
    with open(get_filepath("sgconf.ini"), 'w') as configfile:
        config.write(configfile)
    if params['--controller-port'] == None:
            params['--controller-port'] = 443
    if params['--controller-ip'] != None:
       
        config['CUSTOM'] = {'SERVER_IP': params['--controller-ip'], 'PORT': params['--controller-port']}
        with open(get_filepath("sgconf.ini"), 'w') as configfile:
            config.write(configfile)
    connect()
    if not params['--email']:
        params['--email'] = input("Enter your email address: ")
    # getpass bypasses input-redirection and forces customer to enter the password at the terminal. This makes it impossible to use sg-cli login in a script. So we don't use getpass unless the stdin is a terminal.
    if sys.stdin.isatty():
        password = getpass.getpass()
    else:
        password = sys.stdin.readline().rstrip()

    body = {"username": params['--email'], "password": password}

    conn.request("POST", "/login", body=json.dumps(body))
    r2 = check_resp(200)

    loginResponse = json.loads(r2.read())
    if loginResponse["error"]["code"] == "TwoFactorAuthNeeded":
        auth = input("Enter your Two Factor Authentication code: ")
        body["inputCode"] = auth
        conn.request("POST", "/login", body=json.dumps(body))
        r2 = check_resp(200)
        loginResponse = json.loads(r2.read())

    if loginResponse["error"]["code"] != "Success":
        raise SGException(loginResponse["error"]["errorMessageWithDetails"], loginResponse["error"]["recommendedAction"])

    sys.stdout.write("{}")
    sys.stdout.write("\n")
    sys.stderr.write("\nConnection successful to %s:%s\n" % (SERVER_IP,PORT))
    delete_cookie()

    clientCookie = ""
    for hdr, value in r2.getheaders():
        if hdr.casefold() == "set-cookie":
            clientCookie = append_to_cookie(value, clientCookie)
    cookieFile = get_filepath("sg_cookie.txt")
    try:
        with open(cookieFile, "w") as f:
            f.write(clientCookie)
        os.chmod(cookieFile, 0o400)
    except Exception as e:
        raise SGException("There was an error writing to " + cookieFile, "Check permissions for the file")
    sys.stderr.write("Cookie created successfully\n")

    logger.debug("Cookie written to " + cookieFile)

def get_available_db_versions():
    """
    \r
    Get the available database versions

    Usage:
        sg-cli (mongo | redis | mysql | postgresql) get-available-db-versions --cloud-type <cloud-type>

    Options:
        --cloud-type <cloud-type>  Type of cloud
                                     AWS for AWS, AZURE for Azure, DO for DigitalOcean
        -v, --verbose              Increase verbosity
    """
    convert_mongo()
    if params['--cloud-type'].upper() == "AWS":
        cloudType = "EC2"
    elif params['--cloud-type'].upper() == "AZURE":
        cloudType = "AZUREARM"
    elif params['--cloud-type'].upper() == "DO":
        cloudType = "DIGITALOCEAN"
    else:
        sys.stdout.write("Invalid cloud type\n")
        sys.exit(1)
    resp = get_resp("/Clusters/getDatabaseActiveVersions?dbType=%s&cloudProvider=%s" % (params['db-type'].upper(), cloudType), "GET")
    versions = resp["versions"]
    for k,v in versions.items():
        sys.stdout.write("%s (%s)\n" % (k,v))

def create_cluster():
    """
    \r
    Create a Standalone Cluster or Replica Set

    Usage:
        sg-cli (mongo | redis | mysql | postgresql) create-cluster --cluster-name <unique-cluster-name> --shard-count <number-of-shards> --size <cluster-size> --version <version-number> --cloud-profile-list <list-of-profile-names> [options]

    Options:
    Required:
        --cluster-name <unique-cluster-name>                        Name of the cluster
        --shard-count <number-of-shards>                            Number of shards
                                                                      1 for standalone or ReplicaSet, more for Sharded
                                                                      Must be 3 or 4 for Redis when cluster-mode when is enabled
                                                                      Currently this is limited to 1 in case of PostgreSQL. Change ReplicaCount to deploy in HA mode.
        --size <cluster-size>                                       Size of the cluster
                                                                      Size options: micro, small, medium, large, xlarge, x2xlarge, or x4xlarge
        --version <version-number>                                  Version of database
                                                                    Available versions can be fetched by running the get-available-db-versions command
        --cloud-profile-list <list-of-cloud-profile-names>          List of comma separated cloud profile names
                                                                      Example: --cloud-profile-list "CloudProfile1,CloudProfile2,CloudProfile3"
                                                                      Number of names should match:
                                                                      number of replicas (number of replicas + 1, if even) times number of shards

    Common:
        --encrypt-disk                                              Include option to encrypt disk [default: false]
        --replica-count <nodes-per-shard>                           Number of nodes in each shard of your MongoDB/MySQL cluster
                                                                      1 for standalone, more for ReplicaSet or Sharded
                                                                      An even number will automatically add an Arbiter Instance for mongo
                                                                      and a Quorum instance for MyQSL and PostgreSQL
        --enable-ssl                                                Include option to enable SSL on your MongoDB/MySQL cluster [default: false]
        --cidr-list <list-of-CIDR-ranges>                           List of comma separated CIDR ranges to whitelist on your Redis/MySQL cluster
                                                                      Example: --cidr-list 10.20.0.0/16,10.30.0.0/20

    Database-Specific Options:
    MongoDB:
        --mongo-engine <storage-engine>                             Name of storage engine [default: wiredtiger]
                                                                      Engine options for Mongo: wiredtiger | mmapv1
        --compression-algo <algorithm>                              Compression algorithm for MongoDB. Include option to compress data on disk [default: no compression]
                                                                      Compression options: snappy | zlib | zstd
    Redis:
        --server-count <nodes-per-shard>                            Number of nodes in each shard of your cluster. 1 for standalone.
                                                                      For master/slave deployment, if this is an even number,
                                                                      ensure to set the sentinel-count as one higher than this.
        --sentinel-count <number-of-sentinels>                      Number of sentinel nodes in a master/slave deployment
                                                                      Should be one more than server count if it is even otherwise the same as server count
        --sentinel-cloud-profile-list <list-of-cloud-profile-names> List of comma separated cloud profiles where the sentinels must be created
                                                                      when sentinel count > server count
                                                                      Number of entries must be equal to (sentinel count - server count)
        --enable-cluster-mode                                       Include option to create a Redis cluster mode deployment [default: false]
        --interval <interval_in_hours>                              Use this field to set up a Backup Schedule for your Redis deployment
                                                                      to take a snapshot every 1-24 hours so your data is always accessible.
                                                                      0 to disable scheduled backups
        --maxmemory-policy <policy>                                 Eviction policy when Redis is used as a cache [default: noeviction]
                                                                      Eviction policy options: volatile-lru, allkeys-lru, volatile-lfu, allkeys-lfu, volatile-random,
                                                                      allkeys-random, volatile-ttl, noeviction
        --enable-rdb                                                Include option to enable regular RDB saves to disk for your Redis deployment
        --enable-aof                                                Enable AOF persistence for your Redis deployment
    MySQL:
        --mysql-engine <storage-engine>                             Name of storage engine [default: INNODB]
                                                                      Engine options for MySQL: INNODB
        --replica-config <option>                                   Type of replication: Semisync (semisynchronous) or Async (asynchronous) [default: 0]
                                                                      0 for standalone, 1 for Semisync and 2 for Async
    PostgerSQL:
        --replication-type <replication-type>                       Default: "ASYNC"
                                                                      Value can be "ASYNC" or "SYNC"
                                                                      The type of replication - asynchronous or synchronous. This parameter should be empty/null when creating a standalone cluster.
        --sync-commit-type <sync-commit-type>                       Default: "LOCAL"
                                                                      Value can be: "ON" null "LOCAL" "REMOTE_WRITE" "REMOTE_APPLY" "OFF"
                                                                      Specifies whether transaction commit will wait for WAL records to be written to disk before the command returns a 'success' indication to the client. 
                                                                      We do not recommend setting syncCommitType to OFF. This can cause loss of committed transactions in the event of a server crash.
        --enable-pgBouncer                                          Include option to enable connection-pooling via PgBouncer. Can also be changed after cluster-creation
        --pool-mode <pool-mode>                                     Default: "session"
                                                                      Value can be: "session" "transaction" "statement"
                                                                      This determines how soon connections return to the pool. Use only when pgBouncer is enabled.
        --pool-size <pool-size>                                     The maximum number of cached connections per pool (i.e. per user + database combination). Use only when pgBouncer is enabled.
        --max-client-connections <max-client-connections>           Default: 1000
                                                                      Maximum number of client connections (across all pools) that pgBouncer will allow. This can be higher than the max_connections set on PostgreSQL server. Use only when pgBouncer is enabled.
        --max-db-connections <max-db-connections>                   Default: 0
                                                                      Maximum number of connections to a single database that pgBouncer will allow (across pools). By default this is unlimited (i.e. value = 0). Use only when pgBouncer is enabled.
        --max-user-connections <max-user-connections>               Default: 0
                                                                      Maximum number of connections by a single user that pgBouncer will allow (across pools). By default this is unlimited (i.e. value = 0). Use only when pgBouncer is enabled.

    Generic Options:
        -v, --verbose                                               Increase verbosity
    Examples for Redis:
        For Standalone(1 Node):
            sg-cli redis create-cluster --cluster-name <your-cluster-name> --shard-count 1  --size <size> --version <redis-version>  --cloud-profile-list <your-cloud-profile>  --server-count 1 [options]
            sg-cli redis create-cluster --cluster-name <your-cluster-name> --shard-count 1  --size <size> --version <redis-version>  --cloud-profile-list <your-cloud-profile>  --server-count 1 --interval <backup-interval> --cidr-list <your-cidr-list> --encrypt-disk  --enable-ssl --maxmemory-policy <Eviction-policy> --enable-rdb --enable-aof
        For Master-Slave/Replica Set(2 Node + 3 Sentinel):
            sg-cli redis create-cluster --cluster-name <your-cluster-name> --shard-count 1 --server-count 2 --size <size> --version <redis-version> --cloud-profile-list "ProfileName1,ProfileName2" --sentinel-count 3 --sentinel-cloud-profile-list Sentinel-ProfileName [options]
            sg-cli redis create-cluster --cluster-name <your-cluster-name> --shard-count 1 --server-count 2 --size <size> --version <redis-version> --cloud-profile-list "ProfileName1,ProfileName2" --sentinel-count 3 --sentinel-cloud-profile-list Sentinel-ProfileName --interval <backup-interval> --cidr-list <your-cidr-list> --encrypt-disk  --enable-ssl --maxmemory-policy <Eviction-policy> --enable-rdb --enable-aof
        For Master-Slave/Replica Set(3 Node + 3 Sentinel)
            sg-cli redis create-cluster --cluster-name <your-cluster-name>  --shard-count 1 --server-count 3 --size <size> --version <redis-version> --cloud-profile-list "ProfileName1,ProfileName2,ProfileName3" --sentinel-count 3 [options]
            sg-cli redis create-cluster --cluster-name <your-cluster-name>  --shard-count 1 --server-count 3 --size <size> --version <redis-version> --cloud-profile-list "ProfileName1,ProfileName2,ProfileName3" --sentinel-count 3 --interval <backup-interval> --cidr-list <your-cidr-list> --encrypt-disk  --enable-ssl --maxmemory-policy <Eviction-policy> --enable-rdb --enable-aof
        For Cluster-Mode (k shards [k can be 3 or 4], n node cluster [n can be 1, 2 or 3])
            sg-cli redis create-cluster --enable-cluster-mode --cluster-name <your-cluster-name>  --shard-count k --server-count n --size <size> --version <redis-version> --cloud-profile-list "ProfileName1,ProfileName2,ProfileName3...ProfileName(n*k)" [options]
		
    Examples for Postgres:	
		For Standalone(1 Node):
			sg-cli postgresql create-cluster --cluster-name <your-cluster-name> --shard-count 1 --replica-count 1 --size <size> --version <Postgres-Version> --cloud-profile-list <your-cloud-profile> [options]
			sg-cli postgresql create-cluster --cluster-name <your-cluster-name> --shard-count 1 --replica-count 1 --size <size> --version <Postgres-Version> --cloud-profile-list <your-cloud-profile> --enable-pgBouncer  --pool-size <pool-size> [options]
		For Master-Slave:
			sg-cli postgresql create-cluster --cluster-name <your-cluster-name> --shard-count 1 --replica-count 2 --size <size> --version  <Postgres-Version> --cloud-profile-list "ProfileName1,ProfileName2,ProfileName3" --replication-type <replication-type>  --sync-commit-type <sync-commit-type> [Options]
			sg-cli postgresql create-cluster --cluster-name <your-cluster-name> --shard-count 1 --replica-count 2 --size <size> --version  <Postgres-Version> --cloud-profile-list "ProfileName1,ProfileName2,ProfileName3" --replication-type <replication-type>  --sync-commit-type <sync-commit-type> --enable-pgBouncer  --pool-size <pool-size> [options] 
			sg-cli postgresql create-cluster --cluster-name <your-cluster-name> --shard-count 1 --replica-count 2 --size <size> --version <Postgres-Version> --cloud-profile-list "ProfileName1,ProfileName2,ProfileName3" --replication-type <replication-type>  --sync-commit-type <sync-commit-type> --enable-pgBouncer --pool-mode statement --pool-size <pool-size> --max-client-connections <max-client-connections> --max-user-connections <max-user-connections> --max-db-connections <max-db-connections> --enable-ssl --encrypt-disk

    """

    machines = params['--cloud-profile-list'].split(',')
    machineIDs = []
    for i in machines:
        params['--cloud-profile-name'] = i
        machineIDs += [list_cloud_profiles()["id"]]

    if params['db-type'].lower() == "mongo":
        if params['--replica-count'] == None:
            sys.stderr.write("Required fields are missing.\nExample: sg-cli mongo create-cluster --cluster-name <unique-cluster-name> --shard-count <number-of-shards> --replica-count <nodes-per-shard> --size <cluster-size> --version <version-number> --cloud-profile-list <list-of-profile-names>\n")
            sys.exit(1)
        body = {"clusterName": params['--cluster-name'], "shardCount": int(params['--shard-count']), "replicaCount": int(params['--replica-count']),
                "size": params['--size'], "version": params['--version'].upper(), "machinePoolIDList": machineIDs, "enableAuth": True, "engine": params['--mongo-engine'],
                "enableSSL": params['--enable-ssl'], "encryptDisk": params['--encrypt-disk']}
        if params['--compression-algo'] != None:
            body['compressionAlgo'] = params['--compression-algo']
        resp = get_resp("/%sClusters/create" % params['db-type'], "POST",  body=body)

        sys.stdout.write("Cluster creation started successfully\n")
        print_id(resp["clusterID"], "cluster")
        print_action_id(resp)

    elif params['db-type'].lower() == "redis":
        if (params['--sentinel-count'] == None):
            params['--sentinel-count'] = 0
        if (params['--interval'] == None):
            params['--interval'] = 0
        if (params['--server-count'] == None):
            sys.stderr.write("Required fields are missing.\nPlease make sure you're entering a value in the server-count parameter.\n")
            sys.exit(1)
        if (params['--enable-cluster-mode'] == False) and (int(params['--sentinel-count']) != 3) and (int(params['--server-count']) > 1):
            sys.stderr.write("Sentinel count should be equal to 3 in case of Replica Set mode. \n")
            sys.exit(1)
        if ((int(params['--sentinel-count'])) > (int(params['--server-count']))) and (params['--sentinel-cloud-profile-list'] == None):
            sys.stderr.write("Sentinel cloud-profile list is required\n")
            sys.exit(1)
        
        body = {"clusterName": params['--cluster-name'], "version": params['--version'].upper(), "size": params['--size'], "serverCount": int(params['--server-count']),
                "shardCount": int(params['--shard-count']), "machinePoolIDList": machineIDs, "clusterMode": params['--enable-cluster-mode'],
                "backupIntervalInHours": int(params['--interval']), "encryptDisk": params['--encrypt-disk']}
        if params['--sentinel-count'] != None:
            body['sentinelCount'] = int(params['--sentinel-count'])
        if params['--cidr-list'] != None:
            body['cidrList'] = params['--cidr-list'].split(',')
        if params['--sentinel-cloud-profile-list'] != None:
            sentinelMachines = params['--sentinel-cloud-profile-list'].split(',')
            sentinelMachineIDs = []
            for i in sentinelMachines:
                params['--cloud-profile-name'] = i
                sentinelMachineIDs += [list_cloud_profiles()["id"]]
            body['sentinelMachinePool'] = sentinelMachineIDs

        myRedisConfigParams = {}
        if params['--enable-rdb'] == False:
            myRedisConfigParams['save'] = {"value": "", "split": 0}
        if params['--enable-rdb'] == True:
            myRedisConfigParams['save'] = {"value": "900 1 300 10 60 10000", "split": 0} 
        if params['--enable-aof'] == True:
            myRedisConfigParams['appendonly'] = {"value": "yes", "split": 0}
        if params['--enable-aof'] == False:
            myRedisConfigParams['appendonly'] = {"value": "no", "split": 0}
        if params['--maxmemory-policy'] == None:
            myRedisConfigParams['maxmemory-policy'] = {"value": "noeviction", "split": 0}
        if params['--maxmemory-policy'] != None:
            myRedisConfigParams['maxmemory-policy'] = {"value": params['--maxmemory-policy'], "split": 0}        
        body['redisConfigParams'] = myRedisConfigParams
        
        resp = get_resp("/%sClusters/create" % params['db-type'], "POST",  body=body)

        sys.stdout.write("Cluster creation started successfully\n")
        print_id(resp["clusterID"], "cluster")
        print_action_id(resp)

    elif params['db-type'].lower() == "mysql":
        if params['--replica-count'] == None:
            sys.stderr.write("Required fields are missing.\nExample: sg-cli mysql create-cluster --cluster-name <unique-cluster-name> --shard-count <number-of-shards> --replica-count <nodes-per-shard> --size <cluster-size> --version <version-number> --cloud-profile-list <list-of-profile-names>\n")
            sys.exit(1)
        body = {"clusterName": params['--cluster-name'], "shardCount": int(params['--shard-count']), "replicaCount": int(params['--replica-count']),
                "size": params['--size'], "version": params['--version'].lower(), "machinePoolIDList": machineIDs, "replicaConfig": int(params['--replica-config']),
                "enableAuth": True, "engine": params['--mysql-engine'], "enableSSL": params['--enable-ssl'], "encryptDisk": params['--encrypt-disk']}
        if params['--cidr-list'] != None:
            body['cidrList'] = params['--cidr-list'].split(',')
        resp = get_resp("/%sClusters/create" % params['db-type'], "POST",  body=body)

        sys.stdout.write("Cluster creation started successfully\n")
        print_id(resp["clusterID"], "cluster")
        print_action_id(resp)
    
    elif params['db-type'].lower() == "postgresql":
        if params['--replica-count'] == None:
            sys.stderr.write("Required fields are missing.\nExample: sg-cli postgresql create-cluster --cluster-name <unique-cluster-name> --shard-count <number-of-shards> --replica-count <nodes-per-shard> --size <cluster-size> --version <version-number> --cloud-profile-list <list-of-profile-names>\n")
            sys.exit(1)
        body = {"clusterName": params['--cluster-name'], "shardCount": int(params['--shard-count']), "replicaCount": int(params['--replica-count']),
                "size": params['--size'], "version": params['--version'], "machinePoolIDList": machineIDs,
                "enableAuth": True, "enableSSL": params['--enable-ssl'], "encryptDisk": params['--encrypt-disk'], "enablePgBouncer": params['--enable-pgBouncer']}
        
        if params['--replication-type'] == None:
            params['--replication-type'] = "ASYNC"
        if params['--sync-commit-type'] == None:
            params['--sync-commit-type'] = "LOCAL"
            
        if params['--cidr-list'] != None:
            body['cidrList'] = params['--cidr-list'].split(',')
            
        if int(params['--replica-count']) > 1:
            body['replicationType'] = params['--replication-type']
            if params['--replication-type'] == "ASYNC": 
                if params['--sync-commit-type'] == "LOCAL" or params['--sync-commit-type'] == "OFF":
                    body['syncCommitType'] = params['--sync-commit-type']
                else:
                    sys.stderr.write("If replicationType = ASYNC, syncCommitType can be either LOCAL or OFF\n")
                    sys.exit(1) 
            if params['--replication-type'] == "SYNC":
                if params['--sync-commit-type'] == "ON" or params['--sync-commit-type'] == "REMOTE_WRITE" or params['--sync-commit-type'] == "REMOTE_APPLY":
                    body['syncCommitType'] = params['--sync-commit-type']
                else:
                    sys.stderr.write("If replicationType = SYNC, syncCommitType can be either ON or REMOTE_WRITE or REMOTE_APPLY\n")
                    sys.exit(1)
            
                
        pgBouncerParams = {"settings":{"pool_mode":"transaction","pool_size":"50"}}
        if params['--enable-pgBouncer'] == True:
            if params['--pool-size'] != None:
                pgBouncerParams['settings']['pool_mode'] = params['--pool-mode']
                pgBouncerParams['settings']['pool_size'] = params['--pool-size']
                if params['--max-client-connections'] != None:
                    pgBouncerParams['settings']['max_client_connections'] = params['--max-client-connections']
                if params['--max-db-connections'] != None:
                    pgBouncerParams['settings']['max_db_connections'] = params['--max-db-connections']
                if params['--max-user-connections'] != None:
                    pgBouncerParams['settings']['max_user_connections'] = params['--max-user-connections']
                body['pgBouncerParams'] = pgBouncerParams
            else:
                sys.stderr.write("Required fields are missing.\nSince the pgBouncer is enabled, Please enter the pool-size you want. \n")
                sys.exit(1)
            
            
            
        resp = get_resp("/%sClusters/create" % params['db-type'], "POST",  body=body)

        sys.stdout.write("Cluster creation started successfully\n")
        print_id(resp["clusterID"], "cluster")
        print_action_id(resp)

    else:
        sys.stdout.write("Action not supported\n")

def delete_cluster():
    """
    \r
    Delete an old cluster

    Usage:
        sg-cli (mongo | redis | mysql | postgresql) delete-cluster --cluster-name <unique-cluster-name> [options]

    Options:
        --cluster-name <unique-cluster-name>  Name of a cluster
        -v, --verbose                         Increase verbosity
    """

    id = str(list_clusters(getID=True)["id"])
    call = "/%sClusters/%s" % (params['db-type'], id)
    resp = get_resp(call, "DELETE", body={"skipVMDeletion": False})

    sys.stdout.write("Cluster delete started successfully\n")
    print_action_id(resp)

def get_obj(objs, objName, objType="cluster"):
    if objType=="cloudProfile":
        obj = next((i for i in objs if i["providerMachinePoolName"].lower() == objName.lower()), None)
    else:
        obj = next((i for i in objs if i["name"].lower() == objName.lower()), None)
    if obj == None:
        if objType == "backup":
            message = "The specified %sCluster Backup with name %s was not found" % (params['db-type'], objName)
            rec = "Specify a valid %sCluster Backup name and retry the operation" % params['db-type']
        elif objType == "cloudProfile":
            message = "The specified Cloud Profile with name %s was not found" % objName
            rec = "Specify a valid Cloud Profile name and retry the operation"
        else:
            message = "The specified %sCluster with name %s was not found" % (params['db-type'], objName)
            rec = "Specify a valid %sCluster name and retry the operation" % params['db-type']
        raise SGException(message, rec)
    return obj

def list_clusters(getID=False):
    """
    \r
    Get a list of all your clusters of a specified database type

    Usage:
        sg-cli (mongo | redis | mysql | postgresql) list-clusters [options]

    Options:
        --cluster-name <unique-cluster-name>  Name of a cluster
        -v, --verbose                         Increase verbosity
    """    
    resp = get_resp("/%sClusters/list" % params['db-type'], "GET")
    clusters = resp["clusters"]
    if params['--cluster-name']:
        if getID == True:
           return get_obj(clusters, params['--cluster-name'])
        else:
            print_obj(get_obj(clusters, params['--cluster-name']), CLUSTER_VALS_POSTGRESQL)
    else:
        if len(clusters) == 0:
            sys.stdout.write("No %s clusters\n" % params['db-type'])
        for i in clusters:
            if params['db-type'].lower() == "mongo":
                print_obj(i, CLUSTER_VALS_MONGO)
            elif params['db-type'].lower() == "redis":
                print_obj(i, CLUSTER_VALS_REDIS)
            elif params['db-type'].lower() == "mysql":
                print_obj(i, CLUSTER_VALS_MYSQL)
            elif params['db-type'].lower() == "postgresql":
                print_obj(i, CLUSTER_VALS_POSTGRESQL)

               
def set_pgbouncer():
    """
    \r
    Enable or Disable connection pooling by PgBouncer on a PostgreSQL cluster

    Usage:
        sg-cli (postgresql) set-pgbouncer --cluster-name <unique-cluster-name> [options] 

    Options:
        --cluster-name <unique-cluster-name>                    Name of a cluster
        --pool-mode <pool-mode>                                 Default: "session"
                                                                  Value can be: "session" "transaction" "statement"
                                                                  This determines how soon connections return to the pool. Use only when pgBouncer is enabled.
        --pool-size <pool-size>                                 Default: 50
                                                                The maximum number of cached connections per pool (i.e. per user + database combination). Use only when pgBouncer is enabled.
        --max-client-connections <max-client-connections>       Default: 1000
                                                                  Maximum number of client connections (across all pools) that pgBouncer will allow. This can be higher than the max_connections set on PostgreSQL server. Use only when pgBouncer is enabled
        --max-db-connections <max-db-connections>               Default: 0
                                                                  Maximum number of connections to a single database that pgBouncer will allow (across pools). By default this is unlimited (i.e. value = 0). Use only when pgBouncer is enabled
        --max-user-connections <max-user-connections>           Default: 0
                                                                  Maximum number of connections by a single user that pgBouncer will allow (across pools). By default this is unlimited (i.e. value = 0). Use only when pgBouncer is enabled 
        --disable                                               Include this option to disable connection-pooling via PgBouncer
                                                                  To disable, only provide the cluster name along with this option
                                                                  To enable, provide pool-mode, pool-size with required arguments and exclude this option
        -v, --verbose                                           Increase verbosity
    """
    body = {"settings":{"pool_mode":"session","pool_size":"50"}}
    id = str(list_clusters(getID=True)["id"])
    if params['--disable'] == False:
        if params['--pool-size'] != None:
            body['settings']['pool_mode'] = params['--pool-mode']
            body['settings']['pool_size'] = params['--pool-size']
            if params['--max-client-connections'] != None:
                body['settings']['max_client_connections'] = params['--max-client-connections']
            if params['--max-db-connections'] != None:
                body['settings']['max_db_connections'] = params['--max-db-connections']
            if params['--max-user-connections'] != None:
                body['settings']['max_user_connections'] = params['--max-user-connections']
        else:
            sys.stderr.write("Required fields are missing.\nSince the pgBouncer is enabled, Please enter the pool-size you want. \n")
            sys.exit(1)
        call = "/%sClusters/%s/enablePgBouncer" % (params['db-type'], id)
        resp = get_resp(call, "POST",  body=body)
        sys.stdout.write("Enabling connnection pooling via PgBouncer..\n")
    else:
        call = "/%sClusters/%s/disablePgBouncer" % (params['db-type'], id)
        resp = get_resp(call, "DELETE")
        sys.stdout.write("Disabling Connnection pooling via PgBouncer..\n")
    print_action_id(resp)

def get_pgbouncer_config():
    """
    \r
    Use this action to get your current PgBouncer Configuration. Relevant only if PgBouncer is on.

    Usage:
        sg-cli (postgresql) get-pgbouncer-config --cluster-name <unique-cluster-name> [options] 

    Options:
        --cluster-name <unique-cluster-name>                    Name of a cluster
        -v, --verbose                                           Increase verbosity
    """
    id = str(list_clusters(getID=True)["id"])
    
    call = "/%sClusters/%s/getPgBouncerConfig" % (params['db-type'], id)
    resp = get_resp(call, "GET")
    result = {key:value for key,value in resp.items() if key == 'settings'}
    
    sys.stdout.write("The Current PgBouncer Config is:\n%s" % json.dumps(result, indent=4, separators=(',', ': ')))
    sys.stdout.write("\n")
    
def modify_pgbouncer_config():
    """
    \r
    Use this action to modify your current PgBouncer Configuration. Relevant only if PgBouncer is on.
    
    Usage:
        sg-cli (postgresql) modify-pgbouncer-config --cluster-name <unique-cluster-name> [options] 

    Options:
        --cluster-name <unique-cluster-name>                    Name of a cluster
        --pool-mode <pool-mode>                                 Default: "session"
                                                                  Value can be: "session" "transaction" "statement"
                                                                  This determines how soon connections return to the pool. Use only when pgBouncer is enabled.
        --pool-size <pool-size>                                 Default: 50
                                                                The maximum number of cached connections per pool (i.e. per user + database combination). Use only when pgBouncer is enabled.
        --max-client-connections <max-client-connections>       Default: 1000
                                                                  Maximum number of client connections (across all pools) that pgBouncer will allow. This can be higher than the max_connections set on PostgreSQL server. Use only when pgBouncer is enabled
        --max-db-connections <max-db-connections>               Default: 0
                                                                  Maximum number of connections to a single database that pgBouncer will allow (across pools). By default this is unlimited (i.e. value = 0). Use only when pgBouncer is enabled
        --max-user-connections <max-user-connections>           Default: 0
                                                                  Maximum number of connections by a single user that pgBouncer will allow (across pools). By default this is unlimited (i.e. value = 0). Use only when pgBouncer is enabled
        -v, --verbose                                           Increase verbosity
    """
    body = {"settings":{"pool_mode":"session","pool_size":"50"}}
    id = str(list_clusters(getID=True)["id"])
    if params['--pool-size'] != None:
        body['settings']['pool_mode'] = params['--pool-mode']
        body['settings']['pool_size'] = params['--pool-size']
        if params['--max-client-connections'] != None:
            body['settings']['max_client_connections'] = params['--max-client-connections']
        if params['--max-db-connections'] != None:
            body['settings']['max_db_connections'] = params['--max-db-connections']
        if params['--max-user-connections'] != None:
            body['settings']['max_user_connections'] = params['--max-user-connections']
    else:
        sys.stderr.write("Required fields are missing.\nSince the pgBouncer is enabled, Please enter the pool-size you want. \n")
        sys.exit(1)
    call = "/%sClusters/%s/editPgBouncerConfig" % (params['db-type'], id)
    resp = get_resp(call, "POST",  body=body)
    sys.stdout.write("Modifying PgBouncer Configuration..\n")
    print_action_id(resp)

def list_backups():
    """
    \r
    Get a list of backups of a specified cluster

    Usage:
        sg-cli (mongo | redis | mysql | postgresql) list-backups --cluster-name <unique-cluster-name> [options]

    Options:
        --cluster-name <unique-cluster-name>  Name of a cluster
        --backup-name <unique-backup-name>    Name of a backup of your cluster
        -v, --verbose                         Increase verbosity
    """

    id = str(list_clusters(getID=True)["id"])
    call = "/%sClusters/%s/listBackups" % (params['db-type'], id)
    resp = get_resp(call, "GET")
    backups = resp["backups"]
    if params['--backup-name']:
        return get_obj(backups, params['--backup-name'], "backup")
    else:
        if len(backups) == 0:
            sys.stdout.write("No %s backups for this cluster\n" % params['db-type'])
        for i in backups:
            print_obj(i, BACKUP_VALS)

def start_backup():
    """
    \r
    Create a backup of a cluster

    Usage:
        sg-cli (mongo | redis | mysql | postgresql) start-backup --cluster-name <unique-cluster-name> --backup-name <unique-backup-name> [options] [--primary | --secondary]

    Options:
        --cluster-name <unique-cluster-name>  Name of a cluster
        --backup-name <unique-backup-name>    Name of a backup of your cluster
        --comment <backup-description>        Comments associated with your backup
        [--primary | --secondary]             Virtual machine target of backup. Only for replica sets
                                                For Redis and MySQL replica sets, primary refers to master and secondary to slave
                                              default: --secondary
        -v, --verbose                         Increase verbosity
    """

    id = str(list_clusters(getID=True)["id"])
    body = {"backupName": params['--backup-name'], "comment": params['--comment'], "id": id}
    if params['db-type'].lower() == "mongo":
        if list_clusters(getID=True)["clusterType"].lower() == "replicaset":
            if params['--primary']:
                body["target"] = "PRIMARY"
            else:
                body["target"] = "SECONDARY"
        resp = get_resp("/%sClusters/backup" % params['db-type'], "POST", body)
    elif params['db-type'].lower() == "redis" or "mysql":
        if list_clusters(getID=True)["clusterType"].lower() == "replicaset":
            if params['--primary']:
                body["target"] = "MASTER"
            else:
                body["target"] = "SLAVE"
        resp = get_resp("/%sClusters/backup" % params['db-type'], "POST", body)

    sys.stdout.write("%s backup started successfully\n" % params['--cluster-name'])
    print_action_id(resp)

def peek_at_backup():
    """
    \r
    Create a new standalone cluster from a past backup

    Usage:
        sg-cli (mongo | redis | mysql | postgresql) peek-at-backup --source-cluster <source-cluster-name> --backup-name <unique-backup-name> --cluster-name <new-cluster-name> [options]

    Options:
        --source-cluster <source-cluster-name>   Name of the original/source cluster
        --backup-name <unique-backup-name>       Name of the backup you would like to peek at
        --cluster-name <new-cluster-name>        Name of new cluster to create from backup
        -v, --verbose                            Increase verbosity
    """
    
    peek_cluster_name=params['--cluster-name']
    params['--cluster-name']=params['--source-cluster']

    clusterID = str(list_clusters(getID=True)["id"])
    backupID = str(list_backups()["id"])

    body = {"destinationClusterName": peek_cluster_name, "backupID": backupID, "sourceClusterID": clusterID}
    resp = get_resp("/%sClusters/peekAtBackup" % params['db-type'], "POST", body)

    sys.stdout.write("Peek started successfully\n")
    print_action_id(resp)

def setup_follower():
    """
    \r
    Setup a follower relationship between two clusters

    Usage:
        sg-cli (mongo | redis | mysql | postgresql) setup-follower --target-cluster <target-cluster-name> --source-cluster <source-cluster-name> --start-hour <start-time> --interval <hours-between-sync> [options]

    Options:
        --target-cluster <target-cluster-name>  Name of follower cluster
        --source-cluster <source-cluster-name>  Name of cluster that will be followed
        --start-hour <start-time>               Hour on a 24 hour clock at which the first sync will start
                                                  All subsequent sync will occur every --interval hours
        --interval <hours-between-sync>         Number of hours between each sync with source cluster
        -v, --verbose                           Increase verbosity
    """

    # setting '--cluster-name' parameter to ensure the list_clusters call returns a cluster
    params['--cluster-name'] = params['--target-cluster']
    targetID = str(list_clusters(getID=True)["id"])
    params['--cluster-name'] = params['--source-cluster']
    sourceID = str(list_clusters(getID=True)["id"])
    convert_mongo()
    body = {'sourceClusterID': sourceID, 'dbType': params['db-type'].upper(), 'intervalInHours': params['--interval']}
    body['startTimeStr'] = datetime.now().replace(hour=int(params['--start-hour']), minute=0, second=0, microsecond=0).isoformat()

    resp = get_resp("/clusters/%s/createFollowerRelationship" % targetID, "POST", body=body)
    sys.stdout.write("Follower relationship between clusters %s and %s created successfully\n" % (params['--target-cluster'], params['--source-cluster']))

def get_follower_status():
    """
    \r
    Get the details of follower relationship of the target cluster.

    Usage:
        sg-cli (mongo | redis | mysql | postgresql) get-follower-status --target-cluster <target-cluster-name> [options]

    Options:
        --target-cluster <target-cluster-name>  Name of follower cluster
        -v, --verbose                           Increase verbosity
    """

    params['--cluster-name'] = params['--target-cluster']
    targetID = str(list_clusters(getID=True)["id"])

    convert_mongo()
    body = {'dbType': params['db-type'].upper()}

    resp = get_resp("/clusters/%s/getFollowerRelationshipInfo" % targetID, "POST", body=body)
    print_obj(resp,FOLLOWER_STATUS_VALS)

def sync_follower():
    """
    \r
    On-demand sync of the follower cluster

    Usage:
        sg-cli (mongo | redis | mysql | postgresql) sync-follower --target-cluster <target-cluster-name> [options]

    Options:
        --target-cluster <target-cluster-name>  Name of follower cluster
        -v, --verbose                           Increase verbosity
    """

    params['--cluster-name'] = params['--target-cluster']
    targetID = str(list_clusters(getID=True)["id"])

    convert_mongo()
    body = {'dbType': params['db-type'].upper()}

    resp = get_resp("/clusters/%s/syncFollowerClusterNow" % targetID, "POST", body=body)
    sys.stdout.write("Follower cluster sync started successfully\n")
    print_action_id(resp)

def stop_following():
    """
    \r
    Break the follower relationship between two clusters

    Usage:
        sg-cli (mongo | redis | mysql | postgresql) stop-following --target-cluster <target-cluster-name> [options]

    Options:
        --target-cluster <target-cluster-name>  Name of follower cluster
        -v, --verbose                        Increase verbosity
    """

    # setting '--cluster-name' parameter to ensure the list_clusters call returns a cluster
    params['--cluster-name'] = params['--target-cluster']
    targetID = str(list_clusters(getID=True)["id"])

    convert_mongo()
    body = {'dbType': params['db-type'].upper()}

    resp = get_resp("/clusters/%s/breakFollowerRelationship" % targetID, "POST", body=body)
    sys.stdout.write("Follower relationship broken successfully\n")

def set_backup_schedule():
    """
    \r
    Change the backup schedule of a cluster

    Usage:
        sg-cli (mongo | redis | mysql | postgresql) set-backup-schedule --cluster-name <unique-cluster-name> [options] [--primary | --secondary]

    Options:
        --cluster-name <unique-cluster-name>  Name of a cluster
        --interval <hours-between-backups>    Number of hours between scheduled backups
        --hour <start-time>                   Hour on a 24 hour clock at which the first backup will start
                                                All subsequent backups will occur every --interval hours
        --limit <max-scheduled-backups>       Maximum number of scheduled backups retained
        --disable                             Include this option to disable scheduled backups
                                                To disable, only provide the cluster name along with this option
                                                To enable, provide interval, hour and limit options with required arguments and exclude this option
        [--primary | --secondary]             Virtual machine target of backup. Only for replica sets
                                                For Redis and MySQL replica sets, primary refers to master and secondary to slave
                                                For PostgreSQL replica sets, primary refers to master and secondary to standby
                                                default: --secondary
        -v, --verbose                         Increase verbosity
    """
    id = str(list_clusters(getID=True)["id"])
    if params['--disable'] == False:
        body = {"backupIntervalInHours": params['--interval'], "backupHour": params['--hour'], "backupScheduledBackupLimit": params['--limit'], "id": id}
        body["scheduledBackupEnabled"] = True
        if params['db-type'].lower() == "mongo":
            if list_clusters(getID=True)["clusterType"].lower() == "replicaset":
                if params['--primary']:
                    body["target"] = "PRIMARY"
                else:
                    body["target"] = "SECONDARY"
            resp = get_resp("/%sClusters/setClusterBackupSchedule" % params['db-type'], "POST", body)
        elif params['db-type'].lower() == "postgresql":
            if list_clusters(getID=True)["clusterType"].lower() == "replicaset":
                if params['--primary']:
                    body["target"] = "MASTER"
                else:
                    body["target"] = "STANDBY"
            resp = get_resp("/%sClusters/setBackupSchedule" % params['db-type'], "POST", body)
        elif params['db-type'].lower() == "redis" or "mysql":
            if list_clusters(getID=True)["clusterType"].lower() == "replicaset":
                if params['--primary']:
                    body["target"] = "MASTER"
                else:
                    body["target"] = "SLAVE"
            resp = get_resp("/%sClusters/setBackupSchedule" % params['db-type'], "POST", body)
        sys.stdout.write("Backup schedule set successfully\n")
    else:
        if (params['--interval'] != None) or (params['--hour'] != None) or (params['--limit'] != None):
            sys.stderr.write("To disable backup, run the command as below.\nExample: sg-cli (mongo | redis | mysql | postgresql) set-backup-schedule --cluster-name <unique-cluster-name> --disabled\n")
            sys.exit(1)
        else:
            body = {"id": id}
            if params['db-type'].lower() == "mongo":
                resp = get_resp("/%sClusters/setClusterBackupSchedule" % params['db-type'], "POST", body)
            if params['db-type'].lower() == "redis" or "mysql" or "postgresql":
                resp = get_resp("/%sClusters/setBackupSchedule" % params['db-type'], "POST", body)
            sys.stdout.write("Scheduled backups disabled\n")

def get_backup_schedule():
    """
    \r
    Get the backup schedule of a cluster

    Usage:
        sg-cli (mongo | redis | mysql | postgresql) get-backup-schedule --cluster-name <unique-cluster-name> [options]

    Options:
        --cluster-name <unique-cluster-name>  Name of a cluster
        -v, --verbose                         Increase verbosity
    """

    id = str(list_clusters(getID=True)["id"])

    if params['db-type'].lower() == "mongo":
        call = "/%sClusters/%s/fetch" % (params['db-type'], id)
        resp = get_resp(call, "GET")
        cluster = resp["cluster"]
        result = {key:value for key,value in cluster.items() if key in ("backupHour", "backupIntervalInHours", "backupScheduledBackupLimit", "backupTarget")}
        sys.stdout.write(json.dumps(result, indent=4, separators=(',', ': ')))
        sys.stdout.write("\n")
    elif params['db-type'].lower() in ("redis","mysql"):
        call = "/%sClusters/%s/getBackupSchedule" % (params['db-type'], id)
        resp = get_resp(call, "POST")
        result = {key:value for key,value in resp.items() if key in ("backupHour", "backupIntervalInHours", "backupScheduledBackupLimit", "target")}
        sys.stdout.write(json.dumps(result, indent=4, separators=(',', ': ')))
        sys.stdout.write("\n")
    elif params['db-type'].lower() in ("postgresql"):
        call = "/%sClusters/%s/getBackupSchedule" % (params['db-type'], id)
        resp = get_resp(call, "GET")
        result = {key:value for key,value in resp.items() if key in ("backupHour", "backupIntervalInHours", "backupScheduledBackupLimit", "target")}
        sys.stdout.write(json.dumps(result, indent=4, separators=(',', ': ')))
        sys.stdout.write("\n")

def restore_backup():
    """
    \r
    Restore a backup

    Usage:
        sg-cli (mongo | redis | mysql | postgresql) restore-backup --cluster-name <unique-cluster-name> --backup-name <unique-backup-name> [options]

    Options:
        --cluster-name <unique-cluster-name>  Name of a cluster
        --backup-name <unique-backup-name>    Name of a backup of your cluster
        -v, --verbose                         Increase verbosity
    """

    clusterID = str(list_clusters(getID=True)["id"])
    backupID = str(list_backups()["id"])

    body = {"backupID": backupID, "clusterID": clusterID}
    resp = get_resp("/%sClusters/restore" % params['db-type'], "POST", body)

    sys.stdout.write("%s restore started successfully\n" % params['--backup-name'])
    print_action_id(resp)

def delete_backup():
    """
    \r
    Delete an old backup

    Usage:
        sg-cli (mongo | redis | mysql | postgresql) delete-backup --cluster-name <unique-cluster-name> --backup-name <unique-backup-name> [options]

    Options:
        --cluster-name <unique-cluster-name>  Cluster to delete the backup from
        --backup-name <unique-backup-name>    Name of the backup to delete
        --force                               Force backup to delete [default: false]
        -v, --verbose                         Increase verbosity
    """

    clusterID = str(list_clusters(getID=True)["id"])
    backupID = str(list_backups()["id"])

    body = {"clusterID": clusterID, "backupID": backupID, "force": params['--force']}
    resp = get_resp("/%sClusters/deleteBackup" % params['db-type'], "POST", body)

    sys.stdout.write("Backup Delete started successfully\n")
    print_action_id(resp)

def scale_up():
    """
    \r
    Increase the size of your cluster

    Usage:
        sg-cli (mongo | redis | mysql | postgresql) scale-up --cluster-name <unique-cluster-name> --size <new-size> [options]

    Options:
        --cluster-name <unique-cluster-name>  Name of a cluster
        --size <new-size>                     New size of the cluster
                                                Size options: small, medium, large, xlarge, x2xlarge, or x4xlarge
        -v, --verbose                         Increase verbosity
    """

    id = str(list_clusters(getID=True)["id"])
    body = {"id": id, "newSize": params['--size']}
    resp = get_resp("/%sClusters/scale" % params['db-type'], "POST", body)

    sys.stdout.write("Scale up started successfully\n")
    print_action_id(resp)

def upgrade_agent():
    """
    \r
    Update ScaleGrid agent on the cluster

    Usage:
        sg-cli (mongo | redis | mysql | postgresql) upgrade-agent --cluster-name <unique-cluster-name> [options]

    Options:
        --cluster-name <unique-cluster-name>  Name of a cluster
        -v, --verbose                         Increase verbosity
    """

    id = str(list_clusters(getID=True)["id"])

    convert_mongo()
    body = {"clusterID": id, "dbType": params['db-type'].upper()}
    resp = get_resp("/Clusters/upgradeAgent", "POST", body)
    sys.stdout.write("Upgrading Agent\n")
    print_action_id(resp)

def get_config():
    """
    \r
    Get all database parameter configurations for a MySQL or PostgreSQL cluster

    Usage:
        sg-cli (mysql | postgresql) get-config --cluster-name <unique-cluster-name> [options]

    Options:
        --cluster-name <unique-cluster-name>  Name of a cluster
        --editable-only                       List only config parameters that are editable by user.
        -v, --verbose                         Increase verbosity
    """

    id = str(list_clusters(getID=True)["id"])
    call = "/%sClusters/get%sConfigs?id=%s" % (params['db-type'], params['db-type'], id)
    resp = get_resp(call, "GET")
    if params['db-type'].lower() == "mysql": 
        configs=json.loads(resp["mySqlConfigs"])
    elif params['db-type'].lower() == "postgresql":
        configs=json.loads(resp["postgresqlConfigs"])
    for i in configs:
        if params['--editable-only'] and i['editable'] == True:
            print_obj(i, CONF_VALS_SQL)
        elif params['--editable-only'] and i['editable'] == False:
            continue
        else:
            print_obj(i, CONF_VALS_SQL)
    
def build_index():
    """
    \r
    Create an index for a collection in a database in your MongoDB, MySQL or PostgreSQL cluster

    Usage:
        sg-cli (mongo | mysql | postgresql) build-index --cluster-name <unique-cluster-name> --db-name <database-name> --coll-name <collection-name> --index <keys-and-options> [options]

    Options:
        --cluster-name <unique-cluster-name>  Name of a cluster
        --db-name <database-name              Name of your database
        --coll-name <collection-name>         Name of your collection
        --index <keys-and-options>            JSON formatted string containing a list of the index's keys and options
                                                Example: "[{'key': 1, 'key2': -1}, {'name': 'example', 'unique': false}]"
        -v, --verbose                         Increase verbosity
    """

    id = str(list_clusters(getID=True)["id"])
    call = "/%sClusters/%s/buildIndex" % (params['db-type'], id)

    body = {"dbName": params['--db-name'], "collName": params['--coll-name'], "index": params['--index']}
    resp = get_resp(call, "POST", body)

    sys.stdout.write("Index build started successfully\n")
    print_action_id(resp)

def patch_os():
    """
    \r
    Patch your OS with the most recent updates

    Usage:
        sg-cli (mongo | redis | mysql | postgresql) patch-os --cluster-name <unique-cluster-name> [options]

    Options:
        --cluster-name <unique-cluster-name>  Name of a cluster
        --full-patch                          Include to execute full patch [default: false]
        --skip-shard-routers                  Include to skip shard routers [default: false]
        -v, --verbose                         Increase verbosity
    """

    id = str(list_clusters(getID=True)["id"])
    convert_mongo()
    body = {"id": id, "dbType": params['db-type'].upper(), "fullPatch": params['--full-patch'], "skipShardRouters": params['--skip-shard-routers']}
    resp = get_resp("/clusters/patchos", "POST", body)

    sys.stdout.write("OS Patch started successfully\n")
    print_action_id(resp)

def check_job_status():
    """
    \r
    Check the status of a job that you started

    Usage:
        sg-cli check-job-status --action-id <your-action-id> [options]

    Options:
        --action-id <your-action-id>  Unique ID returned by an action you performed
        -v, --verbose                 Increase verbosity
    """

    resp = get_resp("/actions/%s" % params['--action-id'], "GET")
    return resp['action']

def wait_until_job_done():
    """
    \r
    Pause program until a job finishes

    Usage:
        sg-cli wait-until-job-done --action-id <your-action-id> [options]

    Options:
        --action-id <your-action-id>  Unique ID returned by an action you performed
        -v, --verbose                 Increase verbosity
    """

    sys.stdout.write("Waiting...\n")
    while check_job_status()['status'].lower() == "running":
        sleep(60)
    if check_job_status()['status'].lower() == "failed":
        sys.stderr.write("The Job Failed! Please contact ScaleGrid Support")
        sys.exit(1)
    sys.stdout.write("Done\n")

def update_config():
    """
    \r
    Update database parameter configuration for a Redis, MySQL or PostgreSQL cluster

    Usage:
        sg-cli (redis | mysql | postgresql) update-config --cluster-name <unique-cluster-name> [options]

    Options for Redis:
        --maxmemory-policy <policy>                                 Change Eviction policy when Redis is used as a cache 
                                                                      Eviction policy options: volatile-lru, allkeys-lru, volatile-lfu, allkeys-lfu, volatile-random,
                                                                      allkeys-random, volatile-ttl, noeviction
        --enable-rdb                                                To enable regular RDB saves to disk for your Redis deployment
        --enable-aof                                                To Enable AOF persistence for your Redis deployment
        --disable-rdb                                               To disable regular RDB saves to disk for your Redis deployment
        --disable-aof                                               To disable AOF persistence for your Redis deployment  
    
    Options for MySQL, PostgreSQL:
        --dry-run                                                   Use this flag for a dry run, to check if server restart is involved with cluster configuration change.
        --param-key-value <param1:value1,param2:value2,..>          List of configuration <parameter-name>:<parameter-value>
                                                                      Example: --param-key-value {"param1":"Value1","param2":"Value2",...}
        
    Options:
        --cluster-name <unique-cluster-name>                        Name of a cluster
        -v, --verbose                                               Increase verbosity 
    """   
    id = str(list_clusters(getID=True)["id"])
    body = {"clusterID": id}
    if params['db-type'].lower() == "redis":
        if params['--maxmemory-policy']==None and params['--enable-rdb']==False and params['--enable-aof']==False and params['--disable-rdb']==False and params['--disable-aof']==False:
            sys.stderr.write("Required fields are missing.\n"+'Example: sg-cli redis update-config --cluster-name <unique-cluster-name> [options]'+"\n")
            sys.exit(1)
        else:
            call = "/%sClusters/%s/get%sConfig" % (params['db-type'],id,params['db-type'])
            resp = get_resp(call, "GET") 
            body['redisConfigParams'] = resp['redisConfigMap']
            
            if params['--disable-rdb'] == True:
                body['redisConfigParams']['save'] = {"split": 0, "value": ""}
            if params['--enable-rdb'] == True: 
                body['redisConfigParams']['save'] = {"split": 0, "value": "900 1 300 10 60 10000"}
            if params['--disable-aof'] == True:
                body['redisConfigParams']['appendonly'] = {"split": 0, "value": "no"}
            if params['--enable-aof'] == True:
                body['redisConfigParams']['appendonly'] = {"split": 0, "value": "yes"}        
            if params['--maxmemory-policy'] != None: 
                body['redisConfigParams']['maxmemory-policy'] = {"split": 0, "value": params['--maxmemory-policy']}  
            
            call="/%sClusters/udpate%sConfig" % (params['db-type'],params['db-type'])
        

    elif params['db-type'].lower() == "postgresql" or params['db-type'].lower() == "mysql":
        if params['--param-key-value']==None:
            sys.stderr.write("Required fields are missing.\n"+'Example: sg-cli (mysql | postgresql) update-config --cluster-name <unique-cluster-name> --param-key-value {"param1":"value1","param2":"value2",..}'+"\n")
            sys.exit(1)                       
        else:
            Configs=[]
            paramList=params['--param-key-value'].split(',')
            for arg in paramList:
                Configs.append({
                    "current_val": str(arg.split(':')[1].strip()), 
                    "param_name": str(arg.split(':')[0].strip())
                })
            if params['db-type'].lower() == "postgresql":
                body['postgresqlConfigs'] = str(Configs)
                if params['--dry-run']:
                    body['examineOnly'] = True
                else:
                    body['examineOnly'] = False
            elif params['db-type'].lower() == "mysql":
                body = {"id": id}
                body['mySqlConfigs'] = str(Configs)
                if params['--dry-run']:
                    body['bExamine'] = True
                else:
                    body['bExamine'] = False
                
            call = "/%sClusters/%s/update%sConfigs" % (params['db-type'], id, params['db-type'])
            
    else:
    	sys.stderr.write("Feature unavailable in this release, please use the ScaleGrid console.")
    	sys.exit(1) 
        
    resp = get_resp(call, "POST", body=body)
    if params['--dry-run']:
        if resp["error"]["code"] == "%sRestartWarning" % params['db-type']:
            sys.stdout.write("\n" + resp["error"]["errorMessageWithDetails"] + "\nIf you wish to proceed, remove the '--dry-run' flag and run again.")
        if resp["error"]["code"].lower() == "success":
            sys.stdout.write("\n" + "The following configuration change does not require a server restart" + "\nRun again without the '--dry-run' flag.")
    else:
        sys.stdout.write("\nConfig Update in progress..\n")
        print_action_id(resp)
    
def get_cluster_credentials():
    """
    \r
    Get the username and password for the root database user

    Usage:
        sg-cli (mongo | redis | mysql | postgresql) get-cluster-credentials --cluster-name <unique-cluster-name> [options]

    Options:
        --cluster-name <unique-cluster-name>  Name of a cluster
        -v, --verbose                         Increase verbosity
    """

    id = str(list_clusters(getID=True)["id"])
    call = "/%sClusters/%s/getCredentials" % (params['db-type'], id)
    resp = get_resp(call, "GET")

    logger.debug("Fetching credentials")
    sys.stdout.write("Username: %s\n" % resp['user'])
    sys.stdout.write("Password: %s\n" % resp['password'])
    sys.stdout.write("\n")
    id = str(list_clusters(getID=True)["id"])
    
    call = "/%sClusters/%s/fetch" % (params['db-type'], id)
    resp = get_resp(call, "GET")
    #print(resp)
    logger.debug("Fetching credentials")
    string=resp['cluster']['connectionString']
    if params['db-type'] == "PostgreSQL":
        syntax=resp['cluster']['commandLineServer']
    else:
        syntax=resp['cluster']['commandLineString']
    sys.stdout.write("Connection Strings: \n")
    for i in string:
        print("For " + i['driver'] + ": " + i['conString'])
    sys.stdout.write("\n")   
    sys.stdout.write("Command Line Syntax: \n%s\n" % syntax)
    sys.stdout.write("\n")

def reset_credentials():
    """
    \r
    Reset Credentials for a cluster

    Usage:
        sg-cli (mongo | redis | mysql | postgresql) reset-credentials --cluster-name <unique-cluster-name> [options]

    Options:
        --cluster-name <unique-cluster-name>  Name of a cluster
        -v, --verbose                         Increase verbosity
    """

    id = str(list_clusters(getID=True)["id"])

    convert_mongo()
    #body = {"clusterID": id, "dbType": params['db-type'].upper()}
    call = "/%sClusters/%s/rotateSecrets" % (params['db-type'], id)
    resp = get_resp(call, "POST")
    sys.stdout.write("Credentials rotated successfully\n\n")
    print_action_id(resp)
    sys.stdout.write("\n")
    sleep(5)
    sys.stdout.write("To view the new login credentials run:\n   sg-cli postgresql get-cluster-credentials --cluster-name %s" % params['--cluster-name'])

def add_column():
    """
    \r
    Add new column to an existing table on your MySQL database

    Usage:
        sg-cli (mysql) add-column --cluster-name <unique-cluster-name> --db-name <database-name> --table-name <table-name> --column-name <column-name> --column-type <column-type>

    Options:
        --cluster-name <unique-cluster-name>    Name of a cluster
        --db-name <database-name>               Name of the database
        --table-name <table-name>               Name of the table
        --column-name <column-name>             Name of the new column to add
        --column-type <column-type>             Data type of the new column
                                                  Example: 'INT', 'VARCHAR(100)', 'DATE'
        -v, --verbose                           Increase verbosity
    """

    id = str(list_clusters(getID=True)["id"])
    call = "/%sClusters/%s/alterTable" % (params['db-type'], id)

    body = {"database": params['--db-name'], "table": params['--table-name'], "column_name": params['--column-name'],
            "column_data_type": params['--column-type'], "clusterID": id, "action":"ADD_COLUMN"}
    resp = get_resp(call, "POST", body)
    print('Add column job initialising\n', flush=True)

    stat = get_resp("/actions/%s" % resp["actionID"], "GET")
    if stat['action']['status'].lower() == "initiating" or stat['action']['status'].lower() == "running":
        sleep(30)
    stat = get_resp("/actions/%s" % resp["actionID"], "GET")
    if stat['action']['status'].lower() == "initiating" or stat['action']['status'].lower() == "running":
        print_action_id(resp)
    elif stat['action']['status'].lower() == "completed":
        sys.stdout.write("Column has been added successfully\n")
    else:
        raise SGException(stat["action"]["stepError"]["errorMessageWithDetails"], stat["action"]["stepError"]["recommendedAction"])

def add_index():
    """
    \r
    Add new index to an existing table on your MySQL database

    Usage:
        sg-cli (mysql) add-index --cluster-name <unique-cluster-name> --db-name <database-name> --table-name <table-name> --index-name <index-name> --columns-to-index <column-names>

    Options:
        --cluster-name <unique-cluster-name>    Name of a cluster
        --db-name <database-name>               Name of the database
        --table-name <table-name>               Name of the table
        --index-name <unique-index-name>        Name for the index, alphanumeric characters only
        --columns-to-index <column-names>       List of comma separated columns to index
                                                  Example: column1,column2
        -v, --verbose                           Increase verbosity
    """

    id = str(list_clusters(getID=True)["id"])
    call = "/%sClusters/%s/alterTable" % (params['db-type'], id)

    body = {"database": params['--db-name'], "table": params['--table-name'], "index_name": params['--index-name'],
            "column_names_for_index": params['--columns-to-index'].split(','), "clusterID": id, "action":"ADD_INDEX"}
    resp = get_resp(call, "POST", body)
    print('Add index job initialising...\n', flush=True)

    stat = get_resp("/actions/%s" % resp["actionID"], "GET")
    if stat['action']['status'].lower() == "initiating" or stat['action']['status'].lower() == "running":
        sleep(30)
    stat = get_resp("/actions/%s" % resp["actionID"], "GET")
    if stat['action']['status'].lower() == "initiating" or stat['action']['status'].lower() == "running":
        print_action_id(resp)
    elif stat['action']['status'].lower() == "completed":
        sys.stdout.write("Index has been added successfully\n")
    else:
        raise SGException(stat["action"]["stepError"]["errorMessageWithDetails"], stat["action"]["stepError"]["recommendedAction"])

def compact():
    """
    \r
    Defragment the data in your MonogDB cluster to improve performance

    Usage:
        sg-cli (mongo) compact --cluster-name <unique-cluster-name> [options]

    Options:
        --cluster-name <unique-cluster-name>  Name of a cluster
        -v, --verbose                         Increase verbosity
    """

    id = str(list_clusters(getID=True)["id"])
    call = "/%sClusters/%s/compactDatabase" % (params['db-type'], id)
    resp = get_resp(call, "POST")

    sys.stdout.write("Compact started successfully\n")
    print_action_id(resp)

def pause_cluster():
    """
    \r
    Pause a cluster

    Usage:
        sg-cli (mongo | redis | mysql | postgresql) pause-cluster --cluster-name <unique-cluster-name> [options]

    Options:
        --cluster-name <unique-cluster-name>  Name of a cluster
        -v, --verbose                         Increase verbosity
    """

    id = str(list_clusters(getID=True)["id"])

    convert_mongo()
    body = {"clusterID": id, "dbType": params['db-type'].upper()}
    resp = get_resp("/clusters/pauseCluster", "POST", body)
    sys.stdout.write("Pause started successfully\n")
    print_action_id(resp)

def refresh_cluster():
    """
    \r
    Refresh a cluster

    Usage:
        sg-cli (mongo | redis | mysql | postgresql) refresh-cluster --cluster-name <unique-cluster-name> [options]

    Options:
        --cluster-name <unique-cluster-name>  Name of a cluster
        -v, --verbose                         Increase verbosity
    """

    id = str(list_clusters(getID=True)["id"])

    convert_mongo()
    #body = {"clusterID": id, "dbType": params['db-type'].upper()}
    call = "/%sClusters/%s/refresh" % (params['db-type'], id)
    resp = get_resp(call, "GET")
    sys.stdout.write("Refresh started successfully\n")
    print_action_id(resp)

def resume_cluster():
    """
    \r
    Resume a cluster

    Usage:
        sg-cli (mongo | redis | mysql | postgresql) resume-cluster --cluster-name <unique-cluster-name> [options]

    Options:
        --cluster-name <unique-cluster-name>  Name of a cluster
        -v, --verbose                         Increase verbosity
    """

    id = str(list_clusters(getID=True)["id"])

    convert_mongo()
    body = {"clusterID": id, "dbType": params['db-type'].upper()}
    resp = get_resp("/clusters/resumeCluster", "POST", body)
    sys.stdout.write("Resume started successfully\n")
    print_action_id(resp)

def set_firewall_rules():
    """
    \r
    Add a list of IP CIDR to the firewall rules of your cluster

    Usage:
        sg-cli (mongo | redis | mysql | postgresql) set-firewall-rules --cluster-name <unique-cluster-name> --cidr-list <list-of-CIDR-ranges> [options]

    Options:
        --cluster-name <unique-cluster-name>  Name of a cluster
        --cidr-list <list-of-CIDR-ranges>     List of comma separated CIDR ranges to whitelist
                                                Example: --cidr-list 10.20.0.0/16,10.30.0.0/20
        -v, --verbose                         Increase verbosity
    """

    id = str(list_clusters(getID=True)["id"])

    convert_mongo()
    body = {'clusterID': id, 'dbType': params['db-type'].upper(), 'cidrList': params['--cidr-list'].split(',')}

    get_status("/Clusters/setClusterLevelIPWhiteList", "POST", body)
    get_resp("/Clusters/configureIPWhiteList", "POST", body)
    sys.stdout.write("Firewall rules set successfully\n")

def get_firewall_rules():
    """
    \r
    Get the list of IP CIDR whitelisted from your cluster

    Usage:
        sg-cli (mongo | redis | mysql | postgresql) get-firewall-rules --cluster-name <unique-cluster-name>

    Options:
        --cluster-name <unique-cluster-name>  Name of a cluster
        -v, --verbose                         Increase verbosity
    """

    id = str(list_clusters(getID=True)["id"])
    
    convert_mongo()
    body = {'clusterID': id, 'dbType': params['db-type'].upper()}
    conn.request("POST", "/Clusters/getClusterLevelIPWhiteList", body=json.dumps(body), headers=header)
    r2 = check_resp(200)
    resp = json.loads(r2.read())
    logger.debug("Fetching whitelisted CIDR list")
    result = {key:value for key,value in resp.items() if key == 'cidrList'}
    sys.stdout.write(json.dumps(result, indent=4, separators=(',', ': ')))
    sys.stdout.write("\n")

def get_active_alerts():
    """
    \r
    Get all active alerts on a particular cluster

    Usage:
        sg-cli (mongo | redis | mysql | postgresql) get-active-alerts --cluster-name <unique-cluster-name>

    Options:
        --cluster-name <unique-cluster-name>  Name of a cluster
        -v, --verbose                         Increase verbosity
    """

    id = str(list_clusters(getID=True)["id"])

    convert_mongo()
    body = {'clusterId': id, 'databaseType': params['db-type'].upper()}
    resp = get_resp("/alerts", "POST", body=body)

    alerts = resp["alerts"]
    if len(alerts) == 0:
        sys.stdout.write("No active alerts\n")
    for i in alerts:
        print_obj(i, ALERT_VALS)
        logger.debug("Alert ID: %s" % i["id"])

def resolve_alerts():
    """
    \r
    Dismiss alerts for a particular cluster

    Usage:
        sg-cli (mongo | redis | mysql | postgresql) resolve-alerts --cluster-name <unique-cluster-name> --alert-id-list <list-of-alert-ids> [options]

    Options:
        --cluster-name <unique-cluster-name>  Name of a cluster
        --alert-id-list <list-of-alert-ids>   List of alert IDs to dismiss
                                                Example: --alert-id-list 12345,23456,34567
                                                Get alert IDs from the get-active-alerts command
        -v, --verbose                         Increase verbosity
    """

    id = str(list_clusters(getID=True)["id"])

    convert_mongo()
    body = {'clusterId': id, 'databaseType': params['db-type'].upper(), 'alertsList': params['--alert-id-list'].split(',')}
    resp = get_resp("/dismiss", "POST", body=body)

    sys.stdout.write("Alerts resolved successfully\n")

def create_alert_rule():
    """
    \r
    Create an alert rule for a particular cluster

    Usage:
        sg-cli (mongo | redis | mysql | postgresql) create-alert-rule --cluster-name <unique-cluster-name> --type <alert-rule-type> --operator <operator> --threshold <threshold> --notifications <notification-types> [options]

    Options:
        --cluster-name <unique-cluster-name>  Name of a cluster
        --type <alert-rule-type>              Type of alert rules
                                                Type options: METRIC, DISK_FREE, ROLE_CHANGE
        --operator <operator>                 Operator options: EQ, LT, GT, LTE, GTE
                                                EQ: equal to, LT: less than, GT: greater than, LTE: less than or equal to, GTE: greater than or equal to
        --threshold <threshold>               Decimal number that is paired with operator to create condition
                                                Example: --operator GT --threshold 10.0
                                                    = greater than 10.0
        --notifications <notification-types>  List of notification types
                                                Notification options: EMAIL, SMS, PAGERDUTY
                                                Example: --notification-types EMAIL,SMS
        --metric <metric>                     The metric for which the alert rule needs to be set
                                                For more information, refer the below links
                                                MongoDB - https://help.scalegrid.io/docs/mongodb-alerts-rules-create-cluster-level-rule
                                                Redis - https://help.scalegrid.io/docs/redis-alerts-rules-create-cluster-level-rule
                                                PostgreSQL - https://help.scalegrid.io/docs/postgresql-alerts-rules-create-cluster-level-rule
                                                Only include --metric if --type is METRIC
        --duration <duration-of-condition>    Duration of time the condition must be true before an alert is triggered
                                                Duration options: TWO, SIX, HOURLY, DAILY
                                                TWO: 2 minutes, SIX: 6 minutes, HOURLY: 1 hour, DAILY: 1 day
                                                Duration mandatory for certain alert rule types
        -v, --verbose                         Increase verbosity
    """

    id = str(list_clusters(getID=True)["id"])
    convert_mongo()

    params['--notifications']=params['--notifications'].upper()

    body = {'clusterId': id, 'databaseType': params['db-type'].upper(), 'alertRuleType': params['--type'].upper(),
            'operator': params['--operator'].upper(), 'threshold': params['--threshold'],
            'notifications': params['--notifications'].split(',')}
    if params['--metric'] != None:
        body['metric'] = params['--metric'].upper()
    if params['--duration'] != None:
        body['averageType'] = params['--duration'].upper()

    resp = get_resp("/AlertRules/create", "POST", body=body)

    rule = resp["rule"]
    print_obj(rule, RULE_VALS)
    sys.stdout.write("Alert rule created successfully\n")
    sys.stdout.write("Alert Rule ID: %s\n" % rule["id"])

def list_alert_rules():
    """
    \r
    List all the alert rules for a particular cluster

    Usage:
        sg-cli (mongo | redis | mysql | postgresql) list-alert-rules --cluster-name <unique-cluster-name> [options]

    Options:
        --cluster-name <unique-cluster-name>  Name of a cluster
        -v, --verbose                         Increase verbosity
    """

    id = str(list_clusters(getID=True)["id"])
    convert_mongo()
    resp = get_resp("/AlertRules/list", "POST", body={'clusterId': id, 'databaseType': params['db-type'].upper()})

    rules = resp["rules"]
    if len(rules) == 0:
        sys.stdout.write("No rules for this cluster\n")
    for i in rules:
        print_obj(i, RULE_VALS)

def delete_alert_rule():
    """
    \r
    Delete an alert rule from a particular cluster

    Usage:
        sg-cli delete-alert-rule --alert-rule-id <id-of-alert-rule> [options]

    Options:
        --alert-rule-id <id-of-alert-rule>  Alert rule ID
                                              Get ID from list-alert-rules command
        --force-delete                      Include to force the rule to delete [default: false]
        -v, --verbose                       Increase verbosity
    """

    resp = get_resp("/AlertRules/%s" % params['--alert-rule-id'], "DELETE", body={'forceDelete': params['--force-delete']})
    sys.stdout.write("Alert rule deleted successfully\n")

def list_cloud_profiles():
    """
    \r
    Get a list of all your cloud profiles

    Usage:
        sg-cli list-cloud-profiles [options]

    Options:
        --cloud-profile-name <unique-name-of-cloud-profile>  Unique name of a cloud profile
        -v, --verbose                                        Increase verbosity
    """

    resp = get_resp("/clouds/list", "GET")
    clouds = resp["clouds"]

    if params['--cloud-profile-name']:
        return get_obj(clouds, params['--cloud-profile-name'], "cloudProfile")
    else:
        if len(clouds) == 0:
            sys.stdout.write("No cloud profiles\n")
        for i in clouds:
            print_obj(i, PROFILE_VALS)

def create_script(resp):
    sys.stdout.write("Download and run either the PowerShell/CLI script to grant ScaleGrid the required permissions. This script creates a new ScaleGrid resource group and grants ScaleGrid permissions to it. The azure user to run this script requires account admin and global AD admin permissions.\n")
    scriptType = None
    while scriptType != 'azure' and scriptType != 'powershell':
        scriptType = input("Type 'azure' to download the Azure CLI script. Type 'powershell' to download the PowerShell script: ").lower()
    if scriptType == 'azure':
        scriptName = "grant-sg-permissions.sh"
        scriptContent = resp['bashPermissionsScript']
    else:
        scriptName = "grant-sg-permissions.ps1"
        scriptContent = resp['permissionsScript']
    scriptFile = get_filepath(scriptName)
    try:
        with open(scriptFile, "w") as f:
            f.write(scriptContent)
    except Exception as e:
        raise SGException("There was an error writing to " + scriptFile, "Check permissions for the file")
    sys.stdout.write("Run the script located at %s called %s\n" % (get_filepath(''), scriptName))

def create_cloud_profile():
    """
    \r
    Create a cloud profile. For more details, refer https://help.scalegrid.io/docs/what-is-a-cloud-profile

    Usage:
        sg-cli (mongo | redis | mysql | postgresql) create-cloud-profile --aws --cloud-profile-name <unique-name-of-cloud-profile> --region <region> --access-key <access-key> --secret-key <secret-key> --vpc-id <vpc-id> --subnet-id <subnet-id> --vpc-cidr <vpc-cidr> --subnet-cidr <subnet-cidr> --security-group-name <security-group-name> --security-group-id <security-group-id> [--connectivity-config <config> --enable-ssh] [-v | --verbose]
        sg-cli (mongo | redis | mysql | postgresql) create-cloud-profile --azure --cloud-profile-name <unique-name-of-cloud-profile> --region <region> --subscription-id <subscription-id> --subnet-name <subnet-name> --vnet-name <vnet-name> --vnet-resource-group <vnet-resource-group> --security-group-name <security-group-name> [--is-public] [--use-single-tennant-sp] [-v | --verbose]

    Options:
        --aws                                                Include to create AWS cloud profile
        --azure                                              Include to create Azure cloud profile
        --cloud-profile-name <unique-name-of-cloud-profile>  Unique name of a cloud profile
        --region <region>                                    AWS or Azure region [Avoid Putting Hyphens. Ex: uswest2]
        --access-key <access-key>                            AWS account access key
        --secret-key <secret-key>                            AWS account secret key
        --vpc-id <vpc-id>                                    AWS VPC ID
        --subnet-id <subnet-id>                              AWS VPC subnet ID
        --vpc-cidr <vpc-cidr>                                AWS VPC CIDR
        --subnet-cidr <subnet-cidr>                          AWS VPC Subnet CIDR
        --security-group-name <security-group-name>          AWS or Azure security group name
        --security-group-id <security-group-id>              AWS VPC security group id
        --connectivity-config <config>                       AWS connectivity configuration [default: INTERNET]
                                                               Configuration options: INTERNET, INTRANET, SECURITYGROUP, CUSTOMIPRANGE
        --enable-ssh                                         Include to enable SSH for AWS VPC
        --subscription-id <subscription-id>                  Azure subscription id
        --subnet-name <subnet-name>                          Azure subnet name
        --vnet-name <vnet-name>                              Azure vnet name
        --vnet-resource-group <vnet-resource-group>          Azure vnet resource group name
        --is-public                                          Include to provide a static public IP for your cloud profile
        --use-single-tennant-sp                              Include to use single tennant service principal
        -v, --verbose                                        Increase verbosity
    """

    convert_mongo()
    if params['--aws']:
        body = {'accessKey': params['--access-key'], 'secretKey': params['--secret-key'], 'database': params['db-type'].upper(),
                'region': params['--region'].lower(), 'deploymentStyle': 'VPC', 'connectivityConfig': params['--connectivity-config'],
                'name': params['--cloud-profile-name'], 'vpcID': params['--vpc-id'], 'vpcSubnetID': params['--subnet-id'],
                'vpcCIDR': params['--vpc-cidr'], 'vpcSubnetCIDR': params['--subnet-cidr'], 'vpcSecurityGroupID': params['--security-group-id'],
                'vpcSecurityGroup': params['--security-group-name'], 'dbType': params['db-type'].upper(), 'enableSSH': params['--enable-ssh']}
        call = "/clouds/createMachinePoolForEC2"
    else:
        body = {'name': params['--cloud-profile-name'], 'region': params['--region'], 'subscriptionID': params['--subscription-id'],
                'dbType': params['db-type'].upper(), 'azureTenantId': None, 'subnetName': params['--subnet-name'], 'isPublic': params['--is-public'],
                'vnetName': params['--vnet-name'], 'vnetResourceGroup': params['--vnet-resource-group'], 'securityGroupName': params['--security-group-name'],
                'resourceGroupName': "ScaleGrid-%s" % params['--cloud-profile-name'], 'useSingleTennantSP': params['--use-single-tennant-sp'], 'enablePremiumStorage': False}
        resp = get_resp("/Clouds/generateScriptForAzureARMCloudProfile", "POST", body=body)

        create_script(resp)
        input("Press enter once the script has been executed...")

        body.pop('azureTenantId')
        body.pop('enablePremiumStorage')
        call = "/clouds/createMachinePoolForAzureARM"

    resp = get_resp(call, "POST", body=body)
    print_id(resp["machinePoolID"], "cloud profile")
    print_action_id(resp)

def update_cloud_profile_keys():
    """
    \r
    Update Keys in AWS Cloud Profile

    Usage:
        sg-cli update-cloud-profile-keys --cloud-profile-name <unique-name-of-cloud-profile> --access-key <new-access-key> --secret-key <new-secret-key> [options]

    Options:
        --cloud-profile-name <unique-name-of-cloud-profile>  Unique name of a cloud profile
        --access-key <new-access-key>                        New AWS access key to update in cloud profile
        --secret-key <new-secret-key>                        New AWS secret key to update in cloud profile
        -v, --verbose                                        Increase verbosity
    """

    id = list_cloud_profiles()["id"]
    body = {'machinePoolID': id, 'accessKey': params['--access-key'], 'secretKey': params['--secret-key']}
    resp = get_resp("/Clouds/updateEC2MachinePoolKeys", "POST", body=body)
    sys.stdout.write("AWS cloud profile keys updated successfully\n")

def delete_cloud_profile():
    """
    \r
    Delete a cloud profile

    Usage:
        sg-cli delete-cloud-profile --cloud-profile-name <unique-name-of-cloud-profile> [options]

    Options:
        --cloud-profile-name <unique-name-of-cloud-profile>  Unique name of a cloud profile
        -v, --verbose                                        Increase verbosity
    """

    id = str(list_cloud_profiles()["id"])
    call = "/clouds/%s" % id
    resp = get_resp(call, "DELETE")

    sys.stdout.write("Cloud profile delete started successfully\n")
    print_action_id(resp)

def mongo_h():
    """
    \r
    MongoDB Help Menu

    Usage:
        sg-cli mongo <command> [<args>...]

    Options:
        -v, --verbose  Increase verbosity
        -h, --help     Show this menu
        -V --version   Show version

    Commands:
        set-firewall-rules
        get-firewall-rules
        build-index
        compact
        create-alert-rule
        create-cloud-profile
        create-cluster
        create-follower-cluster
        delete-backup
        delete-cluster
        get-active-alerts
        get-cluster-credentials
        list-alert-rules
        list-backups
        list-cloud-profiles
        list-clusters
        patch-os
        pause-cluster
        peek-at-backup
        resolve-alerts
        restore-backup
        resume-cluster
        scale-up
        set-backup-schedule
        start-backup

    Use sg-cli mongo <command> -h to open the help menu for the command.
    """

def redis_h():
    """
    \r
    Redis Help Menu

    Usage:
        sg-cli redis <command> [<args>...]

    Options:
        -v, --verbose  Increase verbosity
        -h, --help     Show this menu
        -V --version   Show version

    Commands:
        create-cloud-profile
        get-available-db-versions
        list-clusters
        create-cluster
        update-cluster-config
        reset-credentials
        pause-cluster
        resume-cluster
        refresh-cluster
        delete-cluster
        set-firewall-rules
        get-firewall-rules
        get-cluster-credentials
        scale-up
        patch-os
        upgrade-agent
        list-backups
        get-backup-schedule
        set-backup-schedule
        peek-at-backup
        restore-backup
        start-backup
        delete-backup
        create-alert-rule
        list-alert-rules
        delete-alert-rule
        get-active-alerts
        resolve-alerts
    
    Use sg-cli redis <command> -h to open the help menu for the command.
    """

def mysql_h():
    """
    \r
    MySQL Help Menu

    Usage:
        sg-cli mysql <command> [<args>...]

    Options:
        -v, --verbose  Increase verbosity
        -h, --help     Show this menu
        -V --version   Show version

    Commands:
        mysql commands
    """

def postgresql_h():
    """
    \r
    PostgreSQL Help Menu

    Usage:
        sg-cli postgresql <command> [<args>...]

    Options:
        -v, --verbose  Increase verbosity
        -h, --help     Show this menu
        -V --version   Show version

    Commands:
        create-cloud-profile
        get-available-db-versions
        list-clusters
        create-cluster
        reset-credentials
        pause-cluster
        resume-cluster
        refresh-cluster
        delete-cluster
        set-firewall-rules
        get-firewall-rules
        get-cluster-credentials
        scale-up
        patch-os
        upgrade-agent
        list-backups
        get-backup-schedule
        set-backup-schedule
        peek-at-backup
        restore-backup
        start-backup
        delete-backup
        create-alert-rule
        list-alert-rules
        delete-alert-rule
        get-active-alerts
        resolve-alerts
        setup-follower
        sync-follower
        get-follower-status
        stop-following
        set-pgbouncer
        get-pgbouncer-config
        modify-pgbouncer-config
    """

def logout():
    """
    \r
    Logout of your ScaleGrid account

    Usage:
        sg-cli logout [options]

    Options:
        -v, --verbose            Increase verbosity
    """
    connect()
    conn.request("GET", "/logout")
    check_resp(302)

    logger.debug("Removing cookie")
    delete_cookie()
    sys.stdout.write("{}")
    sys.stdout.write("\n")
    sys.stderr.write("Cookie removed, logging out...\n")

def get_db_type(args):
    if args['mongo']:
        return 'Mongo'
    elif args['redis']:
        return 'Redis'
    elif args['mysql']:
        return 'MySQL'
    elif args['postgresql']:
        return "PostgreSQL"
    return None

def get_argv(args, command, dbType):
    if command != 'login' and command != 'logout' and dbType != None:
        return [dbType.lower()] + [args['<command>']] + args['<args>']
    else:
        return [args['<command>']] + args['<args>']

def mod_command(command, dbType):
    command = command.replace('-','_')
    if command == "__help" or command == "_h":
        command = dbType.lower() + "_h"
    return command

def create_params(command, dbType, argv):
    global params
    try:
        try:
            params = docopt(eval(command).__doc__, argv=argv)
        except DocoptExit:
            sys.stderr.write(eval(command).__doc__)
            sys.exit(1)
    except Exception as e:
        raise SGException("Error evaluating arguments. Command %s was not found" % command, "Check parameters and try again")
    try:
        params['db-type'] = dbType
    except AttributeError as e:
        pass

def mod_size():
    global params
    try:
        params['--size'] = params['--size'].lower()
        if not (params['--size'].lower() == 'micro' or params['--size'].lower() == 'small' or params['--size'].lower() == 'medium' or params['--size'].lower() == 'large' or params['--size'].lower() == 'xlarge' or params['--size'].lower() == 'x2xlarge' or params['--size'].lower() == 'x4xlarge'):
            raise SGException("Invalid size for cluster", "--size must have argument small, medium, large, xlarge, x2xlarge, or x4xlarge, not %s" % params['--size'])
        params['--size'] = params['--size'].replace('xl', 'XL')
        params['--size'] = params['--size'][0].upper() + params['--size'][1:]
    except KeyError as e:
        pass

def execute_command(command):
    if command != 'login' and command != 'logout':
        connect()
        load_header()
    return eval(command)()

def print_returned(command, returned):
    objType = command.split('_')[len(command.split('_'))-1]
    if objType.lower() == "status":
        print_obj(returned, eval(objType[:len(objType)].upper() + "_VALS"))
    else:
        print_obj(returned, eval(objType[:len(objType)-1].upper() + "_VALS"))

def main():
    global params
    set_server_ip()
    create_handler()
    try:
        try:
            args = docopt(__doc__, version=("ScaleGrid CLI " + VERSION), options_first=True)
        except DocoptExit:
            sys.stderr.write(__doc__.rstrip())
            sys.exit(1)

        command = args['<command>'].lower()
        dbType = get_db_type(args)

        argv = get_argv(args, command, dbType)
        if '-v' in set(argv) or '--verbose' in set(argv):
            logger.setLevel('DEBUG')

        command = mod_command(command, dbType)
        create_params(command, dbType, argv)
        mod_size()

        returned = execute_command(command)
        if returned != None:
            print_returned(command, returned)
    except Exception as e:
        try:
            display_error_message(e.getMessage(), e.getRecAction())
        except Exception as e:
            display_error_message("Internal error")
        sys.exit(1)

if __name__ == '__main__':
    main()