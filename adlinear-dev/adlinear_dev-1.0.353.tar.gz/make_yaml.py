from pathlib import Path
from transparentpath import TransparentPath

import kfp.dsl as dsl
import kfp
from kubernetes.client.models import V1Toleration
import argparse


class Output:
    def __init__(self, dirpath: TransparentPath, name: str, suf: str = "", prefix: str = ""):

        if dirpath is None:
            raise ValueError("root directory for outputs can not be None")

        self.dirpath = dirpath
        self.path = None
        attempts = 0
        if prefix != "":
            name = f"{name}_{prefix}"

        if suf != "":
            path = (dirpath / f"{name}_{attempts}").with_suffix(suf)
            while path.is_file():
                if attempts > 1e9:
                    raise ValueError(f"Could not create output file after {attempts} attempts")
                attempts += 1
                path = (dirpath / f"{name}_{attempts}").with_suffix(suf)

            self.path = path
            self.path.touch()
            print(f"Making file {self.path}")
        else:
            path = dirpath / f"{name}_{attempts}"
            while path.is_dir():
                if attempts > 1e9:
                    raise ValueError(f"Could not create output dir after {attempts} attempts")
                attempts += 1
                path = dirpath / f"{name}_{attempts}"

            self.path = path
            (self.path / "locker").touch()
            print(f"Making directory {self.path}")


# noinspection PyUnresolvedReferences
def function(prog, prog_name, image, memory_limit, cpu, items, tag, argnames, preemptible, timeout):
    if "/" not in image:
        image = f"eu.gcr.io/crested-acumen-297311/{image}:{tag}"
    else:
        image = f"{image}:{tag}"

    arguments = [prog]
    for argname in argnames:
        arguments.append(f"--{argname}")
        arguments.append(getattr(items, argname))

    container_op = dsl.ContainerOp(
        name=prog_name,
        image=image,
        command=["python"],
        arguments=arguments,
    )
    # Single job specification
    container_op.add_resource_limit("memory", memory_limit)
    container_op.add_resource_limit("cpu", cpu)
    container_op.add_resource_request("memory", memory_limit)
    container_op.add_resource_request("cpu", cpu)
    if timeout is not None:
        container_op.set_timeout(timeout)
    if preemptible:
        container_op.add_toleration(
            V1Toleration(key="dedicated", operator="Equal", value="standard-preemptible", effect="NoSchedule")
        )
    return container_op


def make_yaml(
    program,
    iterations,
    iterfile,
    image_name,
    parallelism,
    ram,
    cpus,
    suffix,
    root,
    no_out,
    additionnal_args,
    prefix,
    tag,
    preemptible,
    timeout,
):

    if program is None:
        raise ValueError("Program path in docker can not be None")

    program_path = Path(program)
    additionnal_args = {item.split(":")[0]: item.split(":")[1] for item in additionnal_args.split(" ")}
    if iterfile != "":
        iterfile = TransparentPath(iterfile, fs="local")
        if not iterfile.is_file():
            raise FileNotFoundError(f"Could not find iteration file '{iterfile}'")

    if ram != "" and not ram.endswith("G") and not ram.endswith("M"):
        raise ValueError("Malformed RAM argument. Should end by 'G' or 'M'")

    if not isinstance(iterations, int) and iterfile == "":
        raise TypeError("Number of iterations must be an integer")

    if iterations < 0 and iterfile == "":
        raise ValueError("Number of iterations must be greater than 0")

    if image_name == "":
        image_name = program_path.stem

    @dsl.pipeline(name="function")
    def pipeline():
        if iterfile != "":
            iterable = iterfile.read()
        else:
            iterable = [{} for _ in range(iterations)]
        if not no_out:
            TransparentPath.set_global_fs("gcs")  # Needs GOOGLE_APPLICATION_CREDENTIALS
        for item in iterable:
            if not no_out:
                item["output"] = str(Output(TransparentPath(root), program_path.stem, suffix, prefix).path)
            for arg in additionnal_args:
                item[arg] = additionnal_args[arg]
            if "name" in item:
                raise ValueError("The argument 'name' is reserved by KubeFlow, you can not use it asone of your "
                                 "program's arguments")

        argnames = []
        for item in iterable:
            argnames += list(item.keys())
        argnames = set(argnames)
        for item in iterable:
            for argname in argnames:
                if argname not in item:
                    raise ValueError(f"Argument '{argname}' is not present in all your runs arguments.")

        with dsl.ParallelFor(iterable, parallelism=parallelism) as item:  # On max 10 machines at a time
            function(
                str(program_path), program_path.stem, image_name, ram, cpus, item, tag, argnames, preemptible, timeout
            )

    yaml_file = program_path.with_suffix(".yaml").name
    # noinspection PyUnresolvedReferences
    kfp.compiler.Compiler().compile(pipeline, yaml_file)
    print(f"Created {yaml_file} file")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A tool to launch one python program several times in parallel on GCP cluster. The program must "
                    "be in a docker image.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-p", "--program", type=str, default=None, help="The relative path to the program inside the docker image"
    )
    parser.add_argument("-i", "--iterations", type=int, default=1, help="The number of times the program must be ran")
    parser.add_argument(
        "-I",
        "--iterfile",
        type=str,
        default="",
        help="Replaces -i, path to a .json file where each line is a set of arguments to pass to the program. The "
             "program will then be launched once per line. See tests/iterfile.json for an example.",
    )
    parser.add_argument(
        "-m", "--max_executions", type=int, default=15, help="Max number of runs that can exist at a time"
    )
    parser.add_argument(
        "-d",
        "--docker",
        type=str,
        default="",
        help="Docker image to use. Default will be eu.gcr.io/crested-acumen-297311/<program stem>. If only the name "
             "if specified, the image will be eu.gcr.io/crested-acumen-297311/<name>. One can also specify the full "
             "image path, for example 'eu.gcr.io/second-capsule-253207/coucou'.",
    )
    parser.add_argument(
        "-a", "--args", type=str, default="", help="additionnal arguments to pass to the program to run"
    )
    parser.add_argument(
        "-n",
        "--nooutputs",
        action="store_true",
        help="If specified, the program is not supposed to write any file and no random output file will be created",
    )
    parser.add_argument(
        "-r",
        "--root",
        type=str,
        default=None,
        help="Root path where single run output should be stored. Useless if **-n** is passed.",
    )
    parser.add_argument("-R", "--ram", type=str, default="2G", help="Max ram used by one single run")
    parser.add_argument("-c", "--cpu", type=str, default="1", help="Max number of CPUs used by one single run")
    parser.add_argument(
        "-s",
        "--suffix",
        type=str,
        default="",
        help="Suffix of the random named file to store single run output. If '' (default), will create a directory "
             "instead.",
    )
    parser.add_argument("-P", "--prefix", type=str, default="", help="Prefix to put in the program output names")
    parser.add_argument("-t", "--tag", type=str, default="latest", help="Docker image tag")
    parser.add_argument(
        "-k", "--preemptible", action="store_true", help="Tells the program that it can use preemptible VMs"
    )
    parser.add_argument(
        "-T", "--timeout", type=int, default=None, help="Tells one single run to kill itself after a"
                                                        " given time (in seconds) (default = None)"
    )
    args = parser.parse_args()

    make_yaml(
        args.program,
        args.iterations,
        args.iterfile,
        args.docker,
        args.max_executions,
        args.ram,
        args.cpu,
        args.suffix,
        args.root,
        args.nooutputs,
        args.args,
        args.prefix,
        args.tag,
        args.preemptible,
        args.timeout,
    )
