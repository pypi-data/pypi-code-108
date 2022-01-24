# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import argparse
import json
import os
from random import randint
from time import sleep

from azureml.core import Run


class Util:

    @staticmethod
    def str2bool(v):

        if v is None:
            return False
        if isinstance(v, bool):
            return v
        if v.lower() in ('yes', 'True', 'true', 't', 'y', '1'):
            return True
        elif v.lower() in ('no', 'False', 'false', 'f', 'n', '0'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')


many_models_train = None

# Whether or not this driver has been initialized
driver_initialized = False


def _get_automl_settings():
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'automl_settings.json')) as json_file:
        return json.load(json_file)


def _initialize_driver():
    print("Initializing driver")

    parser = argparse.ArgumentParser("split")
    parser.add_argument("--node_count", default=1, type=int, help="number of nodes")
    parser.add_argument("--process_count_per_node", default=1, type=int, help="number of processes per node")
    parser.add_argument(
        "--retrain_failed_models", default=False, type=Util.str2bool, help="retrain failed models only")

    args, _ = parser.parse_known_args()

    # Sleep this worker node for a random amount of time. This helps stagger new traffic over a
    # longer period of time so that service pods have time to auto-scale up.

    max_concurrent_runs = args.node_count * args.process_count_per_node
    traffic_ramp_up_period_in_seconds = min(max_concurrent_runs, 600)
    worker_sleep_time_in_seconds = randint(1, traffic_ramp_up_period_in_seconds)
    print("Traffic ramp up period: {} seconds".format(traffic_ramp_up_period_in_seconds))
    print("Sleeping this worker for {} seconds to stagger traffic ramp-up...".format(worker_sleep_time_in_seconds))
    sleep(worker_sleep_time_in_seconds)
    current_step_run = Run.get_context()
    from azureml.train.automl.runtime._many_models.many_models_train import \
        ManyModelsTrain
    global many_models_train
    many_models_train = ManyModelsTrain(current_step_run=current_step_run,
                                        automl_settings=_get_automl_settings(),
                                        process_count_per_node=args.process_count_per_node,
                                        retrain_failed_models=args.retrain_failed_models)
    print('many_models_train_driver._initialize_driver() done.')


def run(input_data):
    print("Invoking many_models_train_driver.run()")

    # Initiailze the driver when the first mini batch runs.
    # (This is done because the initialize call requires a sleep call to stagger new traffic ramp-up (refer to
    # the initialize method for more info). There can be a large time gap between calls to the PRS in-built init()
    # methods and the in-built run methods. For example, for large datasets, it seems possible for PRS to invoke
    # the init() methods of all workers, and then 15 minutes later, invoke the run methods of all workers. Given that,
    # the sleep call to stagger traffic ramp-up won't work as expected if invoked in the PRS in-built init() method.)
    global driver_initialized
    if not driver_initialized:
        _initialize_driver()
        driver_initialized = True

    global many_models_train
    return many_models_train.run(input_data)
