# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import argparse
from azureml.core import Run


logger = None
many_models_inference = None


def init():
    logger = None
    try:
        from azureml_user.parallel_run import EntryScript
        entry_script = EntryScript()
        logger = entry_script.logger
        logger.info("many_models_inference_driver.init() called")
    except Exception as e:
        print("Failed to initialize logger using EntryScript, initializing logger using default method: {}".format(e))
    current_step_run = Run.get_context()

    parser = argparse.ArgumentParser("split")
    parser.add_argument("--partition_column_names", '--nargs', nargs='*', type=str, help="partition_column_names")
    parser.add_argument("--target_column_name", type=str, help="target column", default=None)
    parser.add_argument("--time_column_name", type=str, help="time column", default=None)
    parser.add_argument("--train_run_id",
                        type=str,
                        default=None,
                        required=False,
                        help="train_run_id: many models training run id.")
    parser.add_argument("--forecast_quantiles", nargs='*', type=float, help="forecast quantiles list", default=None)

    args, _ = parser.parse_known_args()

    from azureml.train.automl.runtime._many_models.many_models_inference import \
        ManyModelsInference
    global many_models_inference
    many_models_inference = ManyModelsInference(current_step_run=current_step_run,
                                                partition_column_names=args.partition_column_names,
                                                target_column_name=args.target_column_name,
                                                time_column_name=args.time_column_name,
                                                train_run_id=args.train_run_id,
                                                forecast_quantiles=args.forecast_quantiles)
    print("many_models_inference_driver.init() done.")


def run(input_data):
    print("Invoking many_models_inference_driver.run()")
    global many_models_inference
    return many_models_inference.run(input_data)
