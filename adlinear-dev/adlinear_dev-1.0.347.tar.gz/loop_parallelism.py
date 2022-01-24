from pathlib import Path

import kfp.dsl as dsl
import kfp
from kubernetes.client.models import V1Toleration
import argparse


# noinspection PyUnresolvedReferences
def function(prog_name, image, memory_limit, cpu):
    container_op = dsl.ContainerOp(
        name=prog_name.stem,
        image=f"eu.gcr.io/second-capsule-253207/{image}:latest",
        command=["python"],
        arguments=[str(prog_name)],
    )
    # Single job specification
    container_op.add_resource_limit("memory", memory_limit)
    container_op.add_resource_limit("cpu", cpu)
    container_op.add_resource_request("memory", memory_limit)
    container_op.add_resource_request("cpu", cpu)
    container_op.add_toleration(
        V1Toleration(key="dedicated", operator="Equal", value="standard-preemptible", effect="NoSchedule")
    )
    return container_op


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates the yaml file to launch several iterations of a program on GCP",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("-p", "--program", type=str, default="", help="Program .py file name")
    parser.add_argument("-i", "--iterations", type=int, default=1, help="Number of times to run the program")
    parser.add_argument(
        "-m", "--max_executions", type=int, default=15, help="Max number of runs that can exist at a time"
    )
    parser.add_argument(
        "-d", "--docker", type=str, default="", help="Docker image name. Default will be the program file name"
    )
    parser.add_argument("-r", "--ram", type=str, default="2G", help="Max ram used by one single run")
    parser.add_argument("-c", "--cpu", type=str, default="1", help="Max number of CPUs used by one single run")
    args = parser.parse_args()

    program = args.program
    iterations = args.iterations
    image_name = args.docker
    parallelism = args.max_executions
    ram = args.ram
    cpus = args.cpu

    program_path = Path(program)

    if not program_path.is_file():
        raise FileNotFoundError(f"Could not find file '{program_path}'")

    if not isinstance(iterations, int):
        raise TypeError("Number of iterations must be an integer")

    if iterations < 0:
        raise ValueError("Number of iterations must be greater than 0")

    if image_name == "":
        image_name = program_path.stem

    @dsl.pipeline(name="function")
    def pipeline():
        loop_args = list(range(iterations))  # run 20 jobs
        with dsl.ParallelFor(loop_args, parallelism=parallelism) as _:  # On max 10 machines at a time
            function(program_path, image_name, ram, cpus)

    # noinspection PyUnresolvedReferences
    kfp.compiler.Compiler().compile(pipeline, str(program_path.with_suffix(".yaml")))
