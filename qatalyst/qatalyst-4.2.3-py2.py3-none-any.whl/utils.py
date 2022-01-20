#
#    (C) Quantum Computing Inc., 2021.
#
#    THIS IS UNPUBLISHED PROPRIETARY SOURCE CODE of the Copyright Holder.
#    The contents of this file may not be disclosed to third parties, copied
#    or duplicated in any form, in whole or in part, without the prior written
#    permission of the Copyright Holder.
#
import os
import dateutil as du
import re
import requests
from typing import Union, List, AnyStr
from scipy.optimize import show_options
import pandas as pd

from .data_processing import Status, StatusCodes, AwsDeviceClient
from .constants import QatalystConstants

def sampler_type_is_qpu(sampler_name, samplers=None):
    if samplers is None:
        samplers = load_available_samplers()
    return sampler_name in set(samplers[samplers['quantum']]['target_name'])


def sampler_type_is_not_qpu(sampler_name, samplers=None):
    if samplers is None:
        samplers = load_available_samplers()
    return sampler_name in set(samplers[samplers['quantum'] == False]['target_name'])


def load_available_samplers():
    fname = 'available_samplers.csv'
    path = os.sep.join([*os.path.expanduser(__file__).split(os.sep)[:-1], fname])
    df = pd.read_csv(path, dtype={'max_size': int})
    return df


def print_available_samplers():
    samplers = load_available_samplers()
    cols = samplers.columns.to_list()
    print(f"{cols[0]:<18}{'  ':^5}" + "|".join([f'{col:^15}' for col in cols[1:]]))
    print()
    for _, row in samplers.iterrows():
        print(f"{row['target_name']:<18}{'->':^5}" + "|".join([f'{col:^15}' for col in row.iloc[1:]]))
    print("\nSelect 'target_name' to run a problem on a particular sampler. Size limitations apply. "
          "See Qatalyst documentation for further details.")


def get_scipy_minimize_methods():
    """
    We want to match elements '===' right after the methods in the string returned
    by show_options.
    """
    REGEX = r'[=]+$'
    opts = show_options('minimize', disp=False)
    opts = [x for x in opts.split('\n') if len(x) > 0]
    return [opts[i-1] for i, m in enumerate(opts) if re.match(REGEX, m)]


def mincheck(t, v) -> bool:
    """
    Make sure val > threshold
    """
    return v > t


def boolcheck(v) -> bool:
    """
    Make sure val is a boolean
    """
    return isinstance(v, bool)


def strcheck(param, val) -> bool:
    """
    Make sure val is a string containing only valid characters
    """
    if not val:
        return False

    if not isinstance(val, str):
        raise ValueError(f"Parameter value {val} must be a str.")
        return False

    return val.isidentifier()


def algocheck(options: List[AnyStr], algo: str) -> bool:
    return algo.lower() in options


def optimizer_check(optimizers: List[AnyStr], opt: str) -> bool:
    return opt.lower() in optimizers


def optimizer_options_check(param: Union[str, bool, int, float], opts: dict):
    OPTIONS = {'maxiter': param}
    for opt, val in opts.items():
        if opt in OPTIONS:
            thresh = OPTIONS[opt]
            return mincheck(thresh, val)


def parse_status(resp: requests.Response) -> Status:
    """
    Args:
        resp: requests Response

    Return:

    """
    codes = StatusCodes
    res = resp.json()
    status = res.get('status')
    message = res.get('message')
    ts = res.get('time_stamp')
    ts = du.parser.parse(ts).astimezone()

    if isinstance(message, str) and ('error' in message.lower() or 'exception' in message.lower()):
        return Status(status=codes.error, timestamp=ts, message=message)
    elif status == 'COMPLETE':
        return Status(status=codes.complete, timestamp=ts)
    elif 'ERROR' in status or 'EXCEPTION' in status:
        return Status(status=codes.error, timestamp=ts, message=message)
    else:
        # Strip internal service name from message
        if message is None and '`QUOIR`-' in status:
            processor = status.lstrip('QUOIR-')
            # means we just made it to the consumer and we might be looking for an embedding or something
            if 'producer' in status:
                user_message = f'Sent problem to {processor} preprocessing. Waiting for response...'
            else:
                user_message = f'Sent problem to {processor} processor/QPU. Waiting for response...'
        else:
            user_message = message
        return Status(status=codes.processing, message=user_message, timestamp=ts)


def param_check(params: dict, quantum: bool = False):
    """
    We check the basic parameters here, outside of sampler, which has been checked and set elsewhere.
    """
    checks = {
        QatalystConstants.PARAM_NUM_SOLUTIONS: (mincheck, 0),
        QatalystConstants.PARAM_PROBLEM_NAME: (strcheck, None)
    }

    if quantum:
        checks.update({QatalystConstants.PARAM_NUM_SHOTS: (mincheck, 0),
                       QatalystConstants.PARAM_NUM_READS: (mincheck, 0),
                       QatalystConstants.PARAM_DEPTH: (mincheck, 1),
                       QatalystConstants.PARAM_ALGORITHM: (algocheck, ['vqe', 'qaoa']),
                       QatalystConstants.PARAM_OPTIMIZER: (optimizer_check, get_scipy_minimize_methods()),
                       QatalystConstants.PARAM_OPTIMIZER_PARAMS: (optimizer_options_check, 0)}) # only set up for 'maxiter' > 0 check

    # loop through params
    for pname, val in params.items():
        # get the function from above for a given parameter, else None
        func_param = checks.get(pname)
        if func_param is None:
            continue
        else:
            f, param = func_param
        # is the provided value within the range required
        if not f(param, val):
            if isinstance(param, int):
                raise ValueError(f"Parameter '{pname}'={val}, must be greater than {param}.")
            elif isinstance(param, dict):
                raise ValueError(f"Parameter '{pname}'={val}, must be greater than {param}.")
            elif isinstance(val, str):
                raise ValueError(f"Parameter '{pname}'={val}, must be valid python identifier.")
            else:
                raise ValueError(f"Parameter '{pname}={val}', must be one of {param}")
    else:
        return True


def is_braket_qpu_execution_limited(device: AwsDeviceClient):
    """
    Args:

    """
    hours_up = device.execution_window['hours_up_per_day']
    days_up = device.execution_window['days']
    if days_up == 'Everyday' and hours_up == 24:
        return False
    else:
        return True


def get_braket_qpu_execution_message(device: AwsDeviceClient):
    return f"{device.execution_window['message']} Executing outside of this time window could incur significant " \
           f"delays.\nContinue? Proceed (y) or abort (n)?\n* To disable this warning set kwarg ignore_qpu_window=True or set QATALYST_IGNORE_QPU_WINDOW=1 in your environment. *\n"
