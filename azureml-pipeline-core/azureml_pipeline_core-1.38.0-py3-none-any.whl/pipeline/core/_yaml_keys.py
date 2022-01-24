# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""_yaml_keys.py, class for defining yaml keys."""

ScheduleRecurrenceYaml = ['frequency', 'interval', 'start_time', 'time_zone', 'hours', 'minutes', 'time_of_day',
                          'week_days']
ScheduleYaml = ['description', 'pipeline_parameters', 'wait_for_provisioning', 'wait_timeout', 'datastore_name',
                'polling_interval', 'data_path_parameter_name', 'continue_on_step_failure', 'path_on_datastore',
                'recurrence']

DatabrickStepYamlKeys = {"string": ['existing_cluster_id', 'spark_version', 'node_type', 'instance_pool_id',
                                    'cluster_log_dbfs_path', 'notebook_path', 'python_script_path',
                                    'main_class_name', 'python_script_name', 'run_name', 'permit_cluster_restart'],
                         "integer": ['timeout_seconds', 'max_workers', 'min_workers', 'num_workers']
                         }
AzurebatchStepYamlKeys = {"string": ['vm_size', 'executable', 'pool_id', 'vm_image_urn'],
                          "boolean": ['create_pool', 'delete_batch_job_after_finish', 'delete_batch_pool_after_finish',
                                      'is_positive_exit_code_failure', 'run_task_as_admin', 'target_compute_nodes']
                          }
