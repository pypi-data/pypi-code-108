# node_post_wrapup.py: small module called from end of wrapper script

import os

from xtlib import utils
from xtlib.impl_shared import StoreOnDemand

def main():
    #utils.print_env_vars()
    
    store = StoreOnDemand(None)
    ws_name = os.getenv("XT_WORKSPACE_NAME")
    job_id = os.getenv("XT_JOB_ID")

    node_id = os.getenv("XT_NODE_ID")
    node_index = utils.node_index(node_id)

    post_start_str = os.getenv("XT_POST_START_TIME")

    store.database.node_post_end(ws_name, job_id, node_index, post_start_str)
