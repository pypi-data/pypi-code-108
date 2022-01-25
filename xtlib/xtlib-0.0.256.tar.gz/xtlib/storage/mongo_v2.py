#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
#
# mongo_v2.py: new XT API for talking to mongo about RUN and JOB data

# NOTE: storage v2 is not currently supported (quicktest is broken; implementation is incomplete)
import os
from re import sub
import uuid
import arrow
import json
import time
import numpy as np
import pymongo
import collections
from pymongo import MongoClient
from interface import implements

from xtlib import utils
from xtlib import errors
from xtlib import console
from xtlib import constants
from xtlib import job_helper
from xtlib import run_helper
from xtlib import report_builder
from xtlib.storage.db_interface import DbInterface

DEFAULT_DB = "__default__"
MONGO_INFO = "__mongo_info__"
WORKSPACES = "__workspaces__"

class MongoDB2(implements(DbInterface)):
    '''
    XT mongoDB format v2:
        - STORAGE hierarchy: storage-service/workspace/job/run/child-run
            - job names are allocated names within a workspace
            - run names share the job name: "run47.0" is first child run of job47)

        - DB hierarchy: mongo-service/database/workspace/collections
            - each workspace can be its own mongoDB database, or part of the DB_DEFAULT database
            
            - each workspace consists of:
                - 5 run collections
                    - run_info          (write once, _id: ws/run_name)
                    - run_stats         (high update, _id: ws/run_name)
                    - hparams           (write once, _id: ws/run_name)
                    - metrics           (high update, _id: ws/run_name)
                    - log_records       (write once, _id: GUID)

                - 5 job collections:
                    - job_info          (write once, _id: ws/job_name)
                    - job_stats         (high update, _id: ws/job_name)
                    - child_runs        (medium update, _id: ws/job_name/run_index, key: ws/job_name/node_index)
                    - connect_info      (write once, _id: ws/job_name/node_index)
                    - service_info_by_node      (write once, _id: ws/job_name)

            - workspace-independent collections (always in DB_DEFAULT database):
                - __mongo_info__   (contains mongo format info and paired storage name, "_id": 1)
                - __workspaces__   (record for each workspace, _id: ws_name)

            - each of the above collections is shared (for Cosmos DB versions):
                - shard key is always the _id (unique to each document of the collection)
                - whenever possible, we use a predictable _id (since updates must specify the shard key)
    '''
    
    def __init__(self, mongo_cs, db_name=None, ws_name=None, run_cache_dir=None, 
        direct_mode=True, store=None, db_options=None):

        '''
        direct_mode: means we update data in mongo directly (from XT or the run) (vs. storge tracking)
        '''
        if not db_name:
            db_name = DEFAULT_DB

        self.direct_mode = direct_mode
        self.is_cosmos = not "localhost" in mongo_cs
        self.db_name = db_name
        self.call_stats = {}
        self.retry_errors = 0
        self.mongo_conn_str = mongo_cs
        self.round_trip_count = 0         # stats for last query
        self.name = "mongo_v2"
        self.store = store
        self.last_metrics_write = time.time()
        self.metrics = {}

        # mongo options for stats and logging
        self.update_job_stats = True
        self.update_run_stats = True
        self.add_log_records = True
        self.buffer_metrics = 0
        self.max_retries = 25
        self.max_backoff = 180

        if db_options:
            self.set_mongo_options(db_options)

        self.mongo_client = MongoClient(mongo_cs)

        self.ws_name = ws_name
        if ws_name:
            db_name = self.create_workspace_if_needed(ws_name, db_name)

        # update database for workspace
        self.mongo_db = self.mongo_client[db_name]    

        self.run_cache_dir = os.path.expanduser(run_cache_dir) if run_cache_dir else None

        self.avail_row_count = None

    #---- UTILS ----

    # API call
    def get_db_type(self):
        return "mongo_v2"

    def set_mongo_options(self, md):
        self.update_job_stats = md["update-job-stats"]
        self.update_run_stats = md["update-run-stats"]
        self.add_log_records = md["add-log-records"]
        self.buffer_metrics = md["buffer-metrics"]
        self.max_retries = md["max-retries"]
        self.max_backoff = md["max-backoff"]

    def get_service_name(self):
        _, rest = self.mongo_conn_str.split("//", 1)
        if ":" in rest:
            name, _ = rest.split(":", 1)
        else:
            name, _ = rest.split("/", 1)
        return name

    def get_db(self, ws_name=None, db_name=None):
        if not db_name:
            assert bool(ws_name)

            if self.ws_name == ws_name:
                db_name = self.db_name
            else:
                # look it up for the ws_name
                records = self.get_workspace_infos({"_id": ws_name})
                if not records:
                    errors.service_error("workspace not found: {}".format(ws_name))

                db_name = utils.safe_cursor_value(records, "db_name")
                if not db_name:
                    db_name = DEFAULT_DB
                    
                self.db_name = db_name
                self.ws_name = ws_name

        return self.mongo_client[db_name]

    def get_db_info(self):
        dbx = self.get_db(db_name=DEFAULT_DB)

        records = self.mongo_with_retries("get_db_info", dbx, \
            lambda: dbx[MONGO_INFO].find({"_id": 1}, None), return_records=True)
        record = records[0] if records and len(records) else None
        return record

    def set_db_info(self, db_info): 
        dbx = self.get_db(db_name=DEFAULT_DB)

        self.mongo_with_retries("set_mongo_info", dbx, \
            lambda: dbx[MONGO_INFO].update( {"_id": 1}, db_info, upsert=True) )

    def delete_workspace_if_needed(self, ws_name):
        '''
        delete:
           1. entries for specified workspace from our 10 run/job collections
           2. __workspaces__ entry for workspace
        '''

        # this line will raise an exception if the ws_name is not known to mongo
        exists = bool(self.get_workspace_infos({"_id": ws_name}))
        if exists:
            dbx = self.get_db(ws_name)

            # delete RUN collections
            self.delete_from_collection(dbx, ws_name, "run_info", "_id")
            self.delete_from_collection(dbx, ws_name, "hparams", "_id")
            self.delete_from_collection(dbx, ws_name, "metrics", "_id")
            self.delete_from_collection(dbx, ws_name, "log_records", "_id")
            self.delete_from_collection(dbx, ws_name, "run_stats", "_id")

            # delete JOB collections
            self.delete_from_collection(dbx, ws_name, "job_info", "_id")
            self.delete_from_collection(dbx, ws_name, "job_stats", "_id")
            self.delete_from_collection(dbx, ws_name, "connect_info", "_id")
            self.delete_from_collection(dbx, ws_name, "service_info_by_node", "_id")
            self.delete_from_collection(dbx, ws_name, "child_runs", "key")

            dbx_default = self.get_db(db_name=DEFAULT_DB)
            self.mongo_with_retries("delete_workspace_if_needed", dbx, \
                lambda: dbx_default[WORKSPACES].delete_one( {"_id": ws_name} ))

        return exists

    def delete_from_collection(self, dbx, ws_name, collection_name, shard_key=None):
        '''
        if the collection is sharded, we need to query to get shard key values before
        we can delete.
        '''
        if shard_key and self.is_cosmos:
            # query to get shard keys for matching records
            records = self.mongo_with_retries("delete_from_collection", dbx, \
                lambda: dbx[collection_name].find({"ws_name": ws_name}, {shard_key: 1} ), return_records=True)
            shard_keys = [r[shard_key] for r in records]

            # now delete using shard_keys
            if shard_keys:

                # Cosmos DB doesn't support delete_many with shard keys, so we work around issue with bluk_delete
                #self.mongo_with_retries("delete_from_collection", lambda: dbx[collection_name].delete_many( {shard_key: {"$in": shard_keys}} ))
                self.limited_bulk_delete(dbx, collection_name, shard_keys, key_name=shard_key)
        else:
            # easy case; just delete by ws_name
            self.mongo_with_retries("delete_from_collection", dbx, \
                lambda: dbx[collection_name].delete_many( {"ws_name": ws_name} ))

    def limited_bulk_delete(self, dbx, collection_name, keys, key_name="_id"):
        '''
        Limit number of documents being deleted to a small avoid to avoid "request rate too large"
        errors.  Since using shard keys with Cosmos, we can only target a single key (document) on 
        each delete, so we use bulk_write to batch up a set of commands.
        '''

        max_deletes = 10    # 25 gives "request rate is too large" errors 
        index = 0

        while index < len(keys):
            key_batch = keys[index:index+max_deletes]

            delete_cmds = []
            for key in key_batch:
                cmd = pymongo.operations.DeleteOne( {key_name: key} )
                delete_cmds.append(cmd)

            self.mongo_with_retries("limited_bulk_delete", dbx, \
                lambda: dbx[collection_name].bulk_write( delete_cmds ))

            index += len(key_batch)


    def create_workspace_if_needed(self, ws_name, db_name=None):
        fd = {"_id": ws_name}

        # workspace definitions are stored in DEFAULT_DB
        if not db_name:
            db_name = DEFAULT_DB

        dbx = self.get_db(db_name=DEFAULT_DB)
        records = self.mongo_with_retries("create_workspace_if_needed", dbx, \
            lambda: dbx[WORKSPACES].find(fd, {"db_name": 1}), return_records=True)

        if records:
            # workspace already exists
            db_name = utils.safe_cursor_value(records, "db_name")
        else:
            # workspace not found

            # add workspace document
            dd = {"_id": ws_name, "db_name": db_name, "next_job_number": 1, "next_end_id": 1}
            self.update_sys_collection(WORKSPACES, ws_name, dd, dbx=dbx)

            if self.is_cosmos:
                self.create_workspace_collections_if_needed(db_name)

        return db_name

    def set_workspace_counters(self, ws_name, next_job_number, next_end_id):

        dbx = self.get_db(db_name=DEFAULT_DB)
        dd = {"_id": ws_name, "next_job_number": next_job_number, "next_end_id": next_end_id}
        self.update_sys_collection(WORKSPACES, ws_name, dd, dbx=dbx)
        
    def get_workspace_infos(self, filter, fields=None):
        dbx = self.mongo_client[DEFAULT_DB]
        records = self.mongo_with_retries("create_workspace_if_needed", dbx, \
            lambda: dbx[WORKSPACES].find(filter, fields), return_records=True)
        return records

    def get_workspace_names(self):
        dbx = self.mongo_client[DEFAULT_DB]
        records = self.mongo_with_retries("create_workspace_if_needed", dbx, \
            lambda: dbx[WORKSPACES].find({}, {}), return_records=True)

        ws_names = [r["_id"] for r in records]
        return ws_names

    def create_collection_if_needed(self, dbx, name, shard_key, update_freq, index_key=None):

        cd = {"customAction": "CreateCollection", "collection": name}

        if update_freq == "low":
            thruput = 1000
        elif update_freq == "medium":
            thruput = 5000
        else:
            thruput = 10000

        # specify auto scaling and thruput for collection
        cd["autoScaleSettings"] = {"maxThroughput": thruput}

        # specify shard key for collection
        if shard_key:
            cd["shardKey"] = shard_key

        create_indexes = True

        try:
            dbx.command(cd)
        except pymongo.errors.OperationFailure as ex:
            # this is the exception raised by "already exists"
            msg = ex.details["errmsg"]
            if not "already exists" in msg:
                # unexpected exception
                raise
            # collection already exists
            create_indexes = False

        if create_indexes:
            keys = ["_id", "ws_name"]
            if index_key:
                keys.append(index_key)

            for key in keys:
                dbx[name].create_index(key)

    def create_workspace_collections_if_needed(self, db_name):
        '''
        create our 10 collections in the specified database, if needed
        '''
        dbx = self.get_db(db_name=db_name)

        # run data
        self.create_collection_if_needed(dbx, "run_info", "_id", "low")
        self.create_collection_if_needed(dbx, "run_stats", "_id", "medium")
        self.create_collection_if_needed(dbx, "hparams", "_id", "low")
        self.create_collection_if_needed(dbx, "metrics", "_id", "high")
        self.create_collection_if_needed(dbx, "log_records", "_id", "high")

        # job data
        self.create_collection_if_needed(dbx, "job_info", "_id", "low")
        self.create_collection_if_needed(dbx, "job_stats", "_id", "high")
        self.create_collection_if_needed(dbx, "connect_info", "_id", "medium")
        self.create_collection_if_needed(dbx, "service_info_by_node", "_id", "low")
        self.create_collection_if_needed(dbx, "child_runs", "key", "medium", index_key="key")

    def mongo_with_retries(self, name, dbx, mongo_cmd, ignore_error=False, return_records=False, return_single_record=False):
        import pymongo.errors

        max_retry_count = self.max_retries
        result = None
        started = time.time()
        actual_call_time = None
        retry_count = None
        last_error = None
        got_good_result = False

        for i in range(max_retry_count):
            try:
                actual_started = time.time()

                result = mongo_cmd()

                # most of the time, we want to ALSO want to retry building a record set from the cursor
                if return_records:
                    result = list(result) if result else []
                elif return_single_record:
                    if result:
                        result = list(result)
                        if result:
                            result = result[0]

                actual_call_time = time.time() - actual_started
                retry_count = i
                got_good_result = True
                break

            except BaseException as ex:  
                # watch out for these exceptions: AutoReconnect, OperationFailure (and ???)
                last_error = ex

                # this is to help us debug situations where we raise the exception without ever printing retry msgs
                print("got exception in mongo, i={}, retry_count={}, caller={}".format(i, max_retry_count, name), flush=True)

                # # pymongo.errors.OperationFailure: Message: {"Errors":["Request rate is large"]}
                # if ignore_error:
                #     console.print("ignoring mongo-db error: name={}, ex={}".format(name, ex))
                #     break
                
                # we get hit hard on the "Request rate is large" errors when running 
                # large jobs (500+ simultaneous runs), so beef up the backoff times 
                # so that we don't die with a hard failure here
                if i == 0:
                    backoff = 1 + 10*np.random.random()
                    self.retry_errors += 1
                else:
                    # increased from 60 to 180 secs (sep-24-2020)
                    backoff = 1 + self.max_backoff*np.random.random()

                ex_code = ex.code if hasattr(ex, "code") else ""
                ex_msg = str(ex)[0:100]+"..."

                console.print("retrying mongo-db: name={}, retry={}/{}, backoff={:.2f}, ex.code={}, ex.msg={}".\
                    format(name, i+1, max_retry_count, backoff, ex_code, ex_msg))
                    
                time.sleep(backoff)
                
        if not got_good_result:
            errors.service_error("Mongo max retries exceeded={}, error={}".format(max_retry_count, last_error))

        assert got_good_result
        assert bool(actual_call_time)
        assert retry_count is not None

        self.records_check(result)

        # track all mongo calls stats
        elapsed = time.time() - started

        # get RU's used by last command
        response = dbx.command({"getLastRequestStatistics": 1})
        request_units = response["RequestCharge"]        

        if not name in self.call_stats:
            self.call_stats[name] = []

        entry = {"elapsed": elapsed, "actual_call_time": actual_call_time, "retry_count": retry_count, "ru": request_units}
        self.call_stats[name].append(entry)

        #print("--> mongo call: {} (elapsed: {:.4f} secs)".format(name, elapsed))
        return result

    def records_check(self, result):
        # is this a MONGO ERROR that didn't trigger an exception?
        if result and isinstance(result, collections.Iterable) and not isinstance(result, dict):

            # debugging 'big runs' problem
            for info in result:

                # error # 1?
                if "_t" in info and "$err" in info:
                    errors.service_error("Mongo error detected in result: {}".format(result))

                # error # 2?
                if not "_id" in info:
                    errors.internal_error("join_data: info record has no id: {}".format(result))

    def disallow_embedded_props(self, dd, exceptions=[]):
        # in early days of v2, ensure we have no unexpected embedded info
        for name, value in dd.items():
            if isinstance(value, dict):
                assert name in exceptions

    def update_connect_info_by_node(self, ws_name, job_id, node_id, connect_info):
        _id = "{}/{}/{}".format(ws_name, job_id, node_id)
        connect_info["_id"] = _id
        self.update_collection("connect_info", ws_name, connect_info)

    # V2 API
    def add_docs_by_node(self, collection_name, ws_name, job_id, docs_by_node):
        dbx = self.get_db(ws_name)
        inserts = []

        for node_id, docs in docs_by_node.items():
            node_index = utils.node_index(node_id)

            for doc in docs:
                # add _id
                run_index = doc["run_index"]
                _id = "{}/{}/{}".format(ws_name, job_id, run_index)
                doc["_id"] = _id

                # add key (this is how we will filter our operations)
                key = "{}/{}/{}".format(ws_name, job_id, node_index)
                doc["key"] = key

                # all records must specify ws_name
                doc["ws_name"] = ws_name

                inserts.append(doc)

        inserts = self.filter_out_existing_docs(ws_name, inserts, collection_name, dbx)
        if inserts:
            self.insert_many(dbx, collection_name, inserts)

    # V2 API
    def add_doc_by_node(self, collection_name, ws_name, job_id, doc_by_node):
        dbx = self.get_db(ws_name)

        inserts = []

        for node_id, doc in doc_by_node.items():
            node_index = utils.node_index(node_id)

            _id = "{}/{}/{}".format(ws_name, job_id, node_index)
            doc["_id"] = _id
            doc["ws_name"] = ws_name

        inserts = self.filter_out_existing_docs(ws_name, inserts, collection_name, dbx)
        if inserts:
            self.insert_many(dbx, collection_name, inserts)

    def insert_many(self, dbx, collection_name, inserts):
        # prevent rate limit errors
        max_inserts = 10
        start = 0
        while start < len(inserts):
            batch = inserts[start:start+max_inserts]
            self.mongo_with_retries("insert_many", dbx, \
                lambda: dbx[collection_name].insert_many(batch) )
            start += len(batch)

    def filter_out_existing_docs(self, ws_name, docs, collection_name, dbx):
        # create a dict for fast access
        id_list = [doc["_id"] for doc in docs]
        filter = {"_id": {"$in": id_list}}

        # records = self.mongo_with_retries("filter_out_existing_docs", dbx,
        #     lambda: dbx[collection_name].find(filter, {"_id": 1}) )

        records = self.get_info_for_collection(ws_name, collection_name, filter,  {"_id": 1}) 

        found_ids = {record["_id"]:1 for record in records}
        new_docs = [doc for doc in docs if not doc["_id"] in found_ids]

        return new_docs

    def get_collection(self, ws_name, collection_name, filter, fields=None, sort_col=None, 
        sort_dir=1, skip=None, first=None, count_runs=False, buffer_size=None):

        dbx = self.get_db(ws_name)

        # always try mongo first
        records = self.mongo_with_retries("get_collection", dbx, \
            lambda: dbx[collection_name].find(filter, fields), 
            return_records=True)

        # support for mongo.add-log-records == False
        if collection_name == "log_records":
            id_list = filter["key"]["$in"]
            storage_id_list = self.get_ids_without_logs(id_list, records)
            records += self.store.get_log_records_for_runs(ws_name, storage_id_list)

        return records

    def get_ids_without_logs(self, id_list, records):
        if records:
            found_set = set( [r["key"] for r in records] )
            missing_ids = list(set(id_list) ^ found_set)
        else:
            missing_ids = id_list
        
        return missing_ids


    def update_collection(self, collection_name, ws_name, dd, is_flat=True, flat_exceptions=[]):
        '''
        add or update a single record in the specified collection
        '''
        if collection_name == "log_records" and not self.add_log_records:
            return

        dbx = self.get_db(ws_name)

        if is_flat:
            self.disallow_embedded_props(dd, flat_exceptions)

        # ensure we have assigned an id intentionally
        assert "_id" in dd

        # all collections must have ws_name (for deleting all entries in a specified workspace)
        dd["ws_name"] = ws_name

        # use update_one (vs. insert_one) to add or update record (and allow redundant add/updates for storage tracking)
        update = {"$set": dd}
        filter = {"_id": dd["_id"]}

        my_name = "update_collection__{}".format(collection_name)
        self.mongo_with_retries(my_name, dbx, \
            lambda: dbx[collection_name].update_one(filter=filter, update=update, upsert=True) )
            
    def update_sys_collection(self, collection_name, ws_name, dd, dbx=None):
        '''
        add or update a single record in the specified system collection (__workspaces__ or __info__)
        '''
        if not dbx:
            dbx = self.get_db(DEFAULT_DB)

        self.disallow_embedded_props(dd)

        # for sys collections, the caller assigns the _id and key, if any
        # assert not "_id" in dd
        # assert not "key" in dd

        dd["ws_name"] = ws_name

        # use update_one (vs. insert_one) for rewriting same run during mongo v2 dev/debug cycle
        update = {"$set": dd}
        filter = {"_id": dd["_id"]}

        self.mongo_with_retries("update_sys_collection", dbx, 
            lambda: dbx[collection_name].update_one(filter=filter, update=update, upsert=True) )

    def update_collection_bulk(self, collection_name, ws_name, run_or_job_name, dd_list):
        dbx = self.get_db(ws_name)

        updates = []
        for dd in dd_list:
            self.disallow_embedded_props(dd)

            # dd[ws_name] = ws_name
            # dd[run_name] = run_name

            if "key" in dd:
                key = dd["key"]
            else:
                key = ws_name + "/" + run_or_job_name
                dd["key"] = key

            update = {"$set": dd}
            filter = {"key": key}

            update = pymongo.UpdateOne(filter, update, upsert=True)
            updates.append(update)

        self.mongo_with_retries("update_collection_bulk", dbx, \
            lambda: dbx[collection_name].bulk_write(updates) )

    def get_next_job_id(self, ws_name, id_name):
        fd = {"_id": ws_name}
        dbx = self.mongo_client[DEFAULT_DB]
        path = id_name

        record = self.mongo_with_retries("get_next_job_id", dbx, \
            lambda: dbx[WORKSPACES].find_and_modify( {"_id": ws_name}, update={"$inc": {path: 1} }, new=False))

        next_id = record[path]
        return next_id

    def create_db_job(self, jd):
        ws_name = jd["ws_name"]
        job_id = jd["job_id"]

        self.update_job_info(ws_name, job_id, jd, update_primary=True)
        
    def update_job_info(self, ws_name, job_id, orig_dd, update_primary=False):
        '''
        Args:
            - ws_name: name of the associated workspace
            - job_id: name of the job being updated
            - orig_dd: a dictionary of name/value pairs.  Can include nested: service_info_by_node,
                connect_info, child_runs, and hparams.  Other props split between job_info and job_stats.
            - update_primary: specifies if the job_info collection be updated

        Processing:
            This is the CORE function for updating job related information.  The following 
            collections may be updated: job_info, job_stats, service_info_by_node,
                connect_info, child_runs, and hparams.

            In order for the job_info collection to be updated, update_primary must = True.
        '''
        jd = dict(orig_dd)    # make a copy to operator on
        total_runs = jd["run_count"]

        # delete low-priority embedded info
        utils.safe_delete(jd, "runs_by_box")

        # delete obsolete embedded info
        utils.safe_delete(jd, "active_runs")
        utils.safe_delete(jd, "dynamic_runs_remaining")

        # extract embedded info
        service_info_by_node = utils.safe_delete(jd, "service_info_by_node")
        runs_by_box = utils.safe_delete(jd, "runs_by_box")
        connect_info_by_node = utils.safe_delete(jd, "connect_info_by_node")
        secrets_by_node = utils.safe_delete(jd, "secrets_by_node")
        child_runs_by_node = utils.safe_delete(jd, "child_runs_by_node")
        hparams = utils.safe_delete(jd, "hparams")

        # extract job stats
        job_stats = {}
        utils.safe_move(job_stats, jd, "job_status")
        utils.safe_move(job_stats, jd, "completed_runs")
        utils.safe_move(job_stats, jd, "error_runs")
        utils.safe_move(job_stats, jd, "running_nodes")
        utils.safe_move(job_stats, jd, "running_runs")

        # hardcode some stats so that when processing job log, counts are correct
        job_stats["total_runs"] = total_runs
        job_stats["completed_runs"] = 0
        job_stats["error_runs"] = 0
        job_stats["running_nodes"] = 0
        job_stats["running_runs"] = 0

        self.add_id(job_stats, ws_name, job_id)
        self.update_collection("job_stats", ws_name, job_stats)

        # CHILD RUNS
        if child_runs_by_node:
            self.add_docs_by_node("child_runs", ws_name, job_id, child_runs_by_node)

        # add to SERVICE_INFO_BY_NODE
        if service_info_by_node:
            self.add_id(service_info_by_node, ws_name, job_id)
            self.update_collection("service_info_by_node", ws_name, service_info_by_node, is_flat=False)

        # add to CONNECT_INFO
        if connect_info_by_node or secrets_by_node:
            # merge secrets into connect info
            if connect_info_by_node:
                for n1, n2 in zip(connect_info_by_node, secrets_by_node):
                    connect_info_by_node[n1]["secret"] = secrets_by_node[n1]
            else:
                connect_info_by_node = {}
                for node, secret in secrets_by_node.items():
                    connect_info_by_node[node] = {"secret": secret}

            self.add_doc_by_node("connect_info", ws_name, job_id, connect_info_by_node)

        # add to HPARAMS
        if hparams:
            self.add_id(hparams, ws_name, job_id)
            self.update_collection("hparams", ws_name, hparams)

        # add to JOB_INFO
        if update_primary:
            self.add_id(jd, ws_name, job_id)
            self.update_collection("job_info", ws_name, jd, flat_exceptions=["pool_info", "service_job_info"])

    # API call
    def create_db_run(self, rd):
        '''
        Create or update run information in any/all of the 5 run collections.
        '''
        ws_name = rd["ws_name"]
        run_name = rd["run_name"]

        self.update_run_info(ws_name, run_name, rd, update_primary=True)

    def update_run_info(self, ws_name, run_name, orig_dd, hparams=None, metrics=None, update_primary=False):
        '''
        Args:
            - ws_name: name of the associated workspace
            - run_name: name of the run being updated
            - orig_dd: a dictionary of name/value pairs.  Can include nested: hparams, metrics, log_records
            - hparams dict (optional, usually passed in orig_dd)
            - metrics dict (optional, usually passed in orig_dd)
            - update_primary: specifies if the run_info collection be updated

        Processing:
            This is the CORE function for updating run related information.  The following 
            collections may be updated: run_info, run_stats, metrics, hparams, log_records

            In order for the run_info collection to be updated, update_primary must = True.
        '''
        dbx = self.get_db(ws_name)
        dd = dict(orig_dd)      # make copy so we can modify

        # normalize nested info, if present
        if not hparams:
            hparams = {}
            utils.safe_move(hparams, dd, "hparams", flatten=True)

        if not metrics:
            metrics = {}
            utils.safe_move(metrics, dd, "metrics", flatten=True)

        log_records = {}
        utils.safe_move(log_records, dd, "log_records", flatten=False)
        if log_records:
            log_records = log_records["log_records"]     # list or dict

        run_stats = run_helper.remove_run_stats(dd)

        #print("dd=", dd)
        self.disallow_embedded_props(dd)
        
        run_stats["last_time"] = utils.get_arrow_time_str()
        
        _id = self.make_key(ws_name, run_name)

        # # correct for v1 name of workspace
        # if not "ws_name" in dd:
        #     dd["ws_name"] = ws_name
        #     if "ws" in dd:
        #         del dd["ws"]

        # update RUN_INFO
        if update_primary:
            dd["_id"] = _id
            dd["ws_name"] = ws_name
            update_doc = { "$set": dd}
            self.mongo_with_retries("update_run_info", dbx, \
                lambda: dbx["run_info"].update_one( {"_id": _id}, update_doc, upsert=True))

        # update RUN_STATS
        if self.update_run_stats and run_stats:
            run_stats["_id"] = _id
            run_stats["ws_name"] = ws_name
            update_doc = { "$set": run_stats}
            self.mongo_with_retries("update_run_info", dbx, \
                lambda: dbx["run_stats"].update_one( {"_id": _id}, update_doc, upsert=True))

        # update HPARAMS
        if hparams:
            hparams["_id"] = _id
            hparams["ws_name"] = ws_name
            update_doc = { "$set": hparams}
            self.mongo_with_retries("update_run_info", dbx, \
                lambda: dbx["hparams"].update_one( {"_id": _id}, update_doc, upsert=True))

        # update METRICS
        if metrics:
            metrics["_id"] = _id
            metrics["ws_name"] = ws_name
            update_doc = { "$set": metrics}

            self.mongo_with_retries("update_run_info", dbx, \
                lambda: dbx["metrics"].update_one( {"_id": _id}, update_doc, upsert=True))

        # update LOG_RECORDS
        if log_records and self.add_log_records:
            if isinstance(log_records, list):
                # list of log records (likely called from import)
                self.add_log_record_bulk_limited(ws_name, run_name, log_records)
            else:
                self.add_log_record(ws_name, run_name, log_records)

    def process_run_event(self, ws_name, run_name, event, orig_dd, record_dict):
        run_stats = {}
        completed = False
        dd = dict(orig_dd)

        if event == "created":
            #self.create_db_run(dd)
            utils.safe_delete(dd, "node")
            utils.safe_delete(dd, "run_index")

            self.add_id(dd, ws_name, run_name)
            self.update_collection("run_info", ws_name, dd)

        elif event == "status-change":
            run_stats.update(dd)

        elif event == "ended":
            dd = dict(dd)    # make local copy that we can update
            del dd["metrics_rollup"]
            run_stats.update(dd)
            completed = True

        elif event in ["queued", "ended"]:
            run_stats["status"] = event

        elif event in ["started"]:
            run_stats["status"] = "running"

        elif event == "hparams":
            self.add_id(dd, ws_name, run_name)
            self.update_collection("hparams", ws_name, dd)

        elif event == "metrics":
            self.metrics.update(dd)

            if not "_id" in self.metrics:
                self.add_id(self.metrics, ws_name, run_name)

            diff = time.time() - self.last_metrics_write

            if diff/60 > self.buffer_metrics:
                # time to write metrics to mongo
                #console.print("WRITING metrics: {}".format(dd))
                self.update_collection("metrics", ws_name, self.metrics)
                self.last_metrics_write = time.time()
            else:
                #console.print("BUFFERING metrics: {}".format(dd))
                pass

        if run_stats:
            self.add_id(run_stats, ws_name, run_name)
            self.update_collection("run_stats", ws_name, run_stats)

        if self.add_log_records:
            self.add_log_record(ws_name, run_name, record_dict)

        return completed

    def on_run_close(self, ws_name, run_name):
        if self.metrics:
            # at end of run, write out the buffered metrics record
            console.print("writing METRICS at end of run: {}".format(self.metrics))
            self.update_collection("metrics", ws_name, self.metrics)

    def add_log_record(self, ws_name, run_name, orig_dd):
        '''
        add single log record dict (dd) to LOG_RECORDS collection
        '''
        if self.add_log_records:
            dd = dict(orig_dd)    # make local copy that we can update
            
            # assign a GUID to each log record's id
            dd["_id"] = str(uuid.uuid4())
            dd["ws_name"] = ws_name

            key = self.make_key(ws_name, run_name)
            dd["key"] = key

            self.update_collection("log_records", ws_name, dd, is_flat=False)

    def add_log_record_bulk_limited(self, ws_name, run_name, log_records):
        '''
        add multiple log record dicts to LOG_RECORDS collection
        '''
        if self.add_log_records:
            dbx = self.get_db(ws_name)
            key = self.make_key(ws_name, run_name)

            max_inserts = 10    # 25 gets request rate errors
            index = 0

            while index < len(log_records):
                log_batch = log_records[index : index+max_inserts]

                for dd in log_batch:
                    # assign a GUID to each log record's id
                    dd["_id"] = str(uuid.uuid4())
                    dd["ws_name"] = ws_name

                    if not "key" in dd:
                        dd["key"] = key

                self.mongo_with_retries("add_log_record_bulk_limited", dbx, \
                    lambda: dbx["log_records"].insert_many(log_batch) )

                index += len(log_batch)

    def process_job_events(self, ws_name, job_id, event_records):
        completed = False
        runs = []

        for ev in event_records:
            event = ev["event"]
            dd = ev["data"]

            if event == "node_start":
                self.job_node_start(ws_name, job_id)
            elif event == "node_end":
                completed = self.job_node_exit(ws_name, job_id)
                # add parent run to list of runs
                run = dd["run"]
                runs.append(run)
            elif event == "start_run":
                self.job_run_start(ws_name, job_id)
                run = dd["run"]
                runs.append(run)
            elif event == "end_run":
                is_parent = utils.safe_value(dd, "is_parent")
                if not is_parent:
                    exit_code = dd["exit_code"]
                    self.job_run_exit(ws_name, job_id, exit_code)

        return completed, runs

    def get_service_info_by_node(self, ws_name, job_id):
        dbx = self.get_db(ws_name)

        key = ws_name + "/" + job_id
        filter_dict = {"_id": key}
        records = self.mongo_with_retries("get_service_info_by_node", dbx, \
            lambda: dbx["service_info_by_node"].find(filter_dict), return_records=True)
        record = records[0] if records else None

        if record:
            # zap the "_id" and ws_name leaving only the node keys
            del record["_id"]
            del record["ws_name"]

        return record

    def reset_child_runs(self, ws_name, job_id, node_index):
        '''
        called at start of node's controller in order to detected restarted runs
        '''
        dbx = self.get_db(ws_name)

        key = "{}/{}/{}".format(ws_name, job_id, node_index)
        fd = {"key": key, "status": constants.STARTED}
        ud = {"$set": {"status": constants.WAITING}}

        records = self.mongo_with_retries("reset_child_runs", dbx, \
            lambda: dbx["child_runs"].find_and_modify(fd, update=ud), return_records=True)

    def get_next_child_run(self, ws_name, job_id, node_index):
        '''
        finds next child run that needs to be run for the specified node.
        '''
        dbx = self.get_db(ws_name)

        key = "{}/{}/{}".format(ws_name, job_id, node_index)
        fd = {"key": key, "status": {"$in": [constants.UNSTARTED, constants.WAITING]}}
        ud = {"$set": {"status": constants.STARTED}}
        #console.print("get_next_child_run: key=", key, "fd=", fd, "ud=", ud)

        # this should return a single record
        entry = self.mongo_with_retries("get_next_child_run", dbx, \
            lambda: dbx["child_runs"].find_and_modify(fd, update=ud), return_records=False)

        return entry

    def mark_child_run_completed(self, entry):
        '''
        finds next child run that needs to be run for the specified node.
        '''
        key = entry["key"]
        run_index = entry["run_index"]
        ws_name = entry["ws_name"]

        dbx = self.get_db(ws_name)

        fd = {"key": key, "run_index": run_index}
        ud = {"$set": {"status": "completed"}}

        self.mongo_with_retries("mark_child_run_completed", dbx, \
            lambda: dbx["child_runs"].update_one(fd, update=ud))

    def make_key(self, ws_name, job_or_run_name):
        return ws_name + "/" + job_or_run_name

    def add_id(self, dd, ws_name, job_or_run_name):
        _id = ws_name + "/" + job_or_run_name
        dd["_id"] = _id

    def job_run_start(self, ws_name, job_id):
        '''
        A job's run has started running.  We need to:
            - increment the job's "running_runs" property 
        '''
        if self.update_job_stats:
            dbx = self.get_db(ws_name)
            _id = self.make_key(ws_name, job_id)

            cmd = lambda: dbx["job_stats"].find_and_modify( {"_id": _id}, update={"$inc": {"running_runs": 1} })
            self.mongo_with_retries("job_run_start", dbx, cmd)

    def job_run_exit(self, ws_name, job_id, exit_code):
        '''
        A job's run has finished running.  We need to:
            - decrement the job's "running_runs" property 
            - increment the job's "completed_runs" property
            - if exit_code != 0, increment the job's "error_runs" property
        '''
        if self.update_job_stats:
            dbx = self.get_db(ws_name)
            _id = self.make_key(ws_name, job_id)

            error_inc = 1 if exit_code else 0
            cmd = lambda: dbx["job_stats"].find_and_modify( {"_id": _id}, 
                update={"$inc": {"running_runs": -1, "completed_runs": 1, "error_runs": error_inc} }, new=True)

            result = self.mongo_with_retries("job_run_exit", dbx, cmd)

    def run_start(self, ws_name, run_name):
        '''
        A run has started running.  We need to:
            - set the run "start_time" property to NOW
            - set the run "queue_duration" property to NOW - created_time
        '''
        dbx = self.get_db(ws_name)
        run_restarted = False

        if self.update_run_stats:
            now = arrow.now()
            now_str = str(now)

            # fetch create_time of run
            _id = self.make_key(ws_name, run_name)
            cmd = lambda: dbx["run_info"].find({"_id": _id}, {"create_time": 1, "queue_duration": 1, "restarts": 1})
            records = self.mongo_with_retries("run_start", dbx, cmd, return_records=True)

            doc = records[0] if records else None
            create_time_str = utils.safe_value(doc, "create_time")
            queue_duration = utils.safe_value(doc, "queue_duration")
            restarts = utils.safe_value(doc, "restarts")

            # if queue_duration is non-zero, we have started this run previously
            run_restarted = bool(queue_duration) or bool(restarts)
            if run_restarted:
                # increment the "restarts" field of run_stats
                restarts = 1 if restarts is None else restarts + 1
                console.print("===> restart #{} detected: {} <======".format(restarts, run_name))

            if create_time_str:
                create_time_str = doc["create_time"]
                create_time = arrow.get(create_time_str)

                # compute time in "queue" 
                queue_duration = utils.time_diff(now, create_time)

            # update: start_time, queue_duration, restarts
            cmd = lambda: dbx["run_stats"].find_and_modify( {"_id": _id}, \
                update={"$set": {"start_time": now_str, "queue_duration": queue_duration, "restarts": restarts} })
            self.mongo_with_retries("run_start", dbx, cmd)

        return run_restarted

    def run_exit(self, ws_name, run_name, status, exit_code, db_retries=None, storage_retries=None, start_time=None):
        '''
        A run has finished running.  We need to:
            - set the run "run_duration" property to NOW - start_time
        '''
        dbx = self.get_db(ws_name)

        if self.update_run_stats:
            now = arrow.now()
            now_str = str(now)

            # fetch start_time of run
            _id = self.make_key(ws_name, run_name)
            cmd = lambda: dbx["run_stats"].find({"_id": _id}, {"start_time": 1})
            records = self.mongo_with_retries("run_exit #1", dbx, cmd, return_records=True)

            doc = records[0] if records else None
            if doc and "start_time" in doc:
                start_time_str = doc["start_time"]
                start_time = arrow.get(start_time_str)

                # compute run_duration 
                run_duration = utils.time_diff(now, start_time)

                cmd = lambda: dbx["run_stats"].find_and_modify( {"_id": _id}, \
                    update={"$set": {"run_duration": run_duration} })
                self.mongo_with_retries("run_exit #2", dbx, cmd)

    def job_node_start(self, ws_name, job_id, node_index, is_restart):
        '''
        A job's node has started running.  We need to:
            - increment the job's "running_nodes" property
            - set the "job_status" property to "running"
        '''
        dbx = self.get_db(ws_name)

        if self.update_job_stats:
            _id = self.make_key(ws_name, job_id)
            cmd = lambda: dbx["job_stats"].find_and_modify( {"_id": _id}, update={"$inc": {"running_nodes": 1} }, new=True)
            result = self.mongo_with_retries("job_node_start",dbx,  cmd)

            cmd = lambda: dbx["job_stats"].find_and_modify( {"_id": _id}, update={"$set": {"job_status": "running"} }, new=True)
            result2 = self.mongo_with_retries("job_node_start", dbx, cmd)

            console.diag("job_node_start: result={}, result2={}".format(result, result2))

    def job_node_exit(self, ws_name, job_id):
        '''
        A job's node has finished running.  We need to:
            - decrement the job's "running_nodes" property 
            - if running_nodes==0, set the "job_status" property to "completed"
        '''
        dbx = self.get_db(ws_name)
        job_completed = False
        result2 = None

        if self.update_job_stats:
            _id = self.make_key(ws_name, job_id)
            cmd = lambda: dbx["job_stats"].find_and_modify( {"_id": _id}, update={"$inc": {"running_nodes": -1} }, new=True)
            result = self.mongo_with_retries("job_node_exit", dbx, cmd)
            job_completed = (result["running_nodes"] == 0)

            if job_completed:
                cmd = lambda: dbx["job_stats"].find_and_modify( {"_id": _id}, update={"$set": {"job_status": "completed"} })
                result2 = self.mongo_with_retries("job_node_exit", dbx, cmd)

            console.diag("job_node_exit: result={}, result2={}".format(result, result2))

        return job_completed

    # API call
    def set_job_status(self, ws_name, job_id, status):
        if self.update_job_stats:
            _id = self.make_key(ws_name, job_id)
            dbx = self.get_db(ws_name)
            cmd = lambda: dbx["job_stats"].find_and_modify( {"_id": _id}, update={"$set": {"job_status": status} })
            result2 = self.mongo_with_retries("set_job_status", dbx, cmd)
        
    def update_run_at_end(self, ws_name, run_name, status, exit_code, end_time, log_records, hparams, metrics):
        # update run document on Mongo DB
        dbx = self.get_db(ws_name)

        if self.update_run_stats:
            # update properties
            updates = {}
            updates["status"] = status
            updates["exit_code"] = exit_code
            updates["end_time"] = end_time

            # add the unique end_id (relative to ws_name)
            updates["end_id"] = self.get_next_job_id(ws_name, "next_end_id")

            self.update_run_info(ws_name, run_name, updates, hparams, metrics)

    def print_call_stats(self):
        total_count = 0
        total_elapsed = 0
        total_actual = 0
        total_calls = 0
        total_rus = 0
        total_retries = 0

        # build a list of records that we can generate a report from
        records = []

        for name, entries in self.call_stats.items():
            elapsed_list = [entry["elapsed"] for entry in entries]
            actual_call_list = [entry["actual_call_time"] for entry in entries]
            ru_list = [entry["ru"] for entry in entries]
            retry_count_list = [entry["retry_count"] for entry in entries]

            mean_elapsed = np.mean(elapsed_list)
            mean_actual_call = np.mean(actual_call_list)
            mean_ru = np.mean(ru_list)
            mean_retry = np.mean(retry_count_list)

            record = {}
            record["calls"] = len(elapsed_list)
            record["name"] = name
            record["mean_elapsed"] = mean_elapsed
            record["mean_actual"] = mean_actual_call
            record["mean_ru"] = mean_ru
            record["mean_retry"] = mean_retry

            records.append(record)

            # name = (name + ":").ljust(45)
            # print("  {}x {}\t AVERAGE elapsed={:.2f},\t actual={:.2f},\t retries={:.1f}".format(len(elapsed_list), name,
            #     mean_elapsed, mean_actual_call, mean_retry))

            total_calls += len(elapsed_list)
            total_elapsed += np.sum(elapsed_list)
            total_actual += np.sum(actual_call_list)
            total_rus += np.sum(ru_list)
            total_retries += np.sum(retry_count_list)
            total_count += 1

        builder = report_builder.ReportBuilder()

        text, row_count = builder.build_formatted_table(records)

        # print report
        print(text)

        print("  {}x {}: TOTAL elapsed={:.2f} secs, actual={:.2f} secs, RUs={:,.2f}, retries={:,}". \
            format(total_calls, "CALLS", total_elapsed, total_actual, total_rus, total_retries))
        print()

    def make_next_sub_list(self, id_list, index, max_id_length):
        sub_list = []
        str_len = 0

        while index < len(id_list):
            item = id_list[index]

            # will item fit into sub_list?
            str_len += (2 + len(item))   # allow for comma + space
            if str_len > max_id_length:
                break

            # add item
            sub_list.append(item)
            index += 1

        return sub_list

    def get_info_for_collection_breakup(self, dbx, collection_name, filter_dict, fields_dict=None):
        max_id_length = 250000
        id_list = None
        breakup_needed = False

        # break up needed?
        if "_id" in filter_dict:
            value = filter_dict["_id"]
            if "$in" in value:
                id_list = value["$in"]
                if len(str(id_list)) > max_id_length:
                    breakup_needed = True

        if not breakup_needed:
            return None

        records = []
        index = 0
        part = 0
        my_name = "get_info_for_collection_breakup__{}".format(collection_name)

        while index < len(id_list):
            
            sub_list = self.make_next_sub_list(id_list, index, max_id_length)
            if not sub_list:
                break

            # console.print("---> breaking up long query into multiple parts: part={}".format(part))
            # console.print(sub_list)

            filter_dict["_id"] = {"$in": sub_list}

            sub_records = self.mongo_with_retries(my_name, dbx, \
                lambda: dbx[collection_name].find(filter_dict, fields_dict), return_records=True)

            records += sub_records
            index += len(sub_list)
            part += 1

        return records
        
    def get_info_for_collection(self, ws_name, collection_name, filter_dict, fields_dict=None):
        '''
        Core function of getting filter records for a single collection.  
        
        Due to a CosmosDB limit of 262K characters per resulting SQL command, we break up long "$in" queries 
        on "_id" into shorter ones, and combine the results.
        '''
        if not ws_name in filter_dict:
            filter_dict["ws_name"] = ws_name

        dbx = self.get_db(ws_name)
        my_name = "get_info_for_collection__{}".format(collection_name)

        # see if the id_list needs to be broken into parts
        records = self.get_info_for_collection_breakup(dbx, collection_name, filter_dict, fields_dict)

        if records is None:
            # just do as a single query
            records = self.mongo_with_retries(my_name, dbx, \
                lambda: dbx[collection_name].find(filter_dict, fields_dict), return_records=True)

        return records

    def get_filtered_sorted_core(self, ws_name, collection_name, filter_dict, fields_dict=None, sort_col=None, sort_dir=1, 
        skip=None, first=None, return_records=True, count_records=False, buffer_size=None):

        if not ws_name in filter_dict:
            filter_dict["ws_name"] = ws_name

        dbx = self.get_db(ws_name)

        # put our mongo operations together in a RETRYABLE function
        def fetch():

            cursor = dbx[collection_name].find(filter_dict, fields_dict)
            if sort_col:
                cursor = cursor.sort(sort_col, sort_dir)
            if skip:
                cursor = cursor.skip(skip)
            if first:
                cursor = cursor.limit(first)

            '''
            NOTE: we MUST convert cursor to records WITHIN THIS FUNCTION so that actual
            fetching of records from mongoDB is done in our retry loop with proper
            backoff and error reporting.
            '''
            # cursor to records
            if cursor:
                # warn user if returning a large amount of records
                if count_records:
                    count = cursor.count(True)
                    console.print("retreiving {:,} records".format(count))
                    if count > 500:
                        console.print("  for faster results, use the --first or --last option")

                # this is where we can encounter "max message size" errors if we try to get all
                # records at once
                if buffer_size:
                    cursor = cursor.batch_size(buffer_size)

                records = list(cursor)
            else:
                records = []

            return records

        result = self.mongo_with_retries("get_filtered_sorted_core", dbx, fetch, return_records=return_records)
        self.records_check(result)

        return result

    def does_run_exist(self, ws_name, run_name):
        dbx = self.get_db(ws_name)
        _id = self.make_key(ws_name, run_name)
        fd = {"_id": _id}

        records = self.mongo_with_retries("does_run_exist", dbx, \
            lambda: dbx["run_info"].find(fd), return_records=True)
        return bool(records)

    def get_info_for_jobs(self, ws_name, filter_dict, fields_dict=None):
        '''
        does a find on job_info using specified filter columns from job_info only.
        '''

        dbx = self.get_db(ws_name)
        records = self.mongo_with_retries("get_info_for_jobs", dbx, \
            lambda: dbx["job_info"].find(filter_dict, fields_dict), return_records=True)
        return records

    def get_ids_for_filter(self, dbx, ws_name, collection_name, filter, fields, total_ids):

        if total_ids:
            filter["_id"] = {"$in": total_ids}
        else:
            # first filtering must specify ws_name
            filter["ws_name"] = ws_name

        # result = self.mongo_with_retries("get_ids_for_filter", dbx, \
        #     lambda: dbx[collection_name].find(filter, fields), return_records=True)

        result = self.get_info_for_collection(ws_name, collection_name, filter, fields)
        if result:

            # debugging 'big runs' problem
            for info in result:
                if not "_id" in info:
                    errors.internal_error("join_data: info record has no id: {}".format(info))

            ids = [r["_id"] for r in result]
        else:
            # no matching records
            ids = None

        return ids

    def get_ids_for_sorted_filter(self, dbx, ws_name, collection_name, filter, fields, total_ids, sort_col=None, sort_dir=1, 
        skip=None, first=None):

        if total_ids:
            filter["_id"] = {"$in": total_ids}
        else:
            # first filtering must specify ws_name
            filter["ws_name"] = ws_name

        # put our mongo operations together in a RETRYABLE function
        def fetch():

            cursor = dbx[collection_name].find(filter, fields)
            if sort_col:
                cursor = cursor.sort(sort_col, sort_dir)
            if skip:
                cursor = cursor.skip(skip)
            if first:
                cursor = cursor.limit(first)

            records = list(cursor) if cursor else []
            return records
            
        records = self.mongo_with_retries("get_ids_for_sorted_filter", dbx, fetch, return_records=True)
        
        if records:
            ids = [r["_id"] for r in records]
        else:
            # no matching records
            ids = None

        return ids
        
    def filter_uses_tags(self, name, value):
        uses_tags = name.startswith("tags.")
        if not uses_tags:
            if isinstance(value, list):

                # value is a list of dict's
                for dd in value:
                    for key in dd.keys():
                        if key.startswith("tags."):
                            uses_tags = True
                            break

                    if uses_tags:
                        break
            
        return uses_tags

    def get_filtered_sorted_collection(self, collections, primary_collection, ws_name, filter_dict, fields_dict, 
        sort_col, sort_dir, skip, first, count_records, buffer_size):

        dbx = self.get_db(ws_name)
        id_fields = {"_id": 1}
        total_ids = None

        # remove sort_col temp. from filter_dict
        if sort_col and sort_col in filter_dict:
            entry = filter_dict[sort_col]
            if entry == {"$exists": True}:
                del filter_dict[sort_col]

        # process filters in each collection
        for cd in collections:
            c_name = cd["name"]
            c_props = cd["props"]
            c_sorted = cd["sorted"]
            c_filter = {}

            for name, value in dict(filter_dict).items():
                if c_name == "hparams":
                    if name.startswith("hparams."):
                        prop = name.split(".", 1)[1]
                        c_filter[prop] = value
                        del filter_dict[name]
                elif c_name == "metrics":
                    if name.startswith("metrics."):
                        prop = name.split(".", 1)[1]
                        c_filter[prop] = value
                        del filter_dict[name]
                elif name in c_props:
                    # xxx_info or xxx_stats
                    c_filter[name] = value
                    del filter_dict[name]
                elif self.filter_uses_tags(name, value) and "tags" in c_props:
                    # xxx_info or xxx_stats
                    c_filter[name] = value
                    del filter_dict[name]

            if c_sorted:
                # we have reached the last collection
                if c_name == primary_collection:
                    # sort_col is in primary collection, so we can fall down into final get_filtered_sorted_core() call
                    filter_dict = c_filter

                else:
                    # must apply first/last/skip/sort on this
                    if not sort_col in c_filter:
                        c_filter[sort_col] = {"$exists": True}
                    
                    total_ids = self.get_ids_for_sorted_filter(dbx, ws_name, c_name, c_filter, id_fields, total_ids,
                        sort_col, sort_dir, skip=skip, first=first)
                    self.round_trip_count += 1

                    if not total_ids:
                        return []

                    # clear sort-related props since we have applied them already 
                    sort_col = None
                    skip = None
                    first = None
                    last = None

            elif c_filter:
                # filter total_ids by props specified for collection c_name
                total_ids = self.get_ids_for_filter(dbx, ws_name, c_name, c_filter, id_fields, total_ids)
                self.round_trip_count += 1

                if not total_ids:
                    return []

        # now, get matching RUN INFO records, with needed sort/skip/first/last/fields
        # we need to merge total_ids (from previously processed collections) with filter_dict (filter for this collection)
        if total_ids is not None:
            if "ws_name" in filter_dict:
                del filter_dict["ws_name"]

            if "_id" in filter_dict:
                # set total_ids to the INTERSERCTION of total_ids and ids from filter_dict
                value = filter_dict["_id"]
                if isinstance(value, str):
                    value = [value]
                elif isinstance(value, dict):
                    value = value["$in"]

                total_ids = list(set(total_ids) & set(value)) 

            filter_dict["_id"] = {"$in": total_ids}

        if sort_col and not sort_col in filter_dict:
            filter_dict[sort_col] = {"$exists": True}
        
        fd = filter_dict if filter_dict else None
        records = self.get_filtered_sorted_core(ws_name, primary_collection, fd, None, sort_col=sort_col, sort_dir=sort_dir, 
            skip=skip, first=first, return_records=False, count_records=count_records, buffer_size=buffer_size)
        self.round_trip_count += 1

        self.records_check(records)

        if total_ids and records:
            # sort_col was in another collection (not run_info), so sort records now according to total_ids (but may be a subset)
            records_dict = {r["_id"]: r for r in records}
            records = [records_dict[id] for id in total_ids if id in records_dict]

        self.records_check(records)
        return records

    def get_filtered_sorted_run_ids(self, ws_name, filter_dict, fields_dict=None, sort_col=None, sort_dir=1, skip=None, first=None, 
        count_runs=False, buffer_size=50):
        '''
        Processing:
            filter and sort runs (supporting filter and sort cols in related collections) and return job_id's.
        '''

        collections = [
            {"name": "run_info", "props": run_helper.run_info_props, "sorted": 0},
            {"name": "run_stats", "props": run_helper.run_stats_props, "sorted": 0},
            {"name": "hparams", "props": None, "sorted": 0},
            {"name": "metrics", "props": None, "sorted": 0}
        ]

        # re-order collections so that the one being sorted is on the bottom
        if sort_col:
            if sort_col in run_helper.run_info_props:
                collections[0]["sorted"] = 1
            elif sort_col.startswith("tags.") or sort_col in run_helper.run_stats_props:
                collections[1]["sorted"] = 1
            elif sort_col.startswith("hparams."):
                collections[2]["sorted"] = 1
                sort_col = sort_col.split(".", 1)[1]
            elif sort_col.startswith("metrics."):
                collections[3]["sorted"] = 1
                sort_col = sort_col.split(".", 1)[1]

            collections.sort(key=lambda i: i["sorted"])

        records = self.get_filtered_sorted_collection(collections, "run_info", ws_name, filter_dict, fields_dict, 
            sort_col, sort_dir, skip, first, count_runs, buffer_size)

        return records

    def get_filtered_sorted_job_ids(self, ws_name, filter_dict, fields_dict=None, sort_col=None, sort_dir=1, skip=None, first=None, 
        count_jobs=False, buffer_size=50):
        '''
        Processing:
            filter and sort jobs (supporting filter and sort cols in related collections) and return job_id's.
        '''

        collections = [
            {"name": "job_info", "props": job_helper.job_info_props, "sorted": 0},
            {"name": "job_stats", "props": job_helper.job_stats_props, "sorted": 0},
            {"name": "hparams", "props": None, "sorted": 0},
        ]

        # re-order collections so that the one being sorted is on the bottom
        if sort_col:
            if sort_col in job_helper.job_info_props:
                collections[0]["sorted"] = 1
            elif sort_col.startswith("tags.") or sort_col in job_helper.job_stats_props:
                collections[1]["sorted"] = 1
            elif sort_col.startswith("hparams."):
                collections[2]["sorted"] = 1
                sort_col = sort_col.split(".", 1)[1]

            collections.sort(key=lambda i: i["sorted"])

        records = self.get_filtered_sorted_collection(collections, "job_info", ws_name, filter_dict, fields_dict, 
            sort_col, sort_dir, skip, first, count_jobs, buffer_size)

        return records

    def calc_needed_run_collections(self, orig_fields_dict, include_log_records=False):
        '''
        Processing:
            Collect names of related run collections specified by fields_dict
            and remove those fields from fields_dict.
        '''
        needed = {}
        fields_dict = dict(orig_fields_dict) if orig_fields_dict else None

        default = 0 if fields_dict else 1

        needed["run_info"] = default
        needed["run_stats"] = default
        needed["metrics"] = default
        needed["hparams"] = default
        needed["log_records"] = include_log_records

        if fields_dict:

            for name, value in orig_fields_dict.items():
                if name.startswith("hparams"):
                    needed["hparams"] = value
                    del fields_dict[name]

                elif name.startswith("metrics"):
                    needed["metrics"] = value
                    del fields_dict[name]

                elif name == "log_records":
                    needed["log_records"] = value
                    del fields_dict[name]

                elif name == "run_stats" or name.startswith("tags.") or name in run_helper.run_stats_props:
                    needed["run_stats"] = value
                    del fields_dict[name]

                elif name == "run_info" or name in run_helper.run_info_props:
                    needed["run_info"] = value
                    del fields_dict[name]
                    #fields_dict["_nosuchfield_"] = 0    # for all run_info fields to be returned

                elif name == "all":
                    needed["run_info"] = value
                    needed["run_stats"] = value
                    needed["log_records"] = value
                    needed["metrics"] = value
                    needed["hparams"] = value
                    del fields_dict[name]

                else:
                    errors.internal_error("unrecognized RUN col_name: {}".format(name))

        if not fields_dict:
            fields_dict = None

        return needed, fields_dict

    def get_all_runs(self, aggregator_dest, ws_name, job_or_exper_name, filter_dict=None, fields_dict=None, use_cache=True, 
        fn_cache=None, batch_size=None):

        '''
        Args:
            aggregator_dest: "job" or "experiment"
            ws_name: name of workspace containing the job or experiment
            job_or_exper_name: name of the aggregating job or experiment
            filter_dict: dict of fields to filter with
            fields_dict: dict of fields to return
            use_cache: (currently not used)
            fn_cache: (currently not used)
            batch_size: used to limit the number of records returned on each round trip to the server
        '''
        if not filter_dict:
            if aggregator_dest == "job":
                filter_dict = {"job_id": job_or_exper_name}
            elif aggregator_dest == "experiment":
                filter_dict = {"exper_name": job_or_exper_name}

        records = self.get_filtered_sorted_run_info(ws_name, filter_dict, fields_dict, buffer_size=batch_size)

        return records

    def get_filtered_sorted_run_info(self, ws_name, filter_dict, fields_dict, sort_col=None, sort_dir=1, skip=None, 
            first=None, count_runs=False, buffer_size=50):
        '''
        Processing:
            1. get filtered and sorted run_id's, with support for filter and sort cols in related collections
            2. get specified fields for run_id's, with support for fields in related collections
        '''
        needed_collections, fields_dict = self.calc_needed_run_collections(fields_dict)

        records = self.get_filtered_sorted_run_ids(ws_name, filter_dict, fields_dict, sort_col=sort_col, sort_dir=sort_dir,
            skip=skip, first=first, count_runs=count_runs, buffer_size=buffer_size)

        self.join_needed_run_collections(ws_name, records, needed_collections)
        
        return records

    def get_info_for_runs(self, ws_name, filter_dict, fields_dict=None, include_log_records=False):

        self.round_trip_count = 0
        needed_collections, fields_dict = self.calc_needed_run_collections(fields_dict, \
            include_log_records=include_log_records)

        records = self.get_info_for_collection(ws_name, "run_info", filter_dict, fields_dict)

        self.join_needed_run_collections(ws_name, records, needed_collections)
        return records
    
    def join_needed_run_collections(self, ws_name, records, needed):
        ids = [run["_id"] for run in records]

        # add RUN_STATS
        if needed["run_stats"]:
            stats = self.get_collection(ws_name, "run_stats", {"_id": {"$in": ids}})
            self.join_data(records, stats)
            self.round_trip_count += 1

        # add HPARAMS
        if needed["hparams"]:
            hparams = self.get_collection(ws_name, "hparams", {"_id": {"$in": ids}})
            self.join_data(records, hparams, embed_name="hparams")
            self.round_trip_count += 1

        # add METRICS
        if needed["metrics"]:
            metrics = self.get_collection(ws_name, "metrics", {"_id": {"$in": ids}})
            self.join_data(records, metrics, embed_name="metrics")
            self.round_trip_count += 1

        # add LOG_RECORDS
        if needed["log_records"]:
            log_records = self.get_collection(ws_name, "log_records", {"key": {"$in": ids}})
            self.join_log_records(records, log_records)
            self.round_trip_count += 1

    def calc_needed_job_collections(self, fields_dict):
        '''
        Processing:
            Collect names of related job collections specified by fields_dict
            and remove those fields from fields_dict.
        '''
        needed = {}
        default = 0 if fields_dict else 1

        needed["job_stats"] = default
        needed["connect_info"] = default
        needed["service_info_by_node"] = default
        needed["job_info"] = default
        needed["hparams"] = default
        needed["tags"] = default

        if fields_dict:
            orig_fd = dict(fields_dict)

            for name, value in orig_fd.items():

                if name.startswith("job_stats") or name in job_helper.job_stats_props:
                    needed["job_stats"] = value
                    del fields_dict[name]

                elif name == "tags" or name.startswith("tags."):
                    needed["tags"] = value
                    del fields_dict[name]

                elif name.startswith("connect_info"):
                    needed["connect_info"] = value
                    del fields_dict[name]

                elif name in ["service_info_by_node", "runs_by_box"]:
                    needed["service_info_by_node"] = value
                    del fields_dict[name]

                elif name == "job_info" or name in job_helper.job_info_props:
                    needed["job_info"] = value
                    del fields_dict[name]
                    #fields_dict["_nosuchfield_"] = 0    # for all job_info fields to be returned

                elif name.startswith("hparams"):
                    needed["hparams"] = value
                    del fields_dict[name]

                elif name == "all":
                    needed["job_stats"] = value
                    needed["connect_info"] = value
                    needed["service_info_by_node"] = value
                    needed["job_info"] = value
                    needed["hparams"] = value
                    del fields_dict[name]

                else:
                    errors.internal_error("Unrecognized JOB col: {}".format(name))

        if not fields_dict:
            fields_dict = None

        return needed, fields_dict

    def get_filtered_sorted_job_info(self, ws_name, filter_dict, fields_dict, sort_col=None, sort_dir=1, skip=None, 
            first=None, count_jobs=False, buffer_size=50):
        '''
        Processing:
            1. get filtered and sorted job_id's, with support for filter and sort cols in related collections
            2. get specified fields for job_id's, with support for fields in related collections
        '''
        self.round_trip_count = 0

        needed_collections, fields_dict = self.calc_needed_job_collections(fields_dict)

        records = self.get_filtered_sorted_job_ids(ws_name, filter_dict, fields_dict, sort_col=sort_col, sort_dir=sort_dir,
            skip=skip, first=first, count_jobs=count_jobs, buffer_size=buffer_size)

        self.join_needed_job_collections(ws_name, records, needed_collections)

        return records

    def get_info_for_jobs(self, ws_name, filter_dict, fields_dict=None):
        self.round_trip_count = 0
        needed_collections, fields_dict = self.calc_needed_job_collections(fields_dict)

        records = self.get_info_for_collection(ws_name, "job_info", filter_dict, fields_dict)

        self.join_needed_job_collections(ws_name, records, needed_collections)
        
        return records

    def join_needed_job_collections(self, ws_name, records, needed):
        ids = [job["_id"] for job in records]

        if needed["job_stats"]:
            # add JOB_STATS
            stats = self.get_collection(ws_name, "job_stats", {"_id": {"$in": ids}})
            self.join_data(records, stats)
            self.round_trip_count += 1

        if needed["service_info_by_node"]:
            # add SERVICE_INFO_BY_NODE
            by_node = self.get_collection(ws_name, "service_info_by_node", {"_id": {"$in": ids}})
            self.join_data(records, by_node, embed_name="service_info_by_node")
            self.round_trip_count += 1

        # add CONNECT_INFO
        if needed["connect_info"]:
            connect_info = self.get_collection(ws_name, "connect_info", {"_id": {"$in": ids}})
            self.join_data(records, connect_info, embed_name="connect_info")
            self.round_trip_count += 1

        # add HPARAMS
        if needed["hparams"]:
            hparams = self.get_collection(ws_name, "hparams", {"_id": {"$in": ids}})
            self.join_data(records, hparams, embed_name="hparams")
            self.round_trip_count += 1

        # add TAGS
        if needed["tags"]:
            # NOTE: storage v2 is not currently supported (quicktest is broken; implementation is incomplete)
            tags = self.get_collection(ws_name, "job_tags", {"_id": {"$in": ids}})
            self.join_data(records, tags, embed_name="tags")
            self.round_trip_count += 1

    def join_data(self, records, infos, info_key="_id", embed_name=None):
        # build a dict to quickly find records
        rd = {r["_id"]: r for r in records}

        # debugging 'big runs' problem
        for info in infos:
            if not "_id" in info:
                errors.internal_error("join_data: info record has no id: {}".format(info))

        # update records with infos
        for info in infos:
            id = info[info_key]
            if id in rd:
                record = rd[id]

                if "_id" in info:
                    del info["_id"]

                if "ws_name" in info:
                    del info["ws_name"]

                if embed_name:
                    record[embed_name] = info
                else:
                    record.update(info)

    def join_log_records(self, records, log_recs):
        # build a dict to quickly find records
        rd = {r["_id"]: r for r in records}

        # create a list property on each record
        for record in records:
            record["log_records"] = []

        # add each log_rec to associated record
        for log in log_recs:
            id = log["key"]
            if id in rd:
                record = rd[id]

                # fixup log record
                del log["_id"] 
                del log["key"]

                if "data" in log:
                    data = log["data"]
                    if "_id" in data:
                        del data["_id"]

                # add to record
                record["log_records"].append(log)

    def get_next_run_name(self, ws_name, job_id, is_parent, total_run_count, node_index):
        # v2 run name takes its base from the job_id
        job_num = job_helper.get_job_number(job_id)
        run_name = "run" + str(job_num)

        if total_run_count > 1:
            run_name += constants.NODE_PREFIX + str(node_index)

        return run_name

    def get_all_experiments_in_ws(self, ws_name):
        dbx = self.get_db(ws_name)

        # cannot get "distinct" command to work ("command not supported")
        #cursor = db["__jobs__"].distinct("ws_name") 

        records = self.mongo_with_retries("get_all_experiments_in_ws", dbx, \
            lambda: dbx["job_info"].find({"ws_name": ws_name}, {"exper_name": 1}), return_records=True)

        exper_names = [rec["exper_name"] for rec in records if "exper_name" in rec]
        exper_names = list(set(exper_names))   # remove dups

        console.diag("after get_all_experiments()")        
        return exper_names        

    def get_child_name(self, entry, parent_run_name, first_run_index):
        # use run_index as the child part of the name
        child_num = entry["run_index"]
        parent_num = run_helper.get_parent_run_number(parent_run_name)

        child_name = "run{}.{}".format(parent_num, child_num)
        return child_name

    # API call
    def get_filtered_sorted_node_info(self, ws_name, filter_dict, fields_dict, sort_col=None, sort_dir=1, skip=None, 
        first=None, count_jobs=False, buffer_size=50):
        '''
        for now, node_info documents are not supported on mongo v1.
        '''
        records = []
        return records

    # API call
    def get_info_for_nodes(self, ws_name, filter_dict, fields_dict):
        '''
        for now, node_info documents are not supported on mongo v1.
        '''
        records = []
        return records

    # API call
    def node_start(self, ws_name, job_id, node_index, node_restart, prep_start_str):
        '''
        for now, node_info documents are not supported on mongo v1.
        '''
        pass

    # API call
    def node_end(self, ws_name, job_id, node_index, db_retries, storage_retries, app_start_str):
        '''
        for now, node_info documents are not supported on mongo v1.
        '''
        pass

    # API call
    def node_post_end(self, ws_name, job_id, node_index, post_start_str):
        '''
        for now, node_info documents are not supported on mongo v1.
        '''
        pass

    # API call
    def node_run_start(self, ws_name, job_id, node_index):
        '''
        for now, node_info documents are not supported on mongo v1.
        '''
        pass

    # API call
    def node_run_end(self, ws_name, job_id, node_index, exit_code):
        '''
        for now, node_info documents are not supported on mongo v1.
        '''
        pass

    # API call
    def get_run_count(self, ws_name):
        records = self.get_info_for_runs(ws_name, {"ws_name": ws_name}, {"_id": 1})
        return len(records)

    # API call
    def update_job_run_stats(self, ws_name, job_id, sd):
        '''
        Processing:
            update records in the RUN_STATS collection, using the specified name/values
            in "stats_dict" for all runs in the specified "job_id".
        '''
        update_doc = { "$set": sd}
        dbx = self.get_db(ws_name)

        self.mongo_with_retries("update_job_run_stats", dbx, \
            lambda: self.mongo_db[ws_name].update_one( {"_id": job_id}, update_doc, upsert=True) ) 
    
        # API call
    def set_job_tags(self, ws_name, filter_dict, tag_dict, clear_tags):
        '''
        Update 1 or more job_stats documents from a single set of tag_dict properties.
        Used to update tags on jobs.
        '''
        dbx = self.get_db(ws_name)

        if clear_tags:
            update_doc = { "$unset": tag_dict}
        else:
            update_doc = { "$set": tag_dict}

        matched_count = 0

        # seems mongo requires us to specify a single shard key per query, so let's
        # do this one at a time
        records = self.get_collection(ws_name, "job_info", filter_dict, {"_id": 1})
        id_list = [r["_id"] for r in records]

        for id in filter_dict:
            update_filter = {"_id": id}

            result = self.mongo_with_retries("set_job_tags", dbx, \
                lambda: dbx["job_stats"].update_one( update_filter, update_doc, upsert=True) )

            matched_count += result.matched_count

        return matched_count

    # API call
    def set_run_tags(self, ws_name, filter_dict, tag_dict, clear_tags):
        '''
        Update 1 or more run_stats documents from a single set of tag_dict properties.
        Used to update tags on runs.
        '''
        dbx = self.get_db(ws_name)

        if clear_tags:
            update_doc = { "$unset": tag_dict}
        else:
            update_doc = { "$set": tag_dict}

        matched_count = 0

        # seems mongo requires us to specify a single shard key per query, so let's
        # do this one at a time
        records = self.get_collection(ws_name, "run_info", filter_dict, {"_id": 1})
        id_list = [r["_id"] for r in records]

        for id in filter_dict:
            update_filter = {"_id": id}

            result = self.mongo_with_retries("set_run_tags", dbx, \
                lambda: dbx["run_stats"].update_one( update_filter, update_doc, upsert=True) )

            matched_count += result.matched_count

        return matched_count

    # API call
    def set_insert_buffering(self, value):
        '''
        Support the buffering of multiple insert_record() calls before
        the result is written in a single backend database call.
        '''
        # not supported in mongo_v2
        pass
