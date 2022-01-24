import os
import sys
import logging
import json
from brevettiai.platform import Job

log = logging.getLogger(__name__)


def setup_raygun(api_key=None, force=True):
    try:
        from raygun4py import raygunprovider
    except ModuleNotFoundError:
        return

    api_key = api_key or os.environ.get("RAYGUN_API_KEY")
    if (force or not sys.gettrace()) and api_key is not None:
        log.info("Setting up raygun to catch errors! '%s'")

        def handle_exception(exc_type, exc_value, exc_traceback):
            log.debug("Sending exception info to raygun")

            raygun_config = dict(
                filtered_keys=['AWS_SECRET_ACCESS_KEY'],
                transmit_global_variables=False,
                transmit_local_variables=False,
                userversion=os.environ.get("BUILD_ID"),
            )

            client = raygunprovider.RaygunSender(api_key,
                                                 config=raygun_config)

            client.send_exception(exc_info=(exc_type, exc_value, exc_traceback),
                                  userCustomData={"configs": object_extractor(Job,
                                                                              exc_traceback,
                                                                              prep_criterion_config)})

        sys.excepthook = handle_exception


def prep_criterion_config(config):
    return json.loads(str(config))


def object_extractor(types, exc_tb=None, prep_func=None):
    import inspect
    types = types if isinstance(types, tuple) else (types, )
    objects = {}
    frames = inspect.stack() if exc_tb is None else inspect.getinnerframes(exc_tb)
    for frameinfo in frames:
        frame = frameinfo.frame
        f_locals = frame.f_locals
        keys = list(f_locals.keys())
        for k in keys:
            v = f_locals.get(k, None)
            code = frame.f_code
            if isinstance(v, types):
                entry = objects.setdefault(id(v),
                                           {"location": [],
                                            "obj": v if prep_func is None else prep_func(v)})
                entry["location"].insert(0, f"{k} in {code.co_name}, {code.co_filename}:{frame.f_lineno}")
    return objects