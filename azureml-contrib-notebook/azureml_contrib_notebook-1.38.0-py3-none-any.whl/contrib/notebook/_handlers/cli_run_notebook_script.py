# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Execute notebook with papermill."""
import argparse
import json
import math
import multiprocessing
import os
import papermill as pm
import re
import subprocess
import sys
import traceback
import uuid

from azureml.contrib.notebook import NotebookRunConfig
from azureml.contrib.notebook._cli_run_notebook_handler import CLIRunNotebookHandler
from azureml.contrib.notebook._constants import AZUREML_NOTEBOOK_OUTPUT_PATHS_JSON
from azureml.contrib.notebook._engines._utils import _update_kwargs, _log_scraps_from_notebook
from azureml.core import Run, RunConfiguration
from azureml.core.run import RunStatus

from glob import iglob

try:
    import scrapbook as sb
    _sb = True
except ImportError:
    _sb = False


def init(lock):
    global kernel_create_lock
    kernel_create_lock = lock


def execute_notebook(source_notebook, destination_notebook, infra_args, papermill_args, notebooks_args):
    """Execute notebook with papermill.

    :param source_notebook: Source notebook file name
    :type source_notebook: str
    :param destination_notebook: Source notebook file name
    :type destination_notebook: str
    :param infra_args: Infrastructure arguments
    :type infra_args: dict
    :param papermill_args: Papermill arguments
    :type papermill_args: dict
    :param notebooks_args: Notebook arguments
    :type notebooks_args: dict
    """
    if not destination_notebook:
        destination_notebook = source_notebook + ".output"

    print("Running notebook {}, writing result to {}.".format(source_notebook, destination_notebook))

    # Run in the notebook directory.
    if not papermill_args.get("cwd"):
        papermill_args["cwd"] = os.path.dirname(source_notebook) or "."

    # if kernel name is specified
    kernel_name = papermill_args.get("kernel_name")

    # if not specified try to get it from the notebook
    if not kernel_name:
        with open(source_notebook) as nbfile:
            notebook = json.loads(nbfile.read())
        try:
            kernel_name = notebook.get("metadata").get("kernelspec").get("name")
        except Exception as ex:
            print("Warning: Failed to find kernel in notebook, {}".format(ex))

    # create a kernel spec if not installed
    # If there are multiple processes, creation needs to be locked or it can fail.
    try:
        if kernel_name:
            with kernel_create_lock:
                from jupyter_client.kernelspec import KernelSpecManager
                if not KernelSpecManager().get_all_specs().get(kernel_name):
                    # TODO: replace jupyter_client.kernelspec.KernelSpecManager logic
                    from ipykernel.kernelspec import install
                    install(kernel_name=kernel_name)
                papermill_args["kernel_name"] = kernel_name
    except Exception as ex:
        print("Warning: Failed to create kernel, {}".format(ex))

    papermill_args = _update_kwargs(papermill_args,
                                    input_path=source_notebook,
                                    output_path=destination_notebook,
                                    parameters=notebooks_args)

    # create destination_notebook path if doesn't exist
    if destination_notebook:
        destination_directory = os.path.dirname(destination_notebook)
        if destination_directory:
            os.makedirs(destination_directory, exist_ok=True)

    infra_args["history"] = infra_args.get("history", False) and _sb

    # check if pm<1.0 to skip all the parameters and use defaults
    from pkg_resources import parse_version
    if parse_version("1.0.0") < parse_version(pm.__version__):
        papermill_args = _update_kwargs(papermill_args, **infra_args)
        pm.execute_notebook(**papermill_args)
    else:
        pm.execute_notebook(**papermill_args)
        if infra_args["history"]:
            from azureml.core import Run
            _log_scraps_from_notebook(destination_notebook, Run.get_context())


def execute_notebook_process(notebook_spec, infra_args, papermill_args, notebook_args):
    """Execute notebook with Papermill from inside of a multiprocessing process."""
    clean_process_for_notebook()

    steps = []

    if notebook_spec["preexec"]:
        steps.append({"source": notebook_spec["preexec"]})

    steps.append({"source": notebook_spec["notebook"], "output": notebook_spec["output"]})

    if notebook_spec["postexec"]:
        steps.append({"source": notebook_spec["postexec"]})

    try:
        for step in steps:
            try:
                if step["source"] is None:
                    pass
                elif step["source"].endswith(".py"):
                    step["stdout"] = execute_script(step["source"], [os.path.abspath(notebook_spec["output"])])
                else:
                    execute_notebook(step["source"], step.get("output"), infra_args, papermill_args, notebook_args)
            except subprocess.CalledProcessError as e:
                step["result"] = RunStatus.FAILED
                step["stdout"] = e.output
                step["error"] = traceback.format_exc()
                return notebook_spec, step["error"]
            except Exception:
                step["result"] = RunStatus.FAILED
                step["error"] = traceback.format_exc()
                return notebook_spec, step["error"]

            step["result"] = RunStatus.COMPLETED

        return notebook_spec, None
    finally:
        os.makedirs(os.path.dirname(notebook_spec["report"]) or ".", exist_ok=True)
        with open(notebook_spec["report"], "w") as f:
            json.dump({"steps": steps}, f, indent=4)


def execute_notebooks(source_paths, destination_notebook, destination_directory, infra_args, papermill_args,
                      notebook_args, glob_inputs, child_runs, processes):
    """Execute multiple notebooks in parallel processes or by spawning child runs."""
    run = Run.get_context()
    run_config = RunConfiguration._get_runconfig_using_run_details(run.get_details())

    notebook_specs = get_source_specs(source_paths, glob_inputs)
    print("{} notebooks to execute:".format(len(notebook_specs)))
    print("".join("\t{}\n".format(spec["notebook"]) for spec in notebook_specs))

    generate_output_paths(notebook_specs, destination_notebook, destination_directory)

    if child_runs:
        should_wait_for_children = prepare_for_child_runs(run_config)

        batch_size = int(math.ceil(max(1, len(notebook_specs)) / child_runs))
        child_runs = []
        notebook_run_ids = []

        for i in range(0, len(notebook_specs), batch_size):
            notebook_batch = notebook_specs[i:i + batch_size]

            child_run_id = generate_child_run_id(notebook_batch[0]["notebook"])
            notebook_run_ids += [child_run_id] * len(notebook_batch)

            child_run = spawn_child_run(run, run_config, child_run_id, notebook_batch, infra_args, papermill_args,
                                        notebook_args, processes)
            child_runs.append(child_run)

        log_notebook_paths(notebook_run_ids, notebook_specs)
        finalize_child_runs(child_runs, should_wait_for_children)
    else:
        # Actually execute the notebooks.
        log_notebook_paths([run.id] * len(notebook_specs), notebook_specs)
        write_workspace_config()

        failures = []
        lock = multiprocessing.Lock()

        args = [(spec, infra_args, papermill_args, notebook_args) for spec in notebook_specs]

        # Setting maxtasksperchild=1 means process-level changes by notebooks don't affect subsequent ones.
        with multiprocessing.Pool(processes, initializer=init, initargs=(lock,), maxtasksperchild=1) as pool:
            for spec, error in pool.starmap(execute_notebook_process, args):
                if error:
                    print("Notebook {} failed with exception:\n{}".format(spec["notebook"], error))
                    failures.append((spec["notebook"], error))

        if failures:
            raise Exception("Notebook(s) failed: {}{}".format(
                ", ".join(source for source, _ in failures),
                "".join("\n\nException running {}:\n{}".format(source, error) for source, error in failures)))


def clean_process_for_notebook():
    """
    Remove environment variables that we don't want notebooks to inherit.
    """
    vars_to_remove = [
        "MLFLOW_RUN_ID",
        "MLFLOW_TRACKING_URI"
    ]

    for var in vars_to_remove:
        if var in os.environ:
            del os.environ[var]


def duplicate_ambient_secret(run, run_config):
    """
    Copy the ambient authentication secret, so a parent's cleanup doesn't interfere with the child.

    :param run: The parent run, used for reading/writing the secrets.
    :type run: azureml.core.Run
    :param run_config: A run config object, which will be updated in-place with the new secret name.
    :type run_config: azureml.core.RunConfiguration
    """
    secret_name = run_config.history._ambient_authentication.secret
    new_secret_name = "run-secret-{}".format(uuid.uuid4())

    vault = run.experiment.workspace.get_default_keyvault()
    vault.set_secret(new_secret_name, run.get_secret(secret_name))

    run_config.history._ambient_authentication.secret = new_secret_name


def execute_script(script_path, args):
    """
    Execute a Python script file, throwing if the script fails.

    :param script_path: Path to the .py file.
    :type script_path: str
    :return: Output of the script.
    :rtype: tuple
    """
    print("Running script {}.".format(script_path))

    # Overwrite PYTHONPATH in case it has any relative paths,
    # since we're changing to the script's working directory.
    env = os.environ.copy()
    env["PYTHONPATH"] = (";" if sys.platform == "win32" else ":").join(sys.path)

    script_dir = os.path.dirname(script_path) or "."
    script_file = os.path.basename(script_path)

    result = subprocess.run([sys.executable, script_file, *args], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            cwd=script_dir, check=True, env=env, universal_newlines=True)

    return result.stdout, result.stderr


def finalize_child_runs(child_runs, should_wait_for_children):
    """
    Perform final operations on the created child runs.

    :param child_runs: The child runs just created.
    :type child_runs: list[azureml.core.Run]
    :param should_wait_for_children: Whether to block until all the child runs complete.
    :type should_wait_for_children: bool
    """
    if should_wait_for_children:
        print("Waiting for child runs to complete.")

        for child_run in child_runs:
            child_run.wait_for_completion(wait_post_processing=True, raise_on_error=False)


def generate_child_run_id(notebook):
    """
    Generate a unique but descriptive ID for a child run.

    :param notebook: A notebook file path to incorporate into the run ID.
    :type notebook: str
    :return: A valid and unique run ID.
    :rtype: str
    """
    filename = re.sub(r"[^a-zA-Z0-9_\-]", "-", os.path.basename(notebook))
    return "notebook_{}_{}".format(filename[:200], str(uuid.uuid4())[:8])


def generate_output_paths(notebook_specs, destination_notebook, destination_directory):
    """
    Update notebook_specs with the corresponding output path for each notebook.

    :param notebook_specs: Configuration for each notebook.
    :type notebook_specs: dict
    :param destination_notebook: Exact path to a single output notebook.
    :type destination_notebook: str
    :param destination_directory: Base directory in which to place output notebooks.
    :type destination_directory: str
    """
    if destination_notebook:
        if len(notebook_specs) != 1:
            raise Exception("Cannot provide output file with multiple input files.")

        notebook_specs[0]["output"] = destination_notebook
    else:
        for spec in notebook_specs:
            if not spec.get("output"):
                spec["output"] = os.path.join(destination_directory, spec["notebook"])

    # Uniquify output paths.
    outputs = set()

    for spec in notebook_specs:
        count = 0
        segments = os.path.splitext(spec["output"])

        while spec["output"] in outputs:
            count += 1
            spec["output"] = " ({})".format(count).join(segments)

        outputs.add(spec["output"])

    for spec in notebook_specs:
        if not spec.get("report"):
            spec["report"] = spec["output"] + ".report.json"


def get_source_specs(paths, glob_inputs):
    """
    Convert a path or glob pattern to a list of notebook run specifications.

    :param path: File path, glob pattern, JSON dictionary, or "@" followed by a file path.
    :type path: str
    :param glob_inputs: Whether to applying globbing logic to notebook file paths.
    :type glob_inputs: bool
    :return: Notebook execution specifications, in dictionary form.
    :rtype: list[dict]
    """
    sources = []

    for path in paths:
        if path.startswith("@"):
            # Load a list of sources from a file (so we can process
            # more than would fit in the OS' command line limit).
            with open(path[1:]) as f:
                sources += f.read().splitlines()
        else:
            sources.append(path)

    specs = []

    for source in sources:
        if source:
            try:
                # Direct JSON specification.
                spec = json.loads(source)
                specs.append({
                    "notebook": spec["notebook"],
                    "output": spec.get("output"),
                    "preexec": spec.get("preexec"),
                    "postexec": spec.get("postexec")
                })
            except Exception:
                # Ordinary paths.
                matches = iglob(source, recursive=True) if glob_inputs else [source]
                for match in matches:
                    specs.append({"notebook": match, "output": None, "preexec": None, "postexec": None})

    # Normalize directory separators.
    for spec in specs:
        for attr in ("notebook", "output", "preexec", "postexec"):
            if spec[attr]:
                spec[attr] = spec[attr].replace("\\", "/")

    return specs


def log_notebook_paths(run_ids, notebook_specs):
    """
    Dump all the notebook execution specifications to a JSON file.

    :param run_ids: The run IDs in which each notebook is executing.
    :type run_ids: list[str]
    :param notebook_specs: Notebook execution specifications.
    :type notebook_specs: list[dict]
    """
    with open(os.path.join("outputs", AZUREML_NOTEBOOK_OUTPUT_PATHS_JSON), "w") as f:
        json.dump([{"run_id": run_id, **spec} for run_id, spec in zip(run_ids, notebook_specs)], f, indent=4)


def prepare_for_child_runs(run_config):
    """
    Modify run_config and setup the environment for spawning child runs.

    :param run_config: The parent run configuration to be modified in-place for child runs.
    :type run_config: azureml.core.RunConfiguration
    """
    # Local Docker runs aren't able to spawn more Docker runs, so make them
    # local non-Docker runs (but still inside the parent Docker container).
    if run_config.target == "local" and run_config.environment.docker.enabled:
        run_config.environment.docker.enabled = False
        run_config.environment.python.user_managed_dependencies = True
        should_wait_for_children = True
    else:
        should_wait_for_children = False

    # Don't send our run data to child runs.
    with open(".amlignore", "a") as amlignore:
        for path in ["", "azureml-logs", "azureml-setup", "azureml_compute_logs", "logs", "outputs"]:
            print(path, file=amlignore)

    return should_wait_for_children


def spawn_child_run(run, run_config, child_run_id, notebook_specs, infra_args, papermill_args, notebook_args,
                    processes):
    """
    Create a child run to asynchronously execute a set of notebooks.

    :param run: The current (parent) run.
    :type run: azureml.core.Run
    :param run_config: Run configuration to be used for the new child run.
    :type run_config: azureml.core.RunConfiguration
    :param child_run_id: Run ID to be used for the new child run.
    :type child_run_id: str
    :param notebook_specs: Specifications for the notebooks to execute in the child run.
    :type notebook_specs: list[dict]
    :param infra_args: Arguments passed to the notebook execution engine.
    :type infra_args: dict
    :param papermill_args: Arguments passed to the notebook handler.
    :type papermill_args: dict
    :param notebook_args: Arguments injected into the notebook itself.
    :type notebook_args: dict
    :param processes: Number of parallel processes to use for executing notebooks.
    :type processes: int
    :return: The new child run.
    :rtype: azureml.core.Run
    """
    # Send the batch of inputs and parameters to the child.
    child_inputs_file = "{}_inputs.txt".format(child_run_id)
    with open(child_inputs_file, "w") as f:
        for spec in notebook_specs:
            print(json.dumps(spec), file=f)

    handler_args = {k: v for k, v in papermill_args.items() if k != "engine_name"}

    handler = CLIRunNotebookHandler(output_directory="outputs",
                                    processes=processes,
                                    **handler_args,
                                    **infra_args)

    if run_config.history._ambient_authentication and \
            run_config.history._ambient_authentication.delete_secret_after_run:
        duplicate_ambient_secret(run, run_config)

    notebook_run_config = NotebookRunConfig(source_directory=".",
                                            notebook="@{}".format(child_inputs_file),
                                            parameters=notebook_args,
                                            handler=handler,
                                            run_config=run_config)

    child_run = run.submit_child(notebook_run_config, run_id=child_run_id)

    print("Notebooks submitted to child run {}:".format(child_run.id))
    print("".join("\t{}\n".format(spec["notebook"]) for spec in notebook_specs))

    return child_run


def write_workspace_config():
    """Try to get workspace context and save config to disk.

    Workspace config and Vienna run token should be sufficient to load context in a user script.
    """
    try:
        from azureml.core import Run
        workspace = Run.get_context().experiment.workspace
        workspace.write_config()
    except Exception:
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input", action="append", required=True,
                        help="input notebook")
    parser.add_argument("-e", "--execution_args", default="",
                        help="execution options")
    parser.add_argument("-p", "--papermill_args", default="",
                        help="papermill arguments")
    parser.add_argument("-n", "--notebook_args", default="",
                        help="notebook parameters")
    parser.add_argument("-g", "--glob-input-paths", action="store_true",
                        help="Treat input notebook paths as glob patterns.")
    parser.add_argument("-c", "--child-runs", type=int, default=None,
                        help="Split notebook execution across N child runs.")
    parser.add_argument("--processes", type=int, default=1,
                        help="Run notebooks across N parallel processes.")

    out_group = parser.add_mutually_exclusive_group()
    out_group.add_argument("-o", "--output",
                           help="output notebook")
    out_group.add_argument("-d", "--output-directory",
                           help="Output directory.")

    args = parser.parse_args()

    execute_notebooks(args.input,
                      args.output,
                      args.output_directory,
                      json.loads(args.execution_args),
                      json.loads(args.papermill_args),
                      json.loads(args.notebook_args),
                      args.glob_input_paths,
                      args.child_runs,
                      args.processes)
