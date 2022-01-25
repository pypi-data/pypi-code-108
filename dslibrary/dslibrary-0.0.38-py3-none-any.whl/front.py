"""
The model-facing side of this API.
"""
import io
import json
import jsonschema
import os
import pickle
import uuid
import sys
import pandas
import numpy
import time
import typing
import tempfile
from collections import namedtuple
import yaml
import warnings
import urllib.parse
import shutil

from .exceptions import DSLibraryDataFormatException, DSLibraryException
from .engine_intf import GenericStreamWrapper, BytesIOWrapper
from .proto_handlers import load_protocol_handler
from .utils.connect import connect_to_database, dataframe_to_sql
from .utils.dbconn import sql_enquote_id
from .utils.file_utils import write_stream_with_read_on_close, connect_to_filesystem
from .utils.format_sniffer import find_url_extension, detect_format
from .utils.nosql import connect_to_nosql
from .utils.packages import install_packages

try:
    import mlflow
except ImportError:
    mlflow = None

try:
    import dask.dataframe
except ImportError:
    dask = None

from .metadata import Metadata

# this environment variable says how DSLibrary should be implemented
ENV_DSLIBRARY_TARGET = "DSLIBRARY_TARGET"
# this one provides a JSON specification indicating all the parameters and where the data should be channeled
ENV_DSLIBRARY_SPEC = "DSLIBRARY_SPEC"
# this one is used to provide authentication when communicating with a remote REST service
ENV_DSLIBRARY_TOKEN = "DSLIBRARY_TOKEN"

# use this as the name of an input or output to access metrics
METRICS_ALIAS = "__metrics__"
# use this to specify where parameters are logged
PARAMS_ALIAS = "__params__"
# pass/fail signal from model evaluation actions
EVALUATION_RESULT_ALIAS = "__evaluation_result__"


class DSLibrary(object):
    """
    Base class for all dslibrary implementations.
    """
    # internal representation of a stored metric
    Metric = namedtuple("Metric", "run_id uri user time name value step")

    def __init__(self, spec: dict=None, _env: dict=None):
        """
        :param spec:    See RunModel for a description of (and a generator for) the specification.  It provides
                        parameter values, and says where input and output data should go, what file format to use, and
                        other details of the context in which the model is operating, like whether to delegate any
                        methods to MLFlow.
        """
        self._params = None
        self._spec = spec or {}
        self._env = _env
        spec_wo_data = dict(self._spec)
        spec_wo_data.pop("data", None)
        jsonschema.validate(spec_wo_data, LOCAL_SPECS_SCHEMA)
        self._run_id = self._spec.get("run_id") or ""
        self._mlflow_opts = self._spec.get("mlflow") or {}
        self._mlflow_all = self._mlflow_opts.get("all")
        self._mlflow_metrics = self._mlflow_opts.get("metrics") or self._mlflow_all
        if self._mlflow_opts and not mlflow:
            raise DSLibraryException("MLFlow was selected for output but the mlflow package is not installed")
        self._mlflow_run = None
        self._setup_code_paths()

    def _setup_code_paths(self):
        """
        A list of folders containing required modules can be specified.
        """
        # set up code paths - locations of required source files
        for path in self._spec.get("code_paths") or []:
            if path not in sys.path:
                sys.path.append(path)

    def _xlt_resource(self, resource_name: str, _mode: str="inputs", **kwargs):
        """
        Look up specifications for a named input or output and use those to override supplied defaults.
        :param resource_name:   Named input.
        :param kwargs:          Defaults.
        :return:    A tuple with (0) the URI, and (1) the final set of options
        """
        resource_spec = (self._spec.get(_mode) or {}).get(resource_name) or {}
        kwargs.update(resource_spec)
        uri = kwargs.pop("uri", None) or resource_name
        return uri, kwargs

    def get_metadata(self) -> Metadata:
        """
        Load self-descriptive metadata for this model.  Contains information about parameters, inputs, & outputs.
        Similar to (and aspirationally compatible with) content of mlflow's MLProject file.

        This information would normally come from the model code package itself, but subclasses are free to source it
        from wherever they like.

        The main points covered by the metadata are:
          * entry points - a model can have multiple actions that it can perform, such as training or prediction, and
                most models have a default ('main') action.  Each entry point is associated with a command that can be
                executed, generally involving some source code that is part of the model.
          * parameter names and types - each entry point may have parameters, and the model is made more usable when
                the names and types of those parameters are known without digging into the code.  They can be validated,
                defaults can be filled in, and so on.
          * input and output schemas - each entry point will generally read or write columnar data, and that data will
                usually have some rules, like required columns that must be present, or expected column types.
                Documenting these allows the surrounding infrastructure to ensure that these rules are followed.
        """
        return Metadata()

    def get_parameters(self):
        """
        Parameter values come from supplied specifications (see constructor), or if omitted, we fall back to the command
        line.
        """
        if self._params is None:
            # check local specifications, then check environment and command line
            params = self._spec.get("parameters")
            # fall back to CLI parameters
            if params is None:
                params = self._scan_cli_parameters()
            # fill in defaults, perform type coercion, do additional validation
            metadata = self.get_metadata()
            entry_point = metadata.entry_points.get(self._spec.get("entry_point") or "main")
            if entry_point:
                for param_name, param_props in entry_point.parameters.items():
                    params[param_name] = param_props.process_value(params.get(param_name))
            # cache the parameter values
            self._params = params
        return self._params

    def _scan_cli_parameters(self) -> dict:
        """
        Load parameters from the command line.
        """
        args = {}
        param_next = None
        for arg in sys.argv:
            if param_next:
                v = arg
                if v.isdigit():
                    v = float(v)
                args[param_next] = v
                param_next = None
            elif arg.startswith("--") and arg[2:]:
                if '=' in arg:
                    k, v = arg[2:].split('=', maxsplit=1)
                    if v.isdigit():
                        v = float(v)
                    args[k] = v
                else:
                    param_next = arg[2:]
        return args

    def get_parameter(self, parameter_name: str, default=None):
        """
        Get a defined parameter.  Returns (default) if not defined.
        """
        return self.get_parameters().get(parameter_name, default)

    def get_uri(self) -> str:
        """
        Returns a URI that identifies the model which is currently running.  This is an identifier for a particular
        model or piece of executable code, not for a particular execution of the code.
        """
        # TODO this is given in the metadata but can also be specified in the specification, which is confusing.
        #  - MLFlow assumes it can access a model's project data based on a URI, which makes it seem awkward to expect
        #    it in the metadata file.
        return self.get_metadata().uri or self._spec.get("uri") or ""

    def _opener(self, path: str, mode: str, **kwargs) -> io.RawIOBase:
        """
        Open files.  Derived classes fill this in with a means of opening read or write streams.  It should ensure the
        filename is within allowed bounds for the model, i.e. "../" and "/..." are only allowed in some cases.

        :param path:    Path to file, or URI of file.
        :param mode:    Open mode (r, rb, w, wb, a, ab)
        :param kwargs:  Additional arguments to customize details of the operation.
        :return:    File-like object.  FileNotFoundError if not found for read.
        """
        raise DSLibraryException("base class called")

    def open_resource(self, resource_name: str, mode: str='rb', **kwargs) -> io.RawIOBase:
        """
        Open a stream to or from a named file-like source/destination, or from a URI.  Each input and output should be
        given a name.  The caller selects particular data sources and associates them with these names.  The burden of
        indicating file format details is on the caller.

        A good practice is to specify a logical name in 'resource_name', and provide a default uri in 'uri'.

        NOTES:
          * Inputs and outputs may be segregated: writing to an output named 'x' may have no effect on the input
            named 'x'.
          * Not all file sources support append mode (i.e. s3 buckets).

        :param resource_name:   The path or URI indicating which resource to access.
            * Names starting with './' are treated as local files.
            * Names starting with 'http://', 'https://', 's3://', etc., are treated as URIs of external resources.
            * All other names are expected to match an input or output defined in the metadata.

        :param mode:            File read/write/append mode: 'r', 'rb', 'w', 'wb', 'a', 'ab'

        :param kwargs:      Additional arguments:
                                filesystem = opens the file through a named external filesystem engine

        :returns:       A file-like object.
        """
        uri, open_args = self._xlt_resource(resource_name, _mode="inputs" if "r" in mode else "outputs", **kwargs)
        # remove formatting arguments, etc.
        open_args.pop("format", None)
        open_args.pop("format_options", None)
        open_args.pop("dask", None)
        # send all outputs to mlflow if requested
        use_mlflow = self._mlflow_all and ("w" in mode or "a" in mode)
        if use_mlflow:
            if "a" in mode:
                raise DSLibraryException("Append mode not available with mlflow output")
            return write_stream_with_read_on_close(w_mode=mode, r_mode='r', on_close=lambda fh: mlflow.log_artifact(fh.name, uri))
        # check for a custom protocol handler
        proto_handler = load_protocol_handler(uri, env=self._env)
        if proto_handler:
            return proto_handler.open_resource(uri, mode, **open_args)
        # data can be requested through a named filesystem engine/provider
        filesystem = kwargs.get("filesystem")
        if filesystem:
            open_args.pop("filesystem", None)
            fs = self.get_filesystem_connection(filesystem, for_write="r" not in mode, **open_args)
            # TODO some of 'open_args' might be appropriate to send to open() below rather than get_filesystem_connection(), above
            return fs.open(uri, mode=mode)
        # 'path' has the URI or path of what we need to open
        # 'mode' has the open mode
        # 'open_args' has additional arguments to pass
        return self._opener(uri, mode, **open_args)

    def open_model_binary(self, part: str=None, mode: str='rb') -> io.RawIOBase:
        """
        Read or write to the main model data store for the current model.  If there is just one piece of data, like
        a pickled sklearn model, omit the 'part' argument.  If there are multiple parts, 'part' indicates which one
        to access.

        Reading from this file would be the normal operation when making a prediction.  Writing to this file implies
        a training operation.
        """
        return self.open_resource(f"model-binary/{part}" if part else "model-binary", mode=mode)

    def open_run_data(self, filename: str, mode: str='rb', **kwargs) -> io.RawIOBase:
        """
        Open a stream to or from file-like storage which is local to the current pipeline execution context.

        One model can write to a 'file' in this context, and another can read from that file, provided they are part
        of the same pipeline.
        """
        raise DSLibraryException("open_run_data() is not supported by the selected implementation")

    def set_evaluation_result(self, success: bool, **kwargs) -> None:
        """
        Signal the completion of an evaluation operation, indicating whether it succeeded, and supplying an optional
        message.
        """
        self.log_dict({"uri": self.get_uri(), "success": success, **kwargs}, EVALUATION_RESULT_ALIAS)

    def _get_system_connection(self, system_type, resource_name: str, for_write: bool=False, **kwargs):
        """
        Access all types of external system connections.
        :param system_type:         See methods below.
        :param resource_name:       Named input or output, or URI.
        :param for_write:           Request write access.
        :param kwargs:              Custom arguments.
        :return:        An engine implementation, the type of which depends on the requested system_type.
                        See 'engine_intf'.
        """
        # translate 'resource_name' based on supplied specification and overriding supplied arguments
        uri, kwargs = self._xlt_resource(resource_name, "outputs" if for_write else "inputs", **kwargs)
        handler = load_protocol_handler(uri, env=self._env)
        if handler:
            return handler.get_system_connection(system_type, uri=resource_name, for_write=for_write, **kwargs)
        if system_type == "filesystem":
            return connect_to_filesystem(uri=uri, for_write=for_write, **kwargs)
        if system_type == "sql":
            library = kwargs.pop("library", None)
            return connect_to_database(uri=uri, library=library, for_write=for_write, **kwargs)
        if system_type == "nosql":
            library = kwargs.pop("library", None)
            return connect_to_nosql(uri=uri, library=library, for_write=for_write, **kwargs)
        raise ValueError(f"Unsupported system_type: {system_type}")

    def get_filesystem_connection(self, resource_name: str, for_write: bool=False, **kwargs):
        """
        Returns a FileSystem class for a given external filesystem, like s3, abs, gcs, etc..  See engine_intf.FileSystem,
        which is a simplified version of fsspec.AbstractFileSystem.

        :param resource_name:   Which filesystem to access.  This can be the name of an input or output resource, or a
                                URI providing connection details.
        :param for_write:       True to enable write operations.
        :param kwargs:      Additional arguments, including...
                bucket = named bucket within the filesystem provider/engine.
                read_only = restricts to read operations
        """
        return self._get_system_connection("filesystem", resource_name, for_write, **kwargs)

    def get_sql_connection(self, resource_name: str, for_write: bool=False, **kwargs):
        """
        Returns a DBI-compatible connection object which can be used to communicate with a relational database.

        :param resource_name:   Which database to access.  This can be the name of an input or output resource, or a
                                URI referencing an external data source.
        :param for_write:       True to enable write operations.
        """
        return self._get_system_connection("sql", resource_name, for_write, **kwargs)

    def get_nosql_connection(self, resource_name: str, for_write: bool=False, **kwargs):
        """
        Returns a connection to a NoSQL database, as an interface that abstracts the functionality of a range of
        popular NoSQL engines.

        :param resource_name:   Which database to access.  This can be the name of an input or output resource, or a
                                URI referencing an external data source.
        :param for_write:       True to enable write operations.
        """
        return self._get_system_connection("nosql", resource_name, for_write, **kwargs)

    def log_param(self, key: str, value):
        """
        Log a supplied parameter.
        """
        use_mlflow = self._mlflow_opts.get("params") or self._mlflow_all
        if use_mlflow:
            mlflow.log_param(key, value)
            return
        row = {
            "uri": self.get_uri(),
            "run_id": self._spec.get("run_id") or "",
            "user": self._spec.get("user") or "",
            "time": time.time(),
            "name": key,
            "value": value
        }
        df = pandas.DataFrame(data=[row])
        self.write_resource(PARAMS_ALIAS, df, append=True)

    def log_params(self, params: dict):
        """
        Log multiple parameters (if enabled).
        """
        for k, v in params.items():
            self.log_param(k, v)

    def log_metric(self, metric_name: str, metric_value: float, step: int=0) -> None:
        """
        Save a piece of trackable information about this run.
        """
        if self._mlflow_metrics or self._mlflow_all:
            if mlflow:
                mlflow.log_metric(metric_name, metric_value, step)
            return
        if self._capturing_output(METRICS_ALIAS):
            # captured metrics only return a name and value
            if "capture" not in self._spec:
                self._spec["capture"] = {}
            if METRICS_ALIAS not in self._spec["capture"]:
                self._spec["capture"][METRICS_ALIAS] = {}
            self._spec["capture"][METRICS_ALIAS][metric_name] = metric_value
        else:
            # full metrics output
            row = {
                "uri": self.get_uri(),
                "run_id": self._spec.get("run_id") or "",
                "user": self._spec.get("user") or "",
                "time": time.time(),
                "name": metric_name,
                "value": metric_value,
                "step": step
            }
            df = pandas.DataFrame(data=[row])
            self.write_resource(METRICS_ALIAS, df, append=True)

    def log_metrics(self, metrics: dict, step: int=0) -> None:
        """
        Save multiple metrics.
        """
        for k, v in (metrics or {}).items():
            self.log_metric(k, v, step)

    def get_metrics(self, metric_name: str = None, uri: str = None, time_range: (list, tuple) = None, limit: int = None):
        """
        Retrieve the values of previously stored metrics as a dataframe.  Implementations might limit which metrics are returned
        based on security policies.  Sort order should be by time, descending.

        :param metric_name:     Limits results to a particular named metric.
        :param uri:             Limits results to a particular project, pipeline or model.
        :param time_range:      Limits results to a time range.  Supply two numeric values (or None), for start and
                                end of the time range, respectively.
        :param limit:           Maximum number of results to return.
        :returns:   An iterable of records (type 'Metric') describing each metric.
        """
        use_mlflow = self._mlflow_opts.get("metrics") or self._mlflow_all
        if use_mlflow:
            # TODO to support this would require creating a client, using the run ID to look them up, etc.
            raise DSLibraryException("Access to metrics in mlflow is not supported at this time.")
        # load metrics
        df = self.load_dataframe(METRICS_ALIAS)
        # filter by criteria, sort most recent first, limit to requested number of samples
        if time_range:
            df = df[time_range[0] <= df.time < time_range[1]]
        if uri:
            df = df[df.uri == uri]
        if metric_name:
            df = df[df.name == metric_name]
        df.sort_values(by=["time"], ascending=False)
        if limit:
            df = df.head(limit)
        return df

    def get_last_metric(self, metric_name: str):
        """
        Get the most recently saved metric of the given name for the current model.
        """
        metrics = self.get_metrics(metric_name, uri=self.get_uri(), limit=1)
        if metrics.shape[0]:
            row = metrics.iloc[0]
            return DSLibrary.Metric(**row)

    def log_text(self, text: str, artifact_file: str):
        """
        Log textual data as a run artifact / output.
        """
        self.write_resource(artifact_file, text)

    def log_dict(self, dictionary: dict, artifact_file: str):
        """
        Log JSON or YAML data.
        :param dictionary:
        :param artifact_file:
        """
        use_mlflow = self._mlflow_all
        if use_mlflow:
            mlflow.log_dict(dictionary, artifact_file)
        else:
            self.write_resource(artifact_file, content=dictionary)

    def log_artifact(self, local_path: str, artifact_path: str):
        """
        Send a file as a result from a model run.
        :param local_path:      Local file to send.
        :param artifact_path:   Filename for result file.
        """
        use_mlflow = self._mlflow_all
        if use_mlflow:
            mlflow.log_artifact(local_path, artifact_path)
        else:
            self.write_resource(artifact_path, from_filename=local_path)

    def log_artifacts(self, local_dir, artifact_path: str):
        """
        Send a whole folder.
        """
        for f in os.listdir(local_dir):
            self.log_artifact(os.path.join(local_dir, f), os.path.join(artifact_path, f))

    def next_scoring_request(self, timeout: float=None) -> (dict, None):
        """
        Use this method to iterate through multiple requests.  Returns a new {} on each request, or None if 'timeout'
        expired before any new requests were received.

        :param timeout:    How long to wait for a new request.
        """

    def scoring_response(self, score) -> None:
        """
        Reports a score from a scoring recipe.
        """

    def start_run(self):
        """
        Wraps the operation so that the actual start and end time can be known.  This is optional except when
        using MLFlow.
        """
        use_mlflow = self._mlflow_all
        if use_mlflow:
            mlflow.start_run()
            a_r = mlflow.active_run()
            self._run_id = a_r.info.run_id if a_r else None
        else:
            # generate a run ID
            self._run_id = str(uuid.uuid4())
            if mlflow:
                # capture some information to support active_run() when not using mlflow
                # TODO shouldn't we instead mock these mlflow classes, in case mlflow is not in the environment?
                from mlflow.entities import Run, RunData, RunInfo
                self._mlflow_run = Run(
                    RunInfo(
                        run_uuid=self._run_id, experiment_id=self._spec.get("uri"), user_id=self._spec.get("user"),
                        status="", start_time=time.time(), end_time=None, lifecycle_stage=""
                    ),
                    RunData()
                )
        inst = self
        class Wrap(object):
            def __enter__(self):
                return inst
            def __exit__(self, exc_type, exc_val, exc_tb):
                inst.end_run()
        return Wrap()

    def end_run(self):
        """
        Signals the end of the operation.
        """
        if self._mlflow_all:
            mlflow.end_run()

    def active_run(self):
        """
        For compatibility with MLFlow.
        """
        use_mlflow = self._mlflow_all
        if use_mlflow:
            return mlflow.active_run()
        return self._mlflow_run

    def install_packages(self, packages: list, verbose: bool=False):
        """
        Install packages.  Does a local 'pip install' by default but can be overridden to interact with different
        virtual environment managers.

        :param packages:  An iterable of package names, with optional qualifiers like "pandas==1.1.5"
        :param verbose:   By default we inhibit most output.
        """
        raise NotImplementedError()

    def _write_content(self, opener, resource_name: str, content, append: bool=False, **kwargs):
        """
        Fully write various types of content.

        :param opener:      Method (i.e. self.open_resource() or similar) that will open a write stream.
        :param resource_name: Name of output resource where content should be stored.
        :param content:     Raw content for the data (various types), or a stream containing the data.
        :param append:      True to append, False to overwrite.

        Optional arguments:
            format              Specifies a file format like 'csv' or 'json'.
            format_options      Options compatible with pandas.to_{format}()
            sql_table           Causes dataframe-like data to be stored into a SQL table.
            nosql_collection    Causes dataframe-like data to be stored into a NoSQL table (not yet implemented).
            dask                True to write a folder instead of a single file, using dask or the conventions of dask.

        :returns:       In the specific case where dask is True, returns the list of generated files.
        """
        use_mlflow = self._mlflow_all
        # map resource name using supplied specs
        uri, kwargs = self._xlt_resource(resource_name, _mode="outputs", **kwargs)
        file_extension = find_url_extension(uri).strip(".")
        if not file_extension:
            self._default_format_for_aliases(resource_name, kwargs)
        format = kwargs.pop("format", None) or file_extension
        format_options = dict(kwargs.pop("format_options", None) or {})
        # detect SQL target
        if kwargs.get("sql_table"):
            # write data to an SQL table
            db_conn = self.get_sql_connection(resource_name, database=kwargs.get("database"))
            content = _coerce_to_dataframe(content)
            try:
                table = kwargs.get("sql_table")
                for sql, params in dataframe_to_sql(content, table_name=table, append=append):
                    db_conn.cursor().execute(sql, params)
            finally:
                db_conn.close()
            return
        if kwargs.get("nosql_collection"):
            # TODO detect nosql (nosql_collection) and write data there
            raise NotImplementedError("NoSQL write of columnar data is not yet implemented")
        # we detect numpy arrays, series, etc., and save them as a dataframe with one column
        if isinstance(content, (pandas.Series, numpy.ndarray, pandas.Index)):
            content = _coerce_to_dataframe(content)
        # send (pandas) DataFrame as CSV/etc.
        df_format = format if format in PANDAS_WRITE_FORMATS else "csv"
        if hasattr(content, PANDAS_WRITE_FORMATS[df_format]):
            # dataframes
            # - the 'dask' flag requests dask-like writes to a folder instead of a single file
            is_dask = hasattr(content, "dask")
            use_dask = kwargs.pop("dask", None)
            if use_dask and not is_dask:
                # pandas > dask
                content = dask.dataframe.from_pandas(content, npartitions=1)
                is_dask = True
            elif is_dask and not use_dask and df_format not in ("csv", "tab", "tsf"):
                # dask > pandas
                content = content.compute()
                is_dask = False
            # get write method to call
            df_method = getattr(content, PANDAS_WRITE_FORMATS[df_format])
            # cancel append mode if file does not exist
            if append:
                try:
                    # verify file exists, capture column names
                    with opener(uri, 'rb') as f_r:
                        chk_args = {"nrows": 0}
                        if format == "json":
                            chk_args["lines"] = True
                        # apply write args to read format
                        for f in ["sep"]:
                            if f in format_options:
                                chk_args[f] = format_options[f]
                        # FIXME use load_dataframe() here to get sniffing/etc.
                        df0 = PANDAS_READ_FORMATS[df_format](f_r, **chk_args)
                        # verify column names match
                        cols_l = set(df0.columns)
                        cols_r = set(content.columns)
                        if cols_l != cols_r:
                            raise DSLibraryException(f"Cannot append to {resource_name}, column names do not match: {', '.join(sorted(cols_l))} vs {', '.join(sorted(cols_r))}")
                except FileNotFoundError:
                    append = False
            mode = "w"
            if append:
                mode = "a"
                if format in ("csv", "tab"):
                    format_options.update({"header": False})
            if "index" not in format_options and format not in ("json",):
                format_options["index"] = False
            if format == "json":
                format_options.update({"orient": "records", "lines": True})

            if use_dask:
                # send the URI directly to Dask so that it will write out a folder with each chunk
                # FIXME opener() may do quite a bit more than simply open a file, so this is bound to be error-prone
                return df_method(uri, **format_options, **kwargs)
            if is_dask:
                # in this case we have a dask dataframe but want to send it to a file, not a folder
                #  - dask only supports this for CSV files
                format_options["single_file"] = True
                with tempfile.NamedTemporaryFile(mode='rb', suffix=".csv") as f_tmp:
                    # write to a unified local CSV file
                    df_method(f_tmp.name, **format_options)
                    # use opener() to write to the intended destination
                    with open(f_tmp.name, mode='rb') as f_r:
                        with opener(uri, 'wb', **kwargs) as f_w:
                            shutil.copyfileobj(f_r, f_w)
                return
            with opener(uri, mode, **kwargs) as f_w:
                df_method(f_w, **format_options)
            return
        # save matplotlib figures as images
        elif hasattr(content, "savefig"):
            if append:
                raise ValueError("append is not supported for figures")
            if use_mlflow:
                mlflow.log_figure(content, uri)
                return
            buf = io.BytesIO()
            image_format = format or "png"
            content.savefig(buf, format=image_format)
            content = buf.getvalue()
        mode_base = 'a' if append else 'w'
        if isinstance(content, io.IOBase):
            # copy stream content
            with self.open_resource(resource_name, mode=mode_base + ('' if isinstance(content, io.TextIOBase) else 'b'), **kwargs) as f_w:
                while True:
                    chunk = content.read(5000000)
                    if not chunk:
                        break
                    f_w.write(chunk)
        elif isinstance(content, (str, bytes, bytearray)):
            # write content directly
            if use_mlflow:
                if not isinstance(content, str):
                    content = content.decode("utf-8")
                mlflow.log_text(content, uri)
            else:
                with self.open_resource(resource_name, mode=mode_base + ('' if isinstance(content, str) else 'b'), **kwargs) as f_w:
                    f_w.write(content)
        elif isinstance(content, (dict, list, tuple)):
            # write yaml or json
            if use_mlflow and isinstance(content, dict):
                mlflow.log_dict(content, uri)
                return
            if format in ("yaml", "yml"):
                with self.open_resource(resource_name, mode=mode_base, **kwargs) as f_w:
                    yaml.safe_dump(content, f_w)
                    f_w.write("\n")
            else:
                with self.open_resource(resource_name, mode=mode_base, **kwargs) as f_w:
                    json.dump(content, f_w)
                    f_w.write("\n")
        else:
            raise Exception(f"Unsupported content type or format: {type(content)}")

    def _write_file(self, opener, resource_name: str, filename: str, append: bool=False):
        """
        Copy a file or folder to an output resource.

        :param opener:      Method (i.e. self.open_resource() or similar) that will open a r/w stream.
        :param resource_name: Name of output resource to write to.
        :param filename:    Name of local file or folder to copy.
        :param append:      True to append, False to overwrite.
        """
        if os.path.isdir(filename):
            for f in os.listdir(filename):
                src = os.path.join(filename, f)
                dst = os.path.join(resource_name, f)
                self._write_file(opener, dst, src)
        else:
            with open(filename, 'rb') as f_r:
                with opener(resource_name, mode='ab' if append else 'wb') as f_w:
                    while True:
                        chunk = f_r.read(5000000)
                        if not chunk:
                            break
                        f_w.write(chunk)

    def read_resource(self, resource_name: str, mode: str='rb', **kwargs) -> (str, bytes):
        """
        Completely read the contents of a given named resource.  This is a convenience method for accessing small
        files.
        """
        with self.open_resource(resource_name, mode=mode, **kwargs) as f_r:
            return f_r.read()

    @staticmethod
    def _in_memory_append(a, b):
        if isinstance(a, str):
            return a + str(b)
        if isinstance(a, (bytes, bytearray)):
            return a + (b if isinstance(b, (bytes, bytearray)) else str(b).encode("utf-8"))
        if hasattr(a, "append"):
            return a.append(b)
        if isinstance(a, list):
            return a + list(b)
        if isinstance(a, dict) and isinstance(b, dict):
            out = dict(a)
            out.update(b)
            return out
        return b

    def _capturing_output(self, resource_name: str) -> bool:
        """
        Whether the given output is supposed to be captured.  This is part of the development/debugging feature that
        frees a caller from having to store i/o data in files to test a model.
        """
        return ((self._spec.get("outputs") or {}).get(resource_name) or {}).get("capture")

    def write_resource(self, resource_name: str, content=None, from_filename: str=None, append: bool=False, **kwargs):
        """
        Write various types of content or files to an output resource.
        :param resource_name:       Which output resource.
        :param content:             What to write (content):
            str, bytes, bytearray, file-like object:  Writes supplied content.
            pandas dataframe        Writes to CSV files, etc..
            matplotlib figure       Writes an image.
            dict, list              Writes JSON or YAML files.
        :param from_filename:       What to write (file or folder).
        :param append:              True to append, False to replace.
        """
        if content is not None:
            # content can be requested to be captured
            if self._capturing_output(resource_name):
                if "capture" not in self._spec:
                    self._spec["capture"] = {}
                if append:
                    prev = self._spec["capture"].get(resource_name)
                    if prev is not None:
                        content = self._in_memory_append(prev, content)
                self._spec["capture"][resource_name] = content
                return
            return self._write_content(self.open_resource, resource_name, content=content, append=append, **kwargs)
        elif from_filename is not None:
            use_mlflow = self._mlflow_all
            if use_mlflow:
                mlflow.log_artifact(from_filename, resource_name)
                return
            self._write_file(self.open_resource, resource_name, filename=from_filename, append=append)
        else:
            raise ValueError("expected content or filename")

    def multi_part_upload(self, resource_name: str, chunk: (bytes, bytearray), upload_id: str=None, sequence: int=None, done: bool=False, **kwargs):
        """
        Manage a large upload.

        This is a placeholder for proper upload functionality for very large files, particularly to systems like S3 that
        do not support append.

        :param chunk:       Data to send.
        :param upload_id:   Unique identifier for the upload, returned from the first call.
        :param sequence:    Chunks can be delivered out of sequence, i.e. by separate processes.
        :param done:        Set this flag on the last chunk.
        :return:        An upload identifier.
        """
        # TODO this placeholder implementation just appends to a file.  This won't work for systems like s3.
        with self.open_resource(resource_name, mode='ab' if upload_id else 'wb', **kwargs) as f_w:
            f_w.write(chunk)
        return "-"

    def load_dataframe(self, resource_name: (str, io.RawIOBase, typing.Iterable), **kwargs):
        """
        Load a pandas dataframe from various types of input resources.

        Optional arguments:
            uri - path or URI to target
            format - csv, json, etc
            format_options - these are passed to pandas.read_csv(), etc.
            filesystem - name of a filesystem
            sql - SQL to execute
            sql_table - name of table to fully load
            nosql_collection - name of a NoSQL collection to fully load
            run_data - True to read using open_run_data()
            dask - True to load into a dask dataframe, or an integer to load into dask if file size is >= to threshold.

        :param resource_name:   The name of an input resource, or of a local file, or the URI of an external resource.
        """
        # look up pre-supplied data
        # do translation of named resources
        if isinstance(resource_name, str):
            # check for specifically supplied data
            supplied = (self._spec.get("data") or {}).get(resource_name)
            if supplied is not None and hasattr(supplied, "columns"):
                return supplied
            # map requested resource (resource_name) through input spec and override defaults (kwargs)
            uri, open_args = self._xlt_resource(resource_name, **kwargs)
        else:
            uri = getattr(resource_name, "name") if hasattr(resource_name, "name") else ""
            open_args = kwargs
        # arguments that are specific to load_dataframe() and should not go through to open_resource()
        fallback_to_text = open_args.pop("fallback_to_text", False)
        use_dask = open_args.pop("dask", None) or 0
        if use_dask and not dask:
            warnings.warn("Dask was requested but is not installed", ImportWarning)
            use_dask = False
        format_options = open_args.pop("format_options", None) or {}
        format = open_args.pop("format", None)
        if format:
            format_options = dict(format_options)
            format_options["format"] = format
        if "#" in uri:
            # URI can contain formatting arguments
            uri, uri_args = uri.split("#", maxsplit=1)
            for k, v in urllib.parse.parse_qs(uri_args).items():
                format_options[k] = v[0] if len(v) == 1 else v
        if isinstance(resource_name, str):
            # detect SQL
            if open_args.get("sql") or open_args.get("sql_table"):
                sql = open_args.pop("sql", None)
                table = open_args.pop("sql_table", None)
                db_conn = self.get_sql_connection(resource_name, **open_args)
                if table:
                    flavor = getattr(db_conn, "_flavor") if hasattr(db_conn, "_flavor") else None
                    sql = f"SELECT * from {sql_enquote_id(table, dotted=True, mode=flavor)}"
                try:
                    c = db_conn.cursor()
                    c.execute(sql)
                    col_names = [col[0] for col in c.description]
                    df = pandas.DataFrame(data=c, columns=col_names)
                    if use_dask:
                        mem_size = df.memory_usage().sum()
                        if mem_size > use_dask:
                            partition_size = max(use_dask, 40000000)
                            df = dask.dataframe.from_pandas(df, npartitions=min(mem_size//partition_size, 2))
                finally:
                    db_conn.close()
                return df
            # detect NoSQL
            if open_args.get("nosql_collection"):
                collection = open_args.pop("nosql_collection")
                db_conn = self.get_nosql_connection(resource_name, **open_args)
                rows = list(db_conn.query(collection))
                return pandas.DataFrame(rows)
            # TODO we should offer a validation option that checks the data types against the schema
            # format can be specified, or file extension will be used
            file_extension = find_url_extension(uri)
            if not file_extension:
                self._default_format_for_aliases(resource_name, open_args)
            # this method will be used to open the stream...
            use_opener = self.open_run_data if open_args.pop("run_data", None) else self.open_resource
        elif hasattr(resource_name, "read"):
            stream = resource_name
            orig_mode = "r" if isinstance(stream, io.TextIOBase) else "rb"
            count = [0]
            def open_existing_stream(filename: str, mode: str='rb', **kwargs):
                if count[0]:
                    if hasattr(stream, "seek") and hasattr(stream, "seekable") and stream.seekable():
                        stream.seek(0)
                    else:
                        raise Exception("internal usage error, stream is not seekable")
                count[0] += 1
                s_out = GenericStreamWrapper(stream, close=False)
                if mode != orig_mode:
                    if mode == 'r':
                        s_out = io.TextIOWrapper(s_out, 'utf-8')
                    else:
                        s_out = BytesIOWrapper(s_out)
                return s_out
            use_opener = open_existing_stream
        else:
            # list, dict, etc.
            # FIXME what to do with all the other arguments?  dask, at least could be applied
            return pandas.DataFrame(resource_name)
        # sample-taker
        def sampler():
            sample_size = open_args.pop("sample_size", None) or 30000
            if sample_size < 0:
                return
            try:
                with use_opener(uri, mode='rb', **open_args) as f_r:
                    return f_r.read(sample_size)
            except IsADirectoryError:
                pass
        def sizer():
            with use_opener(resource_name, mode='rb', **open_args) as f_r:
                if not hasattr(f_r, "seek") or not f_r.seekable():
                    return
                try:
                    f_r.seek(0, 2)
                    return f_r.tell()
                except:
                    return
        # sniff format
        use_sizer = use_dask > 1
        format_info = detect_format(
            uri, sampler=sampler, sizer=sizer if use_sizer else None, supplied_options=format_options, fallback_to_text=fallback_to_text
        )
        format = format_info.format
        read_args = format_info.read_args
        # choose dask based on threshold
        if use_dask > 1:
            if format_info.size is not None:
                use_dask = format_info.size > use_dask
            else:
                # size unknown - use dask if dask limit was set to a particularly low value
                use_dask = 10000 > use_dask
        # various formats and their read function
        if use_dask:
            use_dask = format in DASK_READ_FORMATS
            read_method = DASK_READ_FORMATS.get(format, PANDAS_READ_FORMATS.get(format))
            if format == "csv" and use_dask:
                # dask reads 'sample' bytes to determine dtypes, default is 256k, which is often too small
                #  - 10M is also bound to be too small of course, but it's somewhat less likely
                if "sample" not in read_args:
                    read_args["sample"] = 10000000
                # without this, data with ints at the front and floats at the back raises an exception
                #  - this solves one typical problem from the limited dtype sampling above
                if "assume_missing" not in read_args:
                    read_args["assume_missing"] = True
        else:
            read_method = PANDAS_READ_FORMATS.get(format)
        if read_method:
            if use_dask:
                storage_options = open_args.get("storage_options") or open_args
                try:
                    return read_method(uri, storage_options=storage_options, **read_args)
                except IsADirectoryError:
                    return read_method(uri + "/*", storage_options=storage_options, **read_args)
            # when returning a chunk stream we need to keep the stream open until iteration completes
            if format_info.read_args.get("chunksize"):
                class CloseAfterIteration(object):
                    def __init__(self, stream, iterator):
                        self.stream = stream
                        self.iterator = iterator
                        self.closed = False

                    def __iter__(self):
                        return self

                    def __next__(self):
                        try:
                            return next(self.iterator)
                        except StopIteration:
                            self.close()
                            raise

                    def close(self):
                        if not self.closed:
                            self.stream.close()
                            self.closed = True

                    def tell(self):
                        if not hasattr(self.stream, "tell"):
                            return
                        return self.stream.tell()

                    def get_chunk(self, size=None):
                        try:
                            if hasattr(self.iterator, "get_chunk"):
                                return self.iterator.get_chunk(size)
                        except StopIteration:
                            self.close()
                            raise

                stream = use_opener(uri, mode='rb', **open_args)
                iterator = self._open_from_stream(stream, read_method, read_args, format)
                return CloseAfterIteration(stream, iterator)
            with use_opener(uri, mode='rb', **open_args) as f_r:
                return self._open_from_stream(f_r, read_method, read_args, format)
        # TODO support read from folder, i.e. folder of CSVs, parquet, etc.
        raise DSLibraryException(f"file type not supported: {format}")

    def _open_from_stream(self, f_r, read_method, read_args, format):
        if format == "xlsx" and not f_r.seekable():
            # the XLSX reader requires its stream to be seekable so we download to a temporary file
            with tempfile.NamedTemporaryFile(mode='wb') as f_tmp:
                # chunked copy
                shutil.copyfileobj(f_r, f_tmp)
                f_tmp.flush()
                with open(f_tmp.name, mode='rb') as f_r2:
                    return read_method(f_r2, **read_args)
        # the 'hdf' implementation doesn't accept a stream, only a filename
        if format == "hdf" and hasattr(f_r, "name") and ":" not in f_r.name:
            return read_method(f_r.name, **read_args)
        if format == "hdf":
            with tempfile.NamedTemporaryFile(mode='wb') as f_tmp:
                shutil.copyfileobj(f_r, f_tmp)
                f_tmp.flush()
                return read_method(f_tmp.name, **read_args)
        try:
            return read_method(f_r, **read_args)
        except UnicodeDecodeError as err:
            raise DSLibraryDataFormatException(
                f"Invalid character encoding: {err.reason}: encoding={err.encoding}, offset={err.start} - set 'encoding' or 'encoding_errors' options to compensate",
                offset=err.start)
        except ValueError as err:
            if format == "json":
                raise DSLibraryDataFormatException(f"JSON format error: {str(err)}")
            else:
                raise DSLibraryDataFormatException(f"{str(err)}")

    def _default_format_for_aliases(self, resource_name: str, options: dict):
        """
        Fill in default format for the built-in aliases.
        """
        if not options.get("format") and resource_name in (METRICS_ALIAS, PARAMS_ALIAS):
            options["format"] = "json"
            if "format_options" in options:
                format_options = options["format_options"]
            else:
                format_options = options["format_options"] = {}
            if "lines" not in format_options:
                format_options["lines"] = True

    def load_pickled_model(self, part: str=None):
        """
        Un-pickle a saved model from the default model binary, or from one of its named parts.
        """
        with self.open_model_binary(part=part, mode='rb') as f_r:
            return pickle.load(f_r)

    def save_pickled_model(self, model_object, part: str = None):
        """
        Use pickle to save a model.
        """
        with self.open_model_binary(part=part, mode='wb') as f_w:
            return pickle.dump(model_object, f_w)

    def read_run_data(self, resource_name: str, mode='rb') -> (str, bytes):
        """
        Completely read the contents of a given named 'run data' resource'.
        """
        with self.open_run_data(resource_name, mode=mode) as f_r:
            return f_r.read()

    def write_run_data(self, resource_name: str, content=None, filename: str=None, append: bool=False, **kwargs):
        """
        Fully write a named 'run data' object.
        """
        if content is not None:
            self._write_content(self.open_run_data, resource_name, content=content, append=append, **kwargs)
        elif filename is not None:
            self._write_file(self.open_run_data, resource_name, filename=filename, append=append)
        else:
            raise ValueError("expected content or filename")

    # TODO add remaining mlflow.tracking methods so that we can do this:
    #   mlflow = dslibrary.instance()


LOCAL_SPECS_SCHEMA = {
    "comment": "Parameter values, and format/mapping information for inputs and outputs, as well as every other configurable run option is defined here.",
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "uri": {"type": "string"},
        "user": {"type": "string"},
        "run_id": {"type": "string"},
        "entry_point": {"type": "string"},
        "code_paths": {"type": "array", "items": {"type": "string"}},
        "parameters": {
            "comment": "Named parameter values for local testing.",
            "type": "object"
        },
        "inputs": {
            "comment": "Names of each input data source are mapped to appropriate local testing locations.",
            "type": "object",
            "patternProperties": {
                ".+": {
                    "comment": "Instructions for locating this particular named input to the model.  Parameters other than 'path' are passed through to the open() method, i.e. to fsspec.open().",
                    "type": "object",
                    "properties": {
                        "uri": {
                            "comment": "A URI to a remote resource can be given here, or a path (relative to the model root, or absolute) to a local file.  If omitted, blank or '.', the name of the input is used.",
                            "type": "string"
                        }
                    }
                }
            }
        },
        "outputs": {
            "comment": "Names of each output are mapped to appropriate local testing locations.  Same format as 'inputs'.",
            "type": "object"
        },
        "metrics": {
            "comment": "Where to send (or read) metrics.",
            "type": "object",
            "properties": {
                "uri": {
                    "comment": "Designates a columnar file or other data source where metrics will be stored",
                    "type": "string"
                }
            }
        },
        "mlflow": {
            "comment": "MLFlow-related settings",
            "type": "object",
            "properties": {
                "metrics": {"type": "boolean", "comment": "Uses MLFlow for tracking of metrics."},
                "all": {"type": "boolean", "comment": "Uses MLFlow for all available functionality."},
                "connection": {"comment": "uri, username, password"}
            }
        }
    }
}


def _coerce_to_dataframe(content):
    """
    Turn things into dataframes.
    """
    if hasattr(content, "columns") and hasattr(content, "itertuples"):
        return content
    elif hasattr(content, "__iter__"):
        content = pandas.DataFrame(content)
        if len(content.columns) and not isinstance(content.columns[0], str):
            # numeric column names export ambiguously to CSV
            # TODO align this convention with pandas methods which generate (maybe) "Col_1", etc.
            content.columns = [f"col{n}" for n in range(1, len(content.columns)+1)]
        return content
    else:
        raise NotImplementedError(f"cannot convert {type(content)} to dataframe")


PANDAS_READ_FORMATS = {
    "csv": pandas.read_csv,
    # TODO should we use json_normalize() or read_json() here, or add a switch?
    #  - note that json and yaml are currently different
    "json": pandas.read_json,
    "yaml": lambda fh, **kwargs: pandas.json_normalize(yaml.safe_load(fh), **kwargs),
    "parquet": pandas.read_parquet,
    "xlsx": pandas.read_excel,
    "xls": pandas.read_excel,
    "hdf": pandas.read_hdf,
    "fwf": pandas.read_fwf
}

PANDAS_WRITE_FORMATS = {
    "csv": "to_csv",
    "tab": "to_csv",
    "json": "to_json",
    "parquet": "to_parquet",
    "xlsx": "to_excel",
    "xls": "to_excel",
    "hdf": "to_hdf",
    "fwf": "to_fwf"
}

try:
    import dask.dataframe
    DASK_READ_FORMATS = {
        "csv": dask.dataframe.read_csv,
        "json": dask.dataframe.read_json,
        "parquet": dask.dataframe.read_parquet,
        "hdf": dask.dataframe.read_hdf,
        "fwf": dask.dataframe.read_fwf
    }
except ImportError:
    DASK_READ_FORMATS = {}
