#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
#
# store_utils.py: store-related helper functions
'''
NOTE: when store.init_store_utils() is called, we dynamically 
REPLACE ALL OF THE BELOW with their version 1 or version 2 equivalents 
(functions and properties).
'''
from xtlib import constants

def make_share_name(name):
   #raise Exception("store-utils not yet initialized")
   pass

def is_share_name(name):
   #raise Exception("store-utils not yet initialized")
   pass

def get_run_path(job_id, run_name):
   #raise Exception("store-utils not yet initialized")
   pass

def get_jobs_container(ws_name):
   #raise Exception("store-utils not yet initialized")
   pass

def make_id(ws_name, obj_name):
   #raise Exception("store-utils not yet initialized")
   pass

# version independent function
def simplify_id(record):
    if "_id" in record:
        _id = record["_id"]
        if "/" in _id:
            _id = _id.split("/")[-1]
            record["_id"] = _id

# version independent function
def simplify_records_id(records):
    if records:
        for r in records:
            simplify_id(r)

MODELS_STORE_ROOT = None
DATA_STORE_ROOT = None
STORAGE_FORMAT = None

