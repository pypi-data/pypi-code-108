#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
#
# mongo_v1.py: functions that read/write mongo_db data (xt format v1)
import os
import sys
import time
import json
import copy
import arrow
import shutil
import numpy as np
import logging
from interface import implements

from xtlib import utils
from xtlib import errors
from xtlib import constants
from xtlib import file_utils
from xtlib import run_helper
from xtlib.storage.db_interface import DbInterface

from xtlib.console import console

logger = logging.getLogger(__name__)

MONGO_INFO = "__mongo_info__"

class MongoDB(implements(DbInterface)):
    '''
    We use MongoDB to provide fast query access to a large collection of run data.

    NOTE: *Every* underlying MongoDB operation should be wrapped with retryable code, since all sorts of general
    errors results from too much traffic can happen anywhere.

    Currently, we experience severe capacity problems running approx. 500 runs at once 
    (across all users on team).  We need to find a way to scale up to larger limits.

    MongoDB v1 organizes its data as follows:
        - database: xtdb
        - collections:
            __mongo_info__  (single record about format version & paired storage account)
            __jobs__        (document for each nested JOB_INFO, with id=job_id)            
            ws_counters     (__job__ document and a document for each workspace)
            <ws name>       (a collection exists for each workspace; documents are the nested RUN_INFO with id=run_name)             

    '''
    def __init__(self, mongo_conn_str, run_cache_dir):
        if not mongo_conn_str:
            errors.internal_error("Cannot initialize MongoDB() with a empty mongo_conn_str")

        # debug only (show version of pymongo being used)
        # os.system("pip list | grep pymongo")
        # os.system("conda info")

        self.mongo_conn_str = mongo_conn_str
        self.run_cache_dir = run_cache_dir
        self.mongo_client = None
        self.mongo_db = None
        self.call_stats = {}
        self.name = "mongo_v1"
        self.round_trip_count = 0

        # keep a count of how many retryable errors we have encountered
        self.retry_errors = 0

        self.run_cache_dir = os.path.expanduser(run_cache_dir) if run_cache_dir else None

        # initialize mondo-db now
        self.init_mongo_db_connection()

        # controls for mongo stats and logging
        self.update_job_stats = True
        self.update_run_stats = True
        self.add_log_records = True

        # this is used to return row_count of available records for first/last queries
        self.avail_row_count = None

    #---- UTILS ----

    # API call
    def get_db_type(self):
        return "mongo_v1"

    def get_service_name(self):
        _, rest = self.mongo_conn_str.split("//", 1)
        if ":" in rest:
            name, _ = rest.split(":", 1)
        else:
            name, _ = rest.split("/", 1)

        return name
        
    def init_mongo_db_connection(self):
        ''' create mongo_db on-demand since it has some startup overhead (multiple threads, etc.)
        '''
        if not self.mongo_db:
            if self.mongo_conn_str:
                from pymongo import MongoClient

                self.mongo_client = MongoClient(self.mongo_conn_str)

                # this will create the mongo database called "xtdb", if needed
                self.mongo_db = self.mongo_client["xtdb"]

    def get_db_info(self):
        records = self.mongo_with_retries("get_db_info", lambda: self.mongo_db[MONGO_INFO].find({"_id": 1}, None), return_records=True)
        record = records[0] if records and len(records) else None
        return record

    def set_db_info(self, db_info): 
        self.mongo_with_retries("set_mongo_info", lambda: self.mongo_db[MONGO_INFO].update( {"_id": 1}, db_info, upsert=True) )
        
    def delete_workspace_if_needed(self, ws_name):
        self.remove_cache(ws_name)

        # remove associated mongo_db container
        container = self.mongo_db[ws_name]

        self.mongo_with_retries("delete_workspace_if_needed", lambda: container.drop())
        count = container.count()

        console.diag("  after mongo_db container={} dropped, count={}=".format(container, count))

        # remove counters for this workspace
        cmd = lambda: self.mongo_db.ws_counters.remove( {"_id": ws_name} )
        self.mongo_with_retries("delete_workspace_if_needed", cmd, ignore_error=True)

        # remove legacy counters for this workspace
        end_id = ws_name + "-end_id"
        cmd = lambda: self.mongo_db.ws_counters.remove( {"_id": end_id} )
        self.mongo_with_retries("delete_workspace_if_needed", cmd)

    def remove_cache(self, ws_name):
        # remove appropriate node of run_cache_dir
        if self.run_cache_dir:
            cache_fn = os.path.expanduser(self.run_cache_dir) + "/" + constants.RUN_SUMMARY_CACHE_FN
            cache_fn = cache_fn.replace("$ws", ws_name)
            cache_dir = os.path.dirname(cache_fn)

            if os.path.exists(cache_dir):
                console.print("  zapping cache_dir=", cache_dir)
                file_utils.zap_dir(cache_dir)

    #def set_workspace_counters(self, ws_name, next_run, next_end):
    def set_workspace_counters(self, ws_name, next_job_number, next_end_id):
        update_doc = { "_id": ws_name, "next_run": next_job_number, "next_end": next_end_id, "next_child" : {} }

        cmd = lambda: self.mongo_db.ws_counters.find_and_modify( {"_id": ws_name}, update=update_doc, upsert=True)
        self.mongo_with_retries("set_workspace_counters", cmd)

    def get_workspace_names(self):
        db = self.mongo_db
        records = self.mongo_with_retries("get_workspace_names", lambda: db.ws_counters.find(None, {"_id": 1}), return_records=True)
        names = [rec["_id"] for rec in records if rec["_id"] != "__jobs__"]
        return names

    def get_next_sequential_job_id(self, default_next):
        job_ws = "__jobs__"
        path = "next_job"

        db = self.mongo_db

        # does a counters doc exit for this ws_name?
        records = self.mongo_with_retries("get_next_sequential_job_id", lambda: db.ws_counters.find({"_id": job_ws}).limit(1), return_records=True)
        if not records:
            self.mongo_with_retries("get_next_sequential_job_id", lambda: db.ws_counters.insert_one( {"_id": job_ws, path: default_next} ))

        document = self.mongo_with_retries("get_next_sequential_job_id", lambda: \
                db.ws_counters.find_and_modify( {"_id": job_ws}, update={"$inc": {path: 1} }, new=False))

        next_id = document[path]
        return next_id

    def get_legacy_end_id(self, ws_name):
        db = self.mongo_db
        doc_id = ws_name + "-end_id"
        records = self.mongo_with_retries("get_legacy_end_id", lambda: db.ws_counters.find({"_id": doc_id}).limit(1), return_records=True)
        last_id = utils.safe_cursor_value(records, "last_id")
        return last_id

    def get_next_sequential_ws_id(self, ws_name, path, default_next_run):
        db = self.mongo_db

        assert not "/" in ws_name 
        assert not "/" in path 
        
        console.diag("ws={}, path={}, default_next_run={}".format(ws_name, path, default_next_run))

        # does a counters doc exist for this ws_name?
        records = self.mongo_with_retries("get_next_sequential_ws_id", lambda: db.ws_counters.find({"_id": ws_name}).limit(1), return_records=True)
        if not records:
            console.diag("LEGACY ws={} found in get_next_sequential_ws_id".format(ws_name))

            # we need BOTH next_run and next_end for a new record 
            last_id = self.get_legacy_end_id(ws_name)
            default_next_end = 1 + last_id if last_id else 1

            info = {"_id": ws_name, "next_run": default_next_run, "next_end": default_next_end, "next_child": {}}
            self.mongo_with_retries("get_next_sequential_ws_id", lambda: db.ws_counters.insert_one( info ))

        document = self.mongo_with_retries("get_next_sequential_ws_id", lambda: \
            db.ws_counters.find_and_modify( {"_id": ws_name}, update={"$inc": {path: 1} }, new=False))

        next_id = utils.safe_nested_value(document, path)

        if not next_id:
            # child id's start at 0; if we got that, skip it and get next one
            document = self.mongo_with_retries("get_next_sequential_ws_id", lambda: \
                db.ws_counters.find_and_modify( {"_id": ws_name}, update={"$inc": {path: 1} }, new=False))
            next_id = utils.safe_nested_value(document, path)
     
        return next_id

    def get_next_job_id(self, default_next):
        return self.get_next_sequential_job_id(default_next=default_next)

    def get_next_run_id(self, ws_name, default_next=1):
        return self.get_next_sequential_ws_id(ws_name, "next_run", default_next)

    def get_next_child_id(self, ws_name, run_name, default_next=1):
        return self.get_next_sequential_ws_id(ws_name, "next_child." + run_name, default_next)

    def get_next_end_id(self, ws_name, default_next_run=1):
        return self.get_next_sequential_ws_id(ws_name, "next_end", default_next_run)

    def get_next_end_id_without_update(self, ws_name):

        db = self.mongo_db
        filter_dict = {"_id": ws_name}
        fields_dict = {"next_end": 1}

        records = self.mongo_with_retries("get_next_end_id_without_update", lambda: \
            db.ws_counters.find(filter_dict, fields_dict).limit(1), return_records=True)

        #print("records=", records, ", ws_name=", ws_name, ", filter=", filter_dict, ", fields=", fields_dict)
        next_end = utils.safe_cursor_value(records, "next_end")
        assert next_end >= 1

        return next_end

    def mongo_with_retries(self, name, mongo_cmd, ignore_error=False, return_records=False):
        import pymongo.errors

        retry_count = 25
        result = None
        started = time.time()

        for i in range(retry_count):
            try:
                result = mongo_cmd()

                # most of the time, we want to ALSO want to retry building a record set from the cursor
                if return_records:
                    result = list(result) if result else []
                break
            # watch out for these exceptions: AutoReconnect, OperationFailure (and ???)
            except BaseException as ex:   # pymongo.errors.OperationFailure as ex:
                
                # this is to help us debug situations where we raise the exception without ever printing retry msgs
                print("got exception in mongo, i={}, retry_count={}, caller={}".format(i, retry_count, name), flush=True)

                # since we cannot config logger to supress stderr, don't log this
                #logger.exception("Error in mongo_with_retries, ex={}".format(ex))
                
                # pymongo.errors.OperationFailure: Message: {"Errors":["Request rate is large"]}
                if ignore_error:
                    console.print("ignoring mongo-db error: name={}, ex={}".format(name, ex))
                    break
                
                if i == retry_count-1:
                    # we couldn't recover - signal a hard error/failure
                    raise ex

                # we get hit hard on the "Request rate is large" errors when running 
                # large jobs (500 simultaneous runs), so beef up the backoff times to
                # [1,61] so we don't die with a hard failure here
                if i == 0:
                    backoff = 1 + 10*np.random.random()
                    self.retry_errors += 1
                else:
                    backoff = 1 + 60*np.random.random()

                ex_code = ex.code if hasattr(ex, "code") else ""
                ex_msg = str(ex)[0:60]+"..."

                console.print("retrying mongo-db: name={}, retry={}/{}, backoff={:.2f}, ex.code={}, ex.msg={}".format(name, i+1, retry_count, backoff, 
                    ex_code, ex_msg))
                    
                time.sleep(backoff)
                
        # track all mongo calls stats
        elapsed = time.time() - started

        if not name in self.call_stats:
            self.call_stats[name] = []
        self.call_stats[name].append(elapsed)

        #print("--> mongo call: {} (elapsed: {:.4f} secs)".format(name, elapsed))
        return result

    def print_call_stats(self):
        total_count = 0
        total_time = 0
        total_calls = 0

        for name, stats in self.call_stats.items():
            mean = np.mean(stats)
            print("  {}x {}: avg={:.4f}".format(len(stats), name, mean))

            total_calls += len(stats)
            total_time += np.sum(stats)
            total_count += 1

        print()
        print("  {}x {}: total={:.4f} secs".format(total_calls, "CALLS", total_time))
        print()

    #---- RUNS ----

    def create_db_run(self, dd):
        # create run document on Mongo DB
        # copy standard CREATE properties
        run_doc = copy.deepcopy(dd)

        # zap a few we don't want
        if "event" in run_doc:
            del run_doc["event"]

        if "time" in run_doc:
            del run_doc["time"]

        # add some new ones
        is_azure = utils.is_azure_batch_box(dd["box_name"])

        run_doc["_id"] = dd["run_name"]
        run_doc["status"] = "allocating" if is_azure else "created"
        run_doc["duration"] = 0
        
        # add the new RUN document
        ws_name = dd["ws"]

        cmd = lambda: self.mongo_db[ws_name].insert_one(run_doc)
        self.mongo_with_retries("create_db_run", cmd, ignore_error=True)

    def process_run_event(self, ws_name, run_name, orig_dd):

        if self.add_log_records:
            # first, add log record to ws/run document
            update_doc = { "$push": {"log_records": orig_dd} }
            self.mongo_with_retries("process_run_event", lambda: self.mongo_db[ws_name].update_one( {"_id": run_name}, update_doc, upsert=True) )

        if self.update_run_stats:
            event_name = orig_dd["event"]
            data_dict = orig_dd["data"]
            updates = {}

            if event_name == "hparams":
                # create a "hparams" dict property for the run record
                self.flatten_dict_update(updates, "hparams", data_dict)
                self.update_run_info(ws_name, run_name, updates)

            elif event_name == "metrics":
                # create a "metrics" dict property for the run record (most recent metrics)
                self.flatten_dict_update(updates, "metrics", data_dict)
                self.update_run_info(ws_name, run_name, updates)

            if event_name == "started":
                updates = { "status": "running" }
                #console.print("updating run STATUS=", updates)
                self.update_run_info(ws_name, run_name, updates)

            elif event_name == "status-change":
                updates = { "status": data_dict["status"] }
                #console.print("updating run STATUS=", updates)
                self.update_run_info(ws_name, run_name, updates)

    def flatten_dict_update(self, updates, dd_name, dd):
        for key, value in dd.items():
            updates[dd_name + "." + key] = value

    def update_run_at_end(self, ws_name, run_name, status, exit_code, end_time, log_records, hparams, metrics):
        # update run document on Mongo DB

        if self.update_run_stats:
            # update properties
            updates = {}
            updates["status"] = status
            updates["exit_code"] = exit_code
            updates["end_time"] = end_time

            # add the unique end_id (relative to ws_name)
            updates["end_id"] = self.get_next_end_id(ws_name)

            # structured properties
            if hparams:
                #updates["hparams"] = hparams
                self.flatten_dict_update(updates, "hparams", hparams)

            if metrics:
                #updates["metrics"] = metrics
                self.flatten_dict_update(updates, "metrics", metrics)
            
            # no longer need this step here (log records are now appended as they are logged)
            #updates["log_records"] = log_records

            self.update_run_info(ws_name, run_name, updates)

    # API call
    def create_db_run(self, rd):
        ws_name = rd["ws"]   # rd["ws_name"]
        run_name = rd["run_name"]

        self.update_run_info(ws_name, run_name, rd, update_primary=True)  # , new_run=True)
        
    def update_run_info(self, ws_name, run_name, orig_dd, hparams=None, metrics=None, update_primary=False):

        clear = False
        dd = dict(orig_dd)

        if self.update_run_stats:
            if clear:
                update_doc = { "$unset": dd}
            else:
                dd["last_time"] = utils.get_arrow_time_str()
                update_doc = { "$set": dd}

            # update, create prop if needed
            self.mongo_with_retries("update_run_info", \
                lambda: self.mongo_db[ws_name].update_one( {"_id": run_name}, update_doc, upsert=True) )

    def does_run_exist(self, ws_name, run_name):
        records = self.get_info_for_runs(ws_name, {"_id": run_name}, {"_id": 1})
        exists = len(records) == 1
        return exists

    def get_info_for_runs(self, ws_name, filter_dict, fields_dict=None, include_log_records=False):

        self.v2_to_v1_run_cols(filter_dict)
        self.v2_to_v1_run_cols(fields_dict)
        
        if fields_dict:
            if "run_info" in fields_dict:
                fields_dict = None
            else:
                for key in ["run_stats", "hparams", "metrics"]:
                    if key in fields_dict:
                        del fields_dict[key]

        if not fields_dict:
            fields_dict = None

        run_records = self.mongo_with_retries("get_boxes_for_runs", lambda: self.mongo_db[ws_name].find(filter_dict, fields_dict), return_records=True)

        for rr in run_records:
            self.v1_to_v2_run_cols(rr)

        console.diag("after get_boxes_for_runs()")        
        return run_records

    def get_filtered_sorted_run_info(self, ws_name, filter_dict, fields_dict, sort_col=None, sort_dir=1, skip=None, 
        first=None, count_runs=False, buffer_size=50):

        self.v2_to_v1_run_cols(filter_dict)
        self.v2_to_v1_run_cols(fields_dict)

        records = self.get_filtered_sorted_container(ws_name, filter_dict, fields_dict, sort_col, sort_dir, skip, first, 
            count_runs, buffer_size)

        for record in records:
            self.v1_to_v2_run_cols(record)

        return records

    def get_all_experiments_in_ws(self, ws_name):
        # cannot get "distinct" command to work ("command not supported")
        #cursor = db["__jobs__"].distinct("ws_name") 

        records = self.mongo_with_retries("get_all_experiments_in_ws", lambda: self.mongo_db["__jobs__"].find({"ws_name": ws_name}, {"exper_name": 1}), 
            return_records=True)

        exper_names = [rec["exper_name"] for rec in records if "exper_name" in rec]
        exper_names = list(set(exper_names))   # remove dups

        console.diag("after get_all_experiments()")        
        return exper_names

    def get_ws_runs(self, ws_name, filter_dict=None, include_log_records=False):
        '''
        design issue: we cannot use a single cache file for different filter requests.  Possible fixes:
            - do not cache here (current option)
            - name cache by filter settings (one cache file per setting) - not ideal
            - keep all runs for ws in cache and apply filter locally (TODO: this option)
        '''
        if include_log_records:
            fields_dict = None   # all fields, including log_records
            fn_cache = self.run_cache_dir + "/" + constants.ALL_RUNS_CACHE_FN
        else:
            fields_dict = {"log_records": 0}
            fn_cache = self.run_cache_dir + "/" + constants.RUN_SUMMARY_CACHE_FN

        fn_cache = fn_cache.replace("$aggregator", ws_name)

        return self.get_all_runs(None, ws_name, None, filter_dict, fields_dict, use_cache=False, fn_cache=fn_cache)

    def get_all_runs(self, aggregator_dest, ws_name, job_or_exper_name, filter_dict=None, fields_dict=None, use_cache=True, 
        fn_cache=None, batch_size=None):
        '''
        cache design: 
            - organized all cached run information by the way it was accessed: a folder for each workspace (created on demand), 
              and under each, a folder specifying the filter_dict and fields_dict.  This way, we only use cache records for
              exactly matching query info.

            - whenever sort, first_count, or last_count is used (that is, included in the mongo db query), we should set "use_cache" to False.

            - note: since Azure Cosmos version of mongo-db doesn't correctly support sort/first/last (totally busted as of Aug 2019), we never
              include sort/first/last in mongo db query.

            - as of 12/20/2019, the only code that correctly uses the fn_cache is hparam_search.  all other code should call with use_cache=False.
        '''
        # PERF-critical function 
        # below code not yet cache-compliant
        use_cache = False

        records = []
        target = 0
        cache = None

        if use_cache and not fn_cache:
            # fn_cache = self.run_cache_dir + "/" + constants.ALL_RUNS_CACHE_FN
            # fn_cache = fn_cache.replace("$aggregator", ws_name)
            use_cache = False      # play it safe for now

        if use_cache and os.path.exists(fn_cache):
            # read CACHED runs
            started = time.time()
            cache = utils.load(fn_cache)
            elapsed = time.time() - started

            target = max([rec["end_id"] if "end_id" in rec else 0 for rec in cache])
            console.print("loaded {:,} records in {:.2f} secs from cache: {}".format(len(cache), elapsed, fn_cache))

        if not filter_dict:
            if aggregator_dest == "job":
                filter_dict = {"job_id": job_or_exper_name}
            elif aggregator_dest == "experiment":
                filter_dict = {"exper_name": job_or_exper_name}

        # if not fields_dict:
        #     # by default, do NOT return inner log records
        #     fields_dict = {"log_records": 0}

        # adjust filter to get only missing records
        if target:
            filter_dict["end_id"] = {"$gt": target}

        console.diag("  mongo: filter: {}, fields: {}".format(filter_dict, fields_dict))

        #records = self.mongo_db[ws_name].find(filter_dict, fields_dict)  
        def cmd_func():
            started = time.time()
    
            cursor = self.mongo_db[ws_name].find(filter_dict, fields_dict)

            #avail = cursor.count()

            # break query into multiple calls to avoid "message max exceeded" errors
            if batch_size:
                cursor = cursor.batch_size(batch_size)

            records = list(cursor)

            if console.level in ["diagnostics", "detail"]:
                elapsed = time.time() - started
                total_count = self.mongo_db[ws_name].count()
                console.diag("  mongo query returned {} records (of {}), took: {:2f} secs".format(len(return_count), total_count, elapsed))

            #explanation = cursor.explain()

            return records

        records = self.mongo_with_retries("get_all_runs", cmd_func)
        return_count = len(records)

        if cache:
            cache += records
            records = cache

        if return_count and use_cache:
            # write to cache 
            started = time.time()
            utils.save(records, fn_cache)
            elapsed = time.time() - started
            console.print("wrote {:,} records to cache, took: {:2f} secs".format(len(records), elapsed))

        return records

    #---- JOBS ----
    def does_jobs_exist(self, ws_name):
        # does document for ws_name exist?
        job_id = "job1"
        cmd = lambda: self.mongo_db["__jobs__"].find({"_id": job_id}, {"_id": 1}).limit(1)
        records = self.mongo_with_retries("does_jobs_exist", cmd, return_records=True)
        found = len(records) > 0

        return found

    def v2_to_v1_run_cols(self, dd):
        if dd:
            names = {"ws_name": "ws"}

            for name2, name1 in names.items():

                if name2 in dd:
                    dd[name1] = dd[name2]
                    del dd[name2]

    def v1_to_v2_run_cols(self, dd):
        if dd:
            names = {"ws": "ws_name"}

            for name2, name1 in names.items():

                if name2 in dd:
                    dd[name1] = dd[name2]
                    del dd[name2]

    def v2_to_v1_job_cols(self, dd):
        if dd:
            names = {}

            for name2, name1 in names.items():

                if name2 in dd:
                    dd[name1] = dd[name2]
                    del dd[name2]

    def v1_to_v2_job_cols(self, dd):
        if dd:
            names = {}

            for name2, name1 in names.items():

                if name2 in dd:
                    dd[name1] = dd[name2]
                    del dd[name2]

    def get_filtered_sorted_container(self, container, filter_dict, col_dict, sort_col, sort_dir,
        skip, first, count_runs, buffer_size):

        # put our mongo operations together in a retry-compatible function
        def fetch():
            # first query is for available count
            cursor = self.mongo_db[container].find(filter_dict, col_dict)
            self.avail_row_count = cursor.count()

            # second query is for actual records
            cursor = self.mongo_db[container].find(filter_dict, col_dict)
            if sort_col:
                cursor = cursor.sort(sort_col, sort_dir)
            if skip:
                cursor = cursor.skip(skip)
            if first:
                cursor = cursor.limit(first)

            return cursor

        # here is where MONGO does all the hard work for us
        cursor = self.mongo_with_retries("get_db_records", fetch)

        # warn user if returning a large amount of records
        #count_runs = utils.safe_value(args, "count")
        if count_runs:
            count = cursor.count(True)
            console.print("retreiving {:,} records".format(count))
            if count > 500:
                console.print("  for faster results, use the --first or --last option")

        # this is where we can encounter "max message size" errors if we try to get all
        # records at once
        #buffer_size = utils.safe_value(args, "buffer_size", 50)
        cursor = cursor.batch_size(buffer_size)
        records = list(cursor)

        self.round_trip_count += 1

        return records

    def get_info_for_jobs(self, ws_name, filter_dict, fields_dict=None):
        # NOTE: ws_name not used in v1 mongo for jobs

        # if this is a v2 request by related collection names, remove them for v1
        if fields_dict:
            if "job_info" in fields_dict:
                fields_dict = None
            else:
                for key in ["job_stats", "connect_info"]:
                    if key in fields_dict:
                        del fields_dict[key]

        if not fields_dict:
            fields_dict = None

        job_records = self.mongo_with_retries("get_info_for_jobs", lambda: \
            self.mongo_db["__jobs__"].find(filter_dict, fields_dict), return_records=True)

        console.diag("after get_info_for_jobs()")        
        return job_records

    def get_filtered_sorted_job_info(self, ws_name, filter_dict, fields_dict, sort_col=None, sort_dir=1, skip=None, 
        first=None, count_jobs=False, buffer_size=50):

        self.v2_to_v1_job_cols(filter_dict)
        self.v2_to_v1_job_cols(fields_dict)

        records = self.get_filtered_sorted_container("__jobs__", filter_dict, fields_dict, sort_col, 
            sort_dir, skip, first, count_jobs, buffer_size)

        for record in records:
            self.v1_to_v2_job_cols(record)

        return records

    def create_db_job(self, jd):
        ws_name = jd["ws_name"]
        job_id = jd["job_id"]

        self.update_job_info(ws_name, job_id, jd)
        
    #def update_job_info(self, ws_name, job_id, dd, clear=False, upsert=True):
    def update_job_info(self, ws_name, job_id, orig_dd, update_primary=False):

        clear = False

        if self.update_job_stats:
            if clear:
                update_doc = { "$unset": orig_dd}
            else:
                update_doc = { "$set": orig_dd}

            # update, create if needed
            self.mongo_with_retries("update_job_info", lambda: self.mongo_db["__jobs__"].\
                update_one( {"_id": job_id}, update_doc, upsert=True) )

    def get_job_names(self, filter_dict=None):
        job_names = []
        fields_dict = {"_id": 1}
        
        cmd_func = lambda: self.mongo_db["__jobs__"].find(filter_dict, fields_dict)
        jobs = self.mongo_with_retries("get_job_names", cmd_func, return_records=True)
        if jobs:
            # filter out just the names
            job_names = [ job["_id"] for job in jobs]

        return job_names

    def get_job_workspace(self, job_id):
        ''' returns name of workspace associated with job'''
        ws_name = None

        # does document for ws_name exist?
        cmd = lambda: self.mongo_db["__jobs__"].find({"_id": job_id}, {"ws_name": 1}).limit(1)
        records = self.mongo_with_retries("get_job_workspace", cmd, return_records=True)

        if records:
            result = records[0]
            if "ws_name" in result:
                ws_name = result["ws_name"]

        return ws_name

    def job_node_start(self, ws_name, job_id, node_index, is_restart):
        '''
        A job's node has started running.  We need to:
            - increment the job's "running_nodes" property
            - set the "job_status" property to "running"
        '''
        if self.update_job_stats:
            cmd = lambda: self.mongo_db["__jobs__"].find_and_modify( {"_id": job_id}, update={"$inc": {"running_nodes": 1} })
            self.mongo_with_retries("job_node_start", cmd)

            cmd = lambda: self.mongo_db["__jobs__"].find_and_modify( {"_id": job_id}, update={"$set": {"job_status": "running"} })
            self.mongo_with_retries("job_node_start", cmd)

    def job_node_exit(self, ws_name, job_id):
        '''
        A job's node has finished running.  We need to:
            - decrement the job's "running_nodes" property 
            - if running_nodes==0, set the "job_status" property to "completed"
        '''
        if self.update_job_stats:
            cmd = lambda: self.mongo_db["__jobs__"].find_and_modify( {"_id": job_id}, update={"$inc": {"running_nodes": -1} })
            self.mongo_with_retries("job_node_exit", cmd)

            cmd = lambda: self.mongo_db["__jobs__"].find_and_modify( {"_id": job_id, "running_nodes": 0}, update={"$set": {"job_status": "completed"} })
            self.mongo_with_retries("job_node_exit", cmd)

    def update_connect_info_by_node(self, ws_name, job_id, node_id, connect_info):
        key = "connect_info_by_node." + node_id
        update_doc = { "$set": {key: connect_info} }
        self.mongo_with_retries("update_connect_info_by_node", lambda: self.mongo_db["__jobs__"].update_one( {"_id": job_id}, update_doc) )

    def job_run_start(self, ws_name, job_id):
        '''
        A job's run has started running.  We need to:
            - increment the job's "running_runs" property 
        '''
        if self.update_job_stats:
            cmd = lambda: self.mongo_db["__jobs__"].find_and_modify( {"_id": job_id}, update={"$inc": {"running_runs": 1} })
            self.mongo_with_retries("job_run_start", cmd)

    def job_run_exit(self, ws_name, job_id, exit_code):
        '''
        A job's run has finished running.  We need to:
            - decrement the job's "running_runs" property 
            - increment the job's "completed_runs" property
            - if exit_code != 0, increment the job's "error_runs" property
        '''
        if self.update_job_stats:
            error_inc = 1 if exit_code else 0
            cmd = lambda: self.mongo_db["__jobs__"].find_and_modify( {"_id": job_id}, update={"$inc": {"running_runs": -1, "completed_runs": 1, "error_runs": error_inc} })
            self.mongo_with_retries("job_run_exit", cmd)

    def run_start(self, ws_name, run_name):
        '''
        A run has started running.  We need to:
            - set the run "start_time" property to NOW
            - set the run "queue_duration" property to NOW - created_time
        '''
        if self.update_run_stats:
            now = arrow.now()
            now_str = str(now)

            # get create_time of run
            cmd = lambda: self.mongo_db[ws_name].find({"_id": run_name}, {"create_time": 1, "queue_duration": 1, "restarts": 1})
            records = self.mongo_with_retries("run_start", cmd, return_records=True)

            doc = records[0] if records else None
            create_time_str = utils.safe_value(doc, "create_time")
            queue_duration = utils.safe_value(doc, "queue_duration")
            restarts = utils.safe_value(doc, "restarts")

            # if queue_duration is non-zero, we have started this run previously
            run_restarted = bool(queue_duration) or bool(restarts)
            if run_restarted:
                # increment the "restarts" field of run_stats (handle None case)
                restarts = 1 if restarts is None else restarts + 1
                console.print("===> restart #{} detected: {} <======".format(restarts, run_name))

            if create_time_str:
                create_time_str = doc["create_time"]
                create_time = arrow.get(create_time_str)

                # compute time in "queue" 
                queue_duration = utils.time_diff(now, create_time)

            # update: start_time, queue_duration, restarts
            cmd = lambda: self.mongo_db[ws_name].find_and_modify( {"_id": run_name}, \
                update={"$set": {"start_time": now_str, "queue_duration": queue_duration, "restarts": restarts} })
            self.mongo_with_retries("run_start", cmd)

    def run_exit(self, ws_name, run_name, status, exit_code, db_retries=None, storage_retries=None, start_time=None):
        '''
        A run has finished running.  We need to:
            - set the run "run_duration" property to NOW - start_time
        '''
        if self.update_run_stats:
            now = arrow.now()
            now_str = str(now)

            # get start_time of run
            cmd = lambda: self.mongo_db[ws_name].find({"_id": run_name}, {"start_time": 1})
            records = self.mongo_with_retries("run_exit #1", cmd, return_records=True)

            doc = records[0] if records else None
            if doc and "start_time" in doc:
                start_time_str = doc["start_time"]
                start_time = arrow.get(start_time_str)

                # compute run_duration 
                run_duration = utils.time_diff(now, start_time)

                cmd = lambda: self.mongo_db[ws_name].find_and_modify( {"_id": run_name}, update={"$set": {"run_duration": run_duration} })
                self.mongo_with_retries("run_exit #2", cmd)

    def get_next_run_name(self, ws_name, job_id, is_parent, total_run_count, node_index):
        # v1 run name takes its base from the workspace
        run_num = self.get_next_run_id(ws_name)
        run_name = "run" + str(run_num)

        return run_name

    def get_child_name(self, entry, parent_run_name, first_run_index):
        # get 1-relative index for node's child runs
        child_num = 1 + (entry["run_index"] - first_run_index)
        parent_num = run_helper.get_parent_run_number(parent_run_name)

        child_name = "run{}.{}".format(parent_num, child_num)
        return child_name

    def on_run_close(self, ws_name, run_name):
        # nothing for v1 to do on this API call
        # because: no metrics to flush
        pass

    # API call
    def create_workspace_if_needed(self, ws_name, db_name=None):
        # nothing for v1 to do on this API call 
        # because: collection created when first RUN_INFO doc is written
        pass

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
    def update_collection(self, collection_name, ws_name, dd, is_flat=True, flat_exceptions=[]):
        '''
        for now, node_info documents are not supported on mongo v1.
        '''
        if collection_name in ["node_info", "node_stats"]:
            pass
        else:
            errors.internal_error("unsupported collection for update_collection: {}".format(collection_name))
    
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

        self.mongo_with_retries("update_job_run_stats", \
            lambda: self.mongo_db["__jobs__"].update_one( {"_id": job_id}, update_doc, upsert=True) ) 
    
    # API call
    def set_job_tags(self, ws_name, filter_dict, tag_dict, clear_tags):

        modified = None

        if self.update_job_stats:
            if clear_tags:
                update_doc = { "$unset": tag_dict}
            else:
                update_doc = { "$set": tag_dict}

            # update, create prop if needed
            result = self.mongo_with_retries("update_job_stats_from_list", \
                lambda: self.mongo_db["__jobs__"].update_many( filter_dict, update_doc, upsert=False) )
            modified = result.modified_count

        return modified

    # API call
    def set_run_tags(self, ws_name, filter_dict, tag_dict, clear_tags):

        modified = None

        if self.update_run_stats:
            if clear_tags:
                update_doc = { "$unset": tag_dict}
            else:
                update_doc = { "$set": tag_dict}

            # update, create prop if needed
            result = self.mongo_with_retries("update_run_stats_from_list", lambda: \
                self.mongo_db[ws_name].update_many( filter_dict, update_doc, upsert=False) )

            modified = result.modified_count

        return modified

    # API call
    def set_insert_buffering(self, value):
        '''
        Support the buffering of multiple insert_record() calls before
        the result is written in a single backend database call.
        '''
        # not supported in mongo_v1
        pass

    # API call
    def set_job_status(self, ws_name, job_id, status):

        if self.update_job_stats:
            cmd = lambda: self.mongo_db["__jobs__"].find_and_modify( {"_id": job_id}, update={"$set": {"job_status": status} })
            self.mongo_with_retries("set_job_status", cmd)
