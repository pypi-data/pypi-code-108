import os
import pickle
from collections import namedtuple
from typing import Any, Callable, Optional, List
from .constants import DEBUG_DIR
from .utils import create_if_not_exists


Pipeline = namedtuple("Pipeline", ["id", "run"])
Stats = namedtuple("Stats", ["pipeline_id", "times", "objectives"])


def prepare_pipeline(name: str, prep_instance: Callable[[], Any], prep_model: Callable[[Any], Any], run_model: Callable[[Any, Optional[int]], float]):
    """Prepare a pipeline.

    Args:
        prep_instance (Callable[[Any], Any]): Prepared the instance to the pipeline.
        prep_model (Callable[[Any], Any]): From instance to model.
        run_model (Callable[[Any, Optional[int]], float]): From model to solution.
    """
    def run(max_time=None):
        print("Preparing instance...")
        prepared_instance = prep_instance()
        print("Instance prepared.")
        print("Building model...")
        prepared_model = prep_model(prepared_instance)
        print("Model built.")
        print("Solving model...")
        obj = run_model(prepared_model, max_time)
        print("Model solved.")
        return obj
    return Pipeline(name, run)


def evaluate_pipelines(pipelines: List[Pipeline], pb_name="", debug_dir=DEBUG_DIR):
    """Evaluate pipelines with instance

    Args:
        instance (Any): The input instance given to your pipeline
        pipelines (List[Pipeline]): The pipelines
        pb_name (str, optional): The name of the problem. Defaults to "".
        debug_dir ([type], optional): The folder where the debug files are saved. Defaults to DEBUG_DIR.
    """
    create_if_not_exists(debug_dir)
    pipelines_stats = []
    for pipeline in pipelines:
        pipeline_path = os.path.join(debug_dir, f"{pb_name}.{pipeline.id}.pkl")
        if os.path.exists(pipeline_path):
            with open(pipeline_path, 'rb') as f:
                pipelines_stats.append(pickle.load(f))
        else:
            pipeline_id, run = pipeline
            pipeline_stats = Stats(pipeline_id, [], [])
            for max_t in [5, 15, 30, 60, 120]:
                print(f"Solving model {pipeline_id}(max_t={max_t})...")
                obj = run(max_time=max_t)
                pipeline_stats.times.append(max_t)
                pipeline_stats.objectives.append(obj)
                print(f"Model {pipeline_id}(max_t={max_t}) stoped. [{obj}]")
            with open(pipeline_path, 'wb') as f:
                print(pipeline_stats)
                pickle.dump(pipeline_stats, f)
            pipelines_stats.append(pipeline_stats)
    for pipeline_stats in pipelines_stats:
        print(f"Pipeline {pipeline_stats.pipeline_id}")
        for t, obj in zip(pipeline_stats.times, pipeline_stats.objectives):
            print(f"\t{t}s: {obj}")
        print()
