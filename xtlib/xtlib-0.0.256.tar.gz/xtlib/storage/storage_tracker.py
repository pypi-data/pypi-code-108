# storage_tracker.py: POC for using a local MongoDB to track jobs and runs in Azure Storage
import os
import json
import time
import uuid
import numpy as np

from xtlib import utils
from xtlib import console
from xtlib import run_helper
from xtlib.storage.store import Store
from xtlib.helpers.xt_config import get_merged_config

from xtlib.storage.new_mongo import MongoDB2
from xtlib.impl_storage import ImplStorage

FN_STATE = "~/.xt/storage_tracking_state.txt"

class WorkspaceTracker():
    def __init__(self, tracker, key, ws_name, current_job=0):
        self.tracker = tracker
        self.store = tracker.store
        self.mongo = tracker.mongo
        self.key = key

        self.ws_name = ws_name
        self.ws_log = "__ws__/last_job_created.txt"

        self.current_job = current_job
        self.new_job = current_job

    def check_for_changes(self):
        if self.store.helper.provider.does_blob_exist(self.ws_name, self.ws_log):
            new_job_text = store.helper.provider.get_blob_text(self.ws_name, self.ws_log)
            self.new_job = int(new_job_text) 
        else:
            self.new_job = self.current_job

        return self.current_job != self.new_job

    def process_changes(self):
        start_job = 1 + self.current_job
        self.current_job = self.new_job

        for job in range(start_job, 1+self.new_job):
            job_id = "job{}".format(job)
            self.tracker.track("job", self.ws_name, job_id)

    def to_string(self, obj):
        '''
        persist object to string
        '''
        return {"cls": "WorkspaceTracker", "ws_name": obj.ws_name, "current_job": obj.current_job}

class JobTracker():
    def __init__(self, tracker, key, ws_name, job_id, current_text=""):
        self.tracker = tracker
        self.store = tracker.store
        self.mongo = tracker.mongo
        self.key = key

        self.ws_name = ws_name
        self.job_id = job_id
        self.fn_log = "jobs/{}/job.log".format(job_id)
        self.fn_info = "jobs/{}/job_info.json".format(job_id)
        self.current_text = current_text
        self.new_text = current_text

    def check_for_changes(self):
        if self.store.helper.provider.does_blob_exist(self.ws_name, self.fn_log):
            self.new_text = store.helper.provider.get_blob_text(self.ws_name, self.fn_log)
        else:
            self.new_text = self.current_text            

        return self.current_text != self.new_text

    def process_changes(self):
        if self.new_text:

            if not self.current_text:
                # first time thru: we need to process the JOB INFO file
                if self.store.helper.provider.does_blob_exist(self.ws_name, self.fn_info):
                    info_text = store.helper.provider.get_blob_text(self.ws_name, self.fn_info)
                    ji = json.loads(info_text)
                    self.mongo.create_db_job(ji)

            # just take new portion of new_text
            old_len = len(self.current_text)
            json_lines = self.new_text[old_len:]
            jd = utils.load_json_records(json_lines)

            self.current_text = self.new_text

            # now, process each job status record
            completed, runs = self.mongo.process_job_events(self.ws_name, self.job_id, jd)
            if completed:
                self.tracker.mark_entry_finished(self)

            # track each run
            for run in runs:
                self.tracker.track("run", self.ws_name, run)

    def to_string(self, obj):
        '''
        persist object to string
        '''
        return {"cls": "JobTracker", "ws_name": obj.ws_name, "job_id": obj.job_id, "current_text": self.current_text}


class RunTracker():
    def __init__(self, tracker, key, ws_name, run_name, current_text=""):
        self.tracker = tracker
        self.store = tracker.store
        self.mongo = tracker.mongo
        self.key = key

        self.ws_name = ws_name
        self.run_name = run_name
        self.job_id = "job" + str(run_helper.get_parent_run_number(run_name))

        run_path = store_utils.get_run_path(self.job_id, self.run_name) 
        self.fn_log = "{}/run.log".format(run_path)
        self.current_text = current_text
        self.new_text = current_text

    def check_for_changes(self):
        if self.store.helper.provider.does_blob_exist(self.ws_name, self.fn_log):
            self.new_text = store.helper.provider.get_blob_text(self.ws_name, self.fn_log)
        else:
            self.new_text = self.current_text            

        return self.current_text != self.new_text

    def process_changes(self):
        if self.new_text:

            # just take new portion of new_text
            old_len = len(self.current_text)
            json_lines = self.new_text[old_len:]
            jd = utils.load_json_records(json_lines)

            self.current_text = self.new_text

            # now, process each run log record
            for record in jd:
                dd = record["data"]
                event = record["event"]
                completed = self.mongo.update_run_event(self.ws_name, self.run_name, event, dd, record)
                if completed:
                    self.tracker.mark_entry_finished(self)

    def to_string(self, obj):
        '''
        persist object to string
        '''
        return {"cls": "JobTracker", "ws_name": obj.ws_name, "job_id": obj.job_id, "current_text": self.current_text}

class StorageTrackingDB():
    '''
    Tracks changes to XT storage logs (workspace, jobs, runs) and 
    applies changes to (local) mongoDB collections.  
    
    Because XT and previous runs of StorageTrackingDB might have written some of the 
    information to MongoDB already, we prefer "update" to "insert" for
    information.
    '''
    def __init__(self, store, mongo_cs, ws_name=None, db_name=None):
        self.store = store
        self.mongo = MongoDB2(mongo_cs, ws_name=ws_name, db_name=None)

        self.tracking = {}
        self.processing = {}
        self.finished = {}

        self.load_state()

    def import_run(self, ws, run_name):
        try:
            records = store.get_run_log(ws, run_name)
        except BaseException as ex:
            console.print("error reading run log for {}, ex: {}".format(run_name, ex))
            return

        job_id = None

        # we accumulate info for these over multiple records
        run_stats = {}
        hparams = {}
        metrics = {}
        metric_reports = []

        for rd in records:
            event = rd["event"]
            dd = rd["data"]

            if event == "created":
                # create job on first run
                if not job_id:
                    if not job_id in self.jobs_imported:
                        job_id = dd["job_id"]
                        console.print("  importing: {}".format(job_id))
                        self.import_job(job_id)
                        self.jobs_imported[job_id] = 1

                #console.print("    {}".format(run_name))
                self.mongo.create_db_run(ws, run_name, dd)

            elif event == "status-change":
                run_stats.update(dd)

            elif event == "ended":
                del dd["metrics_rollup"]
                run_stats.update(dd)

            elif event in ["queued", "started", "ended"]:
                run_stats["status"] = event

            elif event in ["queued", "started", "ended"]:
                run_stats["status"] = event

            elif event == "hparams":
                hparams.update(dd)

            elif event == "metrics":
                metrics.update(dd)

                # add to metric reports with a GUID _id
                ddg = dict(dd)
                ddg["_id"] = str(uuid.uuid4())
                ddg["ws_name"] = ws
                ddg["run_name"] = run_name

                metric_reports.append(ddg)

        # after reading all records
        if run_stats:
            self.mongo.update_collection("run_stats", ws, run_name, run_stats)

        if hparams:
            self.mongo.update_collection("hparams", ws, run_name, hparams)

        if metrics:
            self.mongo.update_collection("metrics", ws, run_name, metrics)

        if metric_reports:
            self.mongo.update_collection_bulk("metric_report", ws, run_name, metric_reports)

    def import_from_storage(self, store):
        ''' 
        import XT data from Azure Storage service, for the specified workspace names
        '''
        # console.print("one-time import of jobs data into local mongo-db:")
        # job_names = store.get_job_names_from_storage()

        run_names = store.get_run_names(ws_name)

        # sort in descending order (by number part of run_name)
        run_names.sort(key=lambda r: float(r[3:]), reverse=True)

        if run_names:
            console.print("  ws: {}, {:,} runs found".format(ws_name, len(run_names)))
            count = 0

            for run_name in run_names:
                self.import_run(ws_name, run_name)

                count += 1
                if count % 100 == 0:
                    console.print("  " + run_name)

            console.print("  {} jobs imported".format(count))

    def track(self, type, ws_name, obj_name=""):

        key = "{}/{}/{}".format(type, ws_name, obj_name)
        if not key in self.finished and not key in self.tracking:

            if type == "ws":
                entry = WorkspaceTracker(self, key, ws_name)
                self.tracking[key] = entry

            elif type == "job":
                entry = JobTracker(self, key, ws_name, obj_name)
                self.tracking[key] = entry

            elif type == "run":
                entry = RunTracker(self, key, ws_name, obj_name)
                self.tracking[key] = entry

    def mark_entry_finished(self, entry):
        if entry.key in self.tracking:
            del self.tracking[entry.key]
            self.finished[entry.key] = 1

    def json_dump_helper(self, obj):
        if isinstance(obj, list):
            return json.JSONEncoder.default(obj)

        return obj.to_string(obj)
        
    def json_load_helper(self, dd):
        if "cls" in dd:

            if dd["cls"] == "WorkspaceTracker":
                ws_name = dd["ws_name"]
                key = "{}/{}/{}".format("ws", ws_name, "")
                return WorkspaceTracker(self, key, ws_name, current_job=dd["current_job"]) 

            elif dd["cls"] == "JobTracker":
                ws_name = dd["ws_name"]
                job_id = dd["job_id"]
                key = "{}/{}/{}".format("job", ws_name, job_id)
                return JobTracker(self, key, ws_name, job_id, current_text=dd["current_text"]) 

            elif dd["cls"] == "RunTracker":
                ws_name = dd["ws_name"]
                run_name = dd["run_name"]
                key = "{}/{}/{}".format("run", ws_name, run_name)
                return RunTracker(self, key, ws_name, run_name, current_text=dd["current_text"]) 

        return dd

    def save_state(self):
        fn = os.path.expanduser(FN_STATE)
        with open(fn, "wt") as outfile:
            text = json.dumps([self.tracking, self.finished], default=self.json_dump_helper)
            outfile.write(text)

    def load_state(self):
        fn = os.path.expanduser(FN_STATE)
        if os.path.exists(fn):
            with open(fn, "rt") as infile:
                text = infile.read()
                if text:
                    items = json.loads(text, object_hook=self.json_load_helper)
                    self.tracking, self.finished = items
    
    def monitor_changes(self):
        print("monitoring changes...")

        while True:
            self.processing = {}

            for key, entry in self.tracking.items():
                if entry.check_for_changes():
                    self.processing[key] = entry
            
            if self.processing:
                print("  detected {} change(s), processing...".format(len(self.processing)))

            # NOTE: at some point, we might want to use multiple workers to process changes
            for key, entry in self.processing.items():
                entry.process_changes()

            if self.processing:
                self.save_state()

                # one line status
                print("  tracking {} item(s) ({})".format(len(self.tracking), list(self.tracking.keys())[0:3]))
            else:
                # nothing changed; sleep for 2 secs
                time.sleep(2)

if __name__ == "__main__":
    config = get_merged_config()
    store = Store(config=config)

    mongo_cs = config.get("external-services", "localmongo", "connection-string")   
    #mongo_cs = store.db_conn_str

    # print out info about current service set
    impl_storage = ImplStorage(config, store)
    impl_storage.view_store(None)

    db = StorageTrackingDB(store, mongo_cs)

    db.track("ws", "ws2")
    db.monitor_changes()