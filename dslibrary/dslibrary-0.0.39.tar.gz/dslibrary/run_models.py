"""
Run a model.
"""
import json
import inspect
import os
import typing
import subprocess
import sys
import tempfile
import pandas

from pexpect import split_command_line

import dslibrary
from dslibrary import ENV_DSLIBRARY_TOKEN
from dslibrary.front import DSLibraryException, ENV_DSLIBRARY_TARGET, ENV_DSLIBRARY_SPEC, METRICS_ALIAS
from dslibrary.metadata import Metadata


class ModelRunner(object):
    """
    Each instance sets up for one run of one model.
    """
    def __init__(self, uri: str=None, user: str=None, run_id: str=None, project_root: str=None, entry_point: str = "main", mlflow: (bool, dict)=None, parameters: dict=None):
        """
        The constructor provides some context which is optional when directly invoking local code, and required
        when invoking code remotely.

        :param uri:             Unique identifier for the model.
        :param user:            Which user is running the model.
        :param run_id:          Run ID needs to be specified when running in MLFlow.
        :param entry_point:     Which entry point is being called.
        :param mlflow:          MLFlow-related settings.  True = send all to mlflow, {} = send some calls to mlflow.
        """
        self.uri = uri or ""
        self.user = user or ""
        self.run_id = run_id or ""
        self.project_root = project_root
        self.entry_point = entry_point
        self.mlflow = mlflow if isinstance(mlflow, dict) else {"all": True} if mlflow is True else {}
        self.inputs = {}
        self.outputs = {}
        self.data = {}
        self.parameters = parameters or {}
        self.code_paths = []

    def _to_absolute(self, uri: str):
        """
        Convert local paths to absolute paths except when they match a certain pattern.  "~" signifies the
        model's root path and can be used to access built-in model data.
        """
        # TODO consider self.project_root
        # TODO test this
        # blank > means no change to supplied name
        if not uri:
            return ""
        # no changes to URIs
        if ":" in uri:
            return uri
        if uri.startswith("~/"):
            # specifically point to files within the sandbox
            return "./" + uri[1:]
        if uri.startswith("/"):
            # already absolute
            return uri
        # convert to absolute path
        return os.path.abspath(uri)

    def set_input(self, name: str, uri: str="", data=None, **kwargs):
        """
        Specify where data will come from for a particular named input.
        :param name:    Name of input.
        :param uri:     A path to a local file, or the URI of remote data.  Or, a URI specifying a sql or nosql data
                        source.
        :param data:    Specific in-memory data can be supplied when running locally.
        :param kwargs:  Additional parameters to support the various data sources, following fsspec for file-like
                        sources.
        """
        self.inputs[name] = {"uri": self._to_absolute(uri), **kwargs}
        if data is not None:
            self.data[name] = data
        return self

    def set_output(self, name: str, uri: str="", capture: bool=False, **kwargs):
        """
        Specify where data should go for a particular named output.

        A format can be chosen by specifying "format".
          csv or tab -- remaining arguments are sent to pandas.to_csv()
          json - remaining arguments are sent to pandas.to_json()
          etc.

        :param name:    Name of output.
        :param uri:     See set_input()
        :param capture: Output content from write_resource() can be captured in memory.
        :param kwargs:  See set_input()
        """
        spec = {"uri": self._to_absolute(uri), **kwargs}
        self.outputs[name] = spec
        if capture:
            spec["capture"] = True
        return self

    def set_parameter(self, name: str, value):
        """
        Specify a value for one of the parameters.
        """
        self.parameters[name] = value
        return self

    def set_parameters(self, params: dict):
        """
        Specify values for multiple parameters.
        """
        self.parameters.update(params)
        return self

    def add_code_path(self, path: str):
        """
        Point to a location where import modules might exist.
        :param path:   Path to a folder containing python code to import from your model.
        """
        if path not in self.code_paths:
            self.code_paths.append(path)
        return self

    def send_metrics_to(self, uri: str=None, mlflow: bool=None, capture: bool=False, **kwargs):
        """
        Determine where metrics will be stored (for read and write).  Parameters are equivalent to set_output(), in
        that metrics can be sent to a particular location.

        :param uri:         A URI or filename.
        :param mlflow:      Specify True to have the model log its metrics through MLFlow.
        :param kwargs:      Additional arguments.
        """
        if mlflow is not None:
            self.mlflow["metrics"] = bool(mlflow)
        self.inputs[METRICS_ALIAS] = {**kwargs}
        self.outputs[METRICS_ALIAS] = {**kwargs}
        if uri:
            self.inputs[METRICS_ALIAS]["uri"] = uri
            self.outputs[METRICS_ALIAS]["uri"] = uri
        if capture:
            self.outputs[METRICS_ALIAS]["capture"] = True
        return self

    def _generate_spec(self, local: bool=False):
        spec = {
            "uri": self.uri,
            "user": self.user,
            "run_id": self.run_id,
            "entry_point": self.entry_point,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "parameters": self.parameters,
            "code_paths": self.code_paths
        }
        if self.data and local:
            spec["data"] = self.data
        if self.mlflow:
            spec["mlflow"] = self.mlflow
        return spec

    def run_method(self, method: typing.Callable, path: str=None):
        """
        As long as 'method()' uses dslibrary.instance(), and all calls through this method are single threaded, you can
        use this method, and it is very efficient.
        """
        # map parameters to method signature
        call_kwargs = {}
        sig = inspect.signature(method)
        sig_kwargs = None
        remaining_params = dict(self.parameters)
        for p_name, param in sig.parameters.items():
            if param.kind == inspect.Parameter.VAR_KEYWORD:
                sig_kwargs = True
                continue
            if p_name in remaining_params:
                value = remaining_params.pop(p_name)
                if param.annotation and param.annotation is not inspect.Parameter.empty:
                    value = param.annotation(value)
                call_kwargs[p_name] = value
        if sig_kwargs:
            call_kwargs.update(remaining_params)
        # as long as the method lets us send a custom dslibrary instance we can do that
        if "dsl" in sig.parameters or "dslibrary" in sig.parameters:
            run_env = self.prepare_run_env(local_path=path, local=True)
            dsl = dslibrary.instance(run_env)
            call_kwargs["dsl" if "dsl" in sig.parameters else "dslibrary"] = dsl
            retval = method(**call_kwargs)
        else:
            # otherwise we assume method() calls dslibrary.instance()
            # - this approach is not thread safe
            # TODO is this approach even worth supporting???
            run_env = self.prepare_run_env(local_path=path, local=False)
            dsl = dslibrary
            orig_env = {ENV_DSLIBRARY_TARGET: os.environ.get(ENV_DSLIBRARY_TARGET), ENV_DSLIBRARY_SPEC: os.environ.get(ENV_DSLIBRARY_SPEC)}
            try:
                # store specification
                for k, v in run_env.items():
                    os.environ[k] = v or ""
                # the method makes calls to dslibrary, following rules set above
                retval = method(**call_kwargs)
            finally:
                # restore environment
                for k, v in orig_env.items():
                    os.environ[k] = v or ""
        # we return captured data, in case there is any, and it replaces the method return value
        if hasattr(dsl, "_spec"):
            captured = dsl._spec.get("capture")
            if captured:
                retval = captured
        return retval

    def run_local(self, path: str, entry_point: str=None, extra_env: dict=None):
        """
        Execute a python, R or notebook based model in a subprocess.
        """
        # if project_root is specified, 'path' is relative to it, by default
        path = path or ""
        if self.project_root and not path.startswith("/"):
            path = os.path.join(self.project_root, path)
        # verify target exists, split apart path
        if not os.path.exists(path):
            raise DSLibraryException(f"Path not found: {path}")
        # if a folder has been specified we have to look up 'entry_point' and run its official command
        cmd = None
        if not path or os.path.isdir(path):
            folder = self.project_root or path or "."
            meta = Metadata.from_folder(folder)
            entry_point = entry_point or self.entry_point or "main"
            if entry_point not in meta.entry_points:
                raise DSLibraryException(f"Entry point {entry_point} not found in model at {path}")
            cmd_str = meta.entry_points[entry_point].command
            if not cmd_str:
                raise DSLibraryException(f"Entry point {entry_point} for {path} does not define a command")
            cmd = split_command_line(cmd_str)
            # insert venv here as well (if 'python' is the command used)
            if cmd and cmd[0] == "python":
                venv_py = self.find_venv_python(folder)
                if venv_py:
                    cmd[0] = venv_py
        else:
            folder = self.project_root or os.path.split(path)[0] or "."
        # if we're not using metadata we have to infer how to execute the code
        if not cmd:
            cmd = self.infer_command_from_path(path)
        # convert in-memory data to files
        temp_files = []
        for resource_name, data in self.data.items():
            with tempfile.NamedTemporaryFile(delete=False) as f_w:
                if hasattr(data, "to_csv"):
                    data.to_csv(f_w, sep="\t", index=False)
                # TODO don't clobber self.inputs, this should be strictly temporary
                self.inputs[resource_name]["uri"] = f_w.name
                self.inputs[resource_name]["format"] = "csv"
                self.inputs[resource_name]["format_options"] = {"delimiter": "\t"}
                temp_files.append(f_w.name)
        # when capturing outputs, redirect to temporary file
        output_capture_files = {}
        for resource_name, spec in self.outputs.items():
            if spec.get("capture"):
                tmp_fn = tempfile.NamedTemporaryFile(delete=True).name
                temp_files.append(tmp_fn)
                # TODO don't clobber this either
                spec["capture"] = False
                spec["uri"] = output_capture_files[resource_name] = tmp_fn
                spec["format"] = "csv"
                spec["format_options"] = {"sep": "\t"}
        # work out environment variables
        env = {
            **self.prepare_run_env(local_path=folder),
            **(extra_env or {})
        }
        # call the model
        # TODO report failures in a more elegant way
        subprocess.run(cmd, cwd=folder, env=env, check=True)
        # capture outputs
        outputs = None
        for resource_name, filename in output_capture_files.items():
            if not os.path.exists(filename):
                continue
            if not outputs:
                outputs = {}
            # TODO output might not be a dataframe
            outputs[resource_name] = pandas.read_csv(filename, sep="\t")
        # convert captured metrics from dataframe to dict
        if outputs and METRICS_ALIAS in outputs:
            metrics = {}
            for _, row in outputs[METRICS_ALIAS].iterrows():
                metrics[row["name"]] = row.value
            outputs[METRICS_ALIAS] = metrics
        # delete temporary files for self.data and captured outputs
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        # return captured output
        return outputs

    @staticmethod
    def find_venv_python(folder: str):
        venv_py = os.path.join(folder, "venv", "bin", "python")
        if not os.path.exists(venv_py):
            return
        return venv_py

    @staticmethod
    def infer_command_from_path(path: str):
        """
        When we only know the name of a source file we have to work out how to execute it.

        Used by run_local().
        """
        folder, fn = os.path.split(path)
        _, f_ext = os.path.splitext(fn)
        f_ext = f_ext.lower()
        # detect virtual environment
        # TODO 'path' is not the best place to get 'folder'
        venv_py = ModelRunner.find_venv_python(folder)
        # if we're not using metadata we have to infer how to execute the code
        if f_ext == ".py":
            cmd = [venv_py or sys.executable, path]
        elif f_ext == ".r":
            # TODO detect venv for R
            cmd = ["RScript", path]
        elif f_ext == ".ipynb":
            # FIXME apply venv_py here!
            cmd = ["nbconvert", "--to", "notebook", "--execute", "--inplace", path]
        else:
            raise DSLibraryException(f"unrecognized executable extension: {f_ext} in {fn}")
        return cmd

    def prepare_run_env(self, rest_url: str=None, shared_volume: str=None, local_path: str=None, rest_access_token: str=None, local: bool=False) -> dict:
        """
        Prepare environment variables for a run which encapsulate all of the settings generated by calls to this
        class.  Data science code running anywhere, with these environment variables set, can use dslibrary to read
        and write all of its data without having to know any details about data location, credentials or format.

        Three approaches are provided:
          * rest_url and rest_access_token - fill this in to have the target code use a REST service for data access.
          * shared_volume - fill this in to use a shared volume (i.e. a sidecar) for data access.
          * local_path - this option causes all inputs and outputs to default to files in the indicated folder, and
              there is no delegation of data access, it is all performed by the process running the target code.

        In a high security scenario which isolates the data science code from the credentials and other data source
        details:
          * Send the ENV_DSLIBRARY_SPEC value to a secure service (a REST service indicated by rest_uri, or a sidecar
            sharing the volume 'shared_volume' with the target code).
          * Send the other environment variables to the target code.
          * The target code calls dslibrary methods, which communicate with the data service, and the data service
            performs all reads and writes based on the environment data it has been sent.

        The Kubernetes sidecar approach involves running a container alongside your target code's container, and having
        them both mount the same shared, ephemeral volume.  The appropriate environment variables are set for each, and
        voila, the target code is able to perform all its data access without having exposed any sensitive information.

        :param rest_url:            URL of REST service.
        :param shared_volume:       Path to shared volume.
        :param local_path:          Local path.
        :param rest_access_token:   Access token to secure communications.
        :return:  Environment variables to set, as a {}.
        """
        env = {}
        if shared_volume:
            env[ENV_DSLIBRARY_TARGET] = f"volume:{shared_volume}"
        elif rest_url:
            env[ENV_DSLIBRARY_TARGET] = rest_url
            if rest_access_token:
                env[ENV_DSLIBRARY_TOKEN] = rest_access_token
        elif local_path:
            env[ENV_DSLIBRARY_TARGET] = f"local:{local_path}"
        spec = self._generate_spec(local)
        env[ENV_DSLIBRARY_SPEC] = spec if local else json.dumps(spec)
        return env

    def run_mlflow(self, model_uri: str):
        """
        Use mlflow.run() to execute an MLFlow model.

        The trick will be how to set the environment variables in the remote model such that the interception takes
        place and sends data back to us.  Could initially only be supported when running locally with an environment
        variable.
        """
        # TODO code me
        # TODO I don't see a way to have MLFlow deliver extra environment variables!
