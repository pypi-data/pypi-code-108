"""
DSLIBRARY - run your data science code anywhere.

"""
__version__ = "0.0.38"

# exceptions
from .exceptions import *
# environment variables
from .front import ENV_DSLIBRARY_TARGET, ENV_DSLIBRARY_SPEC, ENV_DSLIBRARY_TOKEN
# main base class
from .front import DSLibrary
# run models
from .run_models import ModelRunner
# utils for doing setup
from .utils.instantiation import parse_verb_and_args, instantiate_class_and_args

# if a package called 'mmlibrary' is installed it becomes the default target
try:
    import mmlibrary
except ImportError:
    mmlibrary = None


def instance(env: dict=None):
    """
    Get an instance of mmlibrary methods.  Configuration is through environment variables.

    To run locally in the current folder:   (this is the default)
      DSLIBRARY_TARGET=local

    To run locally with a specific default folder:
      DSLIBRARY_TARGET=local:<folder>

    To run against a REST API:
      DSLIBRARY_TARGET=https://hostname:port/path/to/api/
      DSLIBRARY_TOKEN=<access token, or credentials>

    To use a custom implementation:
      DSLIBRARY_TARGET=package.ClassName:value:name=value

    Parameter values and data input/output locations/formats and such are defined by setting this variable to
    JSON (see ModelRunner).
      DSLIBRARY_SPEC={...}

    :param env:  Instead of using os.environ, environment values can be specified here.

    :returns:    An instance of the MMLibrary() base class.
    """
    from .transport.to_local import DSLibraryLocal
    from .transport.to_rest import DSLibraryViaREST
    from .transport.to_volume import DSLibraryViaVolume
    from .transport.to_mmlibrary import DSLibraryViaMMLibrary

    import json
    import os
    if env is None:
        env = os.environ
    spec = env.get(ENV_DSLIBRARY_SPEC) or "{}"
    if isinstance(spec, str):
        spec = json.loads(spec)
    target = env.get(ENV_DSLIBRARY_TARGET) or ("mmlibrary" if mmlibrary else "local")
    target_parts = target.split(":")
    # point to a REST API
    if target_parts[0] in ("http", "https"):
        token = env.get(ENV_DSLIBRARY_TOKEN)
        return DSLibraryViaREST(url=target, token=token)
    # FIXME protocol handlers need to use 'env'
    # gather arguments
    mode, args, kwargs = parse_verb_and_args(target)
    if spec:
        kwargs["spec"] = spec
    if env is not None:
        kwargs["_env"] = env
    # a strictly local instance
    if target_parts[0] == "local":
        return DSLibraryLocal(*args, **kwargs)
    # delegation to 'mmlibrary'
    if target_parts[0] == "mmlibrary":
        return DSLibraryViaMMLibrary(*args, **kwargs)
    # writes through a shared volume, i.e. so that a sidecar can perform communications for us
    if target_parts[0] == "volume":
        return DSLibraryViaVolume(*args, **kwargs)
    # we fall through to custom implementation support
    return instantiate_class_and_args(target, DSLibrary)


def run_model_method(method, dsl=None):
    """
    Call a method representing a model, passing along the parameters that come from either a supplied dslibrary instance
    (dsl), or from the default dslibrary instance.

    :param method:  Method to call.
    :param dsl:     Dslibrary instance which will fetch the calling parameters.
    :return:        Return value from the method (or captured KPIs if that is configured).
    """
    params = dsl.get_parameters() if dsl else get_parameters()
    return ModelRunner(parameters=params).run_method(method)


# set up default methods
_DEFAULT = instance()
get_parameter = _DEFAULT.get_parameter
get_parameters = _DEFAULT.get_parameters
load_dataframe = _DEFAULT.load_dataframe
open_resource = _DEFAULT.open_resource
write_resource = _DEFAULT.write_resource
log_metric = _DEFAULT.log_metric
log_metrics = _DEFAULT.log_metrics
log_param = _DEFAULT.log_param
log_artifact = _DEFAULT.log_artifact
log_artifacts = _DEFAULT.log_artifacts
log_dict = _DEFAULT.log_dict
log_text = _DEFAULT.log_text
get_sql_connection = _DEFAULT.get_sql_connection
open_run_data = _DEFAULT.open_run_data
read_run_data = _DEFAULT.read_run_data
write_run_data = _DEFAULT.write_run_data
set_evaluation_result = _DEFAULT.set_evaluation_result
open_model_binary = _DEFAULT.open_model_binary
load_pickled_model = _DEFAULT.load_pickled_model
save_pickled_model = _DEFAULT.save_pickled_model
read_resource = _DEFAULT.read_resource
start_run = _DEFAULT.start_run
end_run = _DEFAULT.end_run
active_run = _DEFAULT.active_run
get_metadata = _DEFAULT.get_metadata
get_uri = _DEFAULT.get_uri
get_last_metric = _DEFAULT.get_last_metric
get_filesystem_connection = _DEFAULT.get_filesystem_connection
install_packages = _DEFAULT.install_packages
scoring_response = _DEFAULT.scoring_response
# TODO there may be more methods to add here
