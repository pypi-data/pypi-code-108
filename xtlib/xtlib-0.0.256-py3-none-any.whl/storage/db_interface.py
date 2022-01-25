#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
#
# db_interface.py: specifies the interface for XT database services
from interface import Interface

class DbInterface(Interface):

    # def __init__(self, arg_dict=None):
    #     '''
    #     arg_dict are database-specific properties, including credentials
    #     '''
    #     pass
   
    # API call
    def get_service_name(self):
        '''
        Returns:
            name of the service (e.g., xtsandboxsql)

        Description:
            This method is called to get the name of the database service.
        '''
        pass

    # API call
    def get_db_info(self):
        '''
        Returns:
            dict of database/storage pairing

        Description:
            This method is called to validate the match of the database service to the storage service.
        '''
        pass

    # API call
    def set_db_info(self, db_info):
        pass    

    # API call
    def create_workspace_if_needed(self, ws_name, db_name=None):
        pass

    # API call
    def delete_workspace_if_needed(self, ws_name):
        pass

    # API call
    def get_next_run_name(self, ws_name, job_id, is_parent, total_run_count, node_index):
        pass

    # API call
    def update_collection(self, collection_name, ws_name, dd, is_flat=True, flat_exceptions=[]):
        pass

    # API call
    def create_db_job(self, jd):
        pass

    # API call
    def update_job_info(self, ws_name, job_id, orig_dd, update_primary=False):
        pass

    # API call
    def get_info_for_jobs(self, ws_name, filter_dict, fields_dict=None):
        pass

    # API call
    def run_start(self, ws_name, run_name):
        pass

    # API call
    def get_info_for_runs(self, ws_name, filter_dict, fields_dict=None, include_log_records=False):        
        pass

    # API call
    def job_run_start(self, ws_name, job_id):
        pass

    # API call
    def job_run_exit(self, ws_name, job_id, exit_code):
        pass

    # API call
    def job_node_start(self, ws_name, job_id, node_index, is_restart):
        pass

    # API call
    def job_node_exit(self, ws_name, job_id):
        pass

    # API call
    def update_run_info(self, ws_name, run_name, orig_dd, hparams=None, metrics=None, update_primary=False):
        pass

    # API call
    def on_run_close(self, ws_name, run_name):
        pass

    # API call
    def update_run_at_end(self, ws_name, run_name, status, exit_code, end_time, log_records, hparams, metrics):
        pass

    # API call
    def print_call_stats(self):
        pass

    # API call
    def run_exit(self, ws_name, run_name, status, exit_code, db_retries=None, storage_retries=None, start_time=None):
        pass

    # API call
    def get_filtered_sorted_run_info(self, ws_name, filter_dict, fields_dict, sort_col=None, sort_dir=1, skip=None, 
        first=None, count_runs=False, buffer_size=50):
        pass

    # API call
    def get_filtered_sorted_job_info(self, ws_name, filter_dict, fields_dict, sort_col=None, sort_dir=1, skip=None, 
        first=None, count_jobs=False, buffer_size=50):
        pass

    # API call
    def get_child_name(self, entry, parent_run_name, first_run_index):
        pass

    # API call
    def get_all_runs(self, aggregator_dest, ws_name, job_or_exper_name, filter_dict=None, fields_dict=None, use_cache=True, 
        fn_cache=None, batch_size=None):
        pass

    # API call
    def does_run_exist(self, ws_name, run_name):
        pass

    # API call
    def get_filtered_sorted_node_info(self, ws_name, filter_dict, fields_dict, sort_col=None, sort_dir=1, skip=None, 
        first=None, count_jobs=False, buffer_size=50):
        pass

    # API call
    def get_info_for_nodes(self, ws_name, filter_dict, fields_dict):
        pass  

    # API call
    def node_start(self, ws_name, job_id, node_index, node_restart, prep_start_str):
        pass

    # API call
    def node_end(self, ws_name, job_id, node_index, db_retries, storage_retries, app_start_str):
        pass

    # API call
    def node_post_end(self, ws_name, job_id, node_index, post_start_str):
        pass

    # API call
    def node_run_start(self, ws_name, job_id, node_index):
        pass  

    # API call
    def node_run_end(self, ws_name, job_id, node_index, exit_code):
        pass  

    # API call
    def get_run_count(self, ws_name):
        pass

    # API call
    def set_workspace_counters(self, ws_name, next_job_number, next_end_id):
        pass

    # API call
    def get_all_experiments_in_ws(self, ws_name):
        pass

    # API call
    def update_job_run_stats(self, ws_name, job_id, sd):
        '''
        Processing:
            update records in the RUN_STATS collection, using the specified name/values
            in "stats_dict" for all runs in the specified "job_id".
        '''
        pass
    
    # API call
    def set_job_tags(self, ws_name, filter_dict, tag_dict, clear_tags):
        pass

    # API call
    def set_run_tags(self, ws_name, filter_dict, tag_dict, clear_tags):
        pass

    # API call
    def set_insert_buffering(self, value):
        '''
        Support the buffering of multiple insert_record() calls before
        the result is written in a single backend database call.
        '''
        pass

    # API call
    def update_connect_info_by_node(self, ws_name, job_id, node_id, connect_info):
        pass

    # API call
    def create_db_run(self, rd):
        pass

    # API call
    def set_job_status(self, ws_name, job_id, status):
        pass