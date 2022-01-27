#
# $Id:$
#
# This file is part of the Cloud Services Integration Platform (CSIP),
# a Model-as-a-Service framework, API, and application suite.
#
# 2012-2020, OMSLab, Colorado State University.
#
# OMSLab licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
#
from builtins import Exception

import requests
import numpy as np
import json
from csip import Client

NORM = {
    'kge': lambda x: 1 - x,
    'nslog': lambda x: 1 - x,
    'nslog1p': lambda x: 1 - x,
    'ns': lambda x: 1 - x,
    'rmse': lambda x: x,
    'trmse': lambda x: x,
    'pbias': lambda x: abs(x)
}


def calc_cost(response: "Client", objfunc) -> float:
    """aggregated objective function value -> cost"""

    # this will eliminate the failed run as a candidate solution.
    if not response.is_finished():
        return np.nan

    cost = 0.0
    for o in objfunc:
        cosu_val = response.get_cosu_value(o['name'])
        if cosu_val is None:
            raise Exception('No cosu of value for ' + o['name'])
        cosu_of = o['of']
        n = NORM.get(cosu_of, lambda x: x) # default
        cost += n(cosu_val) * o.get('weight', 1.0)

        # of_val = response.get_data_value(of['name'])
        # for name in NORM:
        #     if str(c['name']).startswith(name):
        #         cost += NORM[name](cosu_val) * c.get('weight', 1.0)
    return cost

def save(file, dict):
    """ Save dict to json file. """
    with open(file, 'w') as json_file:
        json.dump(dict, json_file, sort_keys=False, indent=2)


def load(file):
    """ Load dict from json file. """
    with open(file) as json_file:
        data = json.load(json_file)
    return data


def get_step_info(steps, index):
    """Extract all relevant info from the step dict"""

    step = steps[index]
    l = len(step['param'])
    param_min = np.ones(l)
    param_max = np.ones(l)
    param_names = []

    # extract names and bounds
    for i, p in enumerate(step['param']):
        param_names.append(p['name'])
        if len(p['bounds']) != 2:
            raise Exception('Invalid bounds tuple: (min, max): "{}"'.format(p['bounds']))
        if not p['bounds'][0] < p['bounds'][1]:
            raise Exception('Invalid bounds values: "{}"'.format(p['bounds']))
        param_min[i] = p['bounds'][0]
        param_max[i] = p['bounds'][1]

        # check if OF is supported
    for o in step['objfunc']:
        #  if not o['name'] in NORM:
        #    raise Exception('OF not supported: "{}"'.format(o['name']))
        found = False
        for name in NORM:
            if str(o['name']).startswith(name):
                found = True
        if not found:
            raise Exception('OF not supported: "{}"'.format(o['name']))
        if len(o['data']) != 2:
            raise Exception('OF missing data: (sim, obs): "{}"'.format(o['name']))

    return param_names, (param_min, param_max), step['objfunc']


def get_calibrated_params(steps, index):
    """Get all previously calibrated parameter from any other step"""

    step = steps[index]
    cp = {}
    for s in steps:
        # skip the own step
        if s is step:
            continue
        for p in s['param']:
            # if 'value' in p.keys():
            if 'value' in p:
                cp[p['name']] = p['value']

    # if the step parameter are in any other step, take them out since
    # we rather want to calibrate them
    for p in step['param']:
        if p['name'] in cp:
            cp.pop(p['name'])

    return cp


def annotate_step(best_cost, pos, steps, index):
    """Annotate the step with the best value"""

    step = steps[index]
    step['cost'] = best_cost
    for i, p in enumerate(step['param']):
        p['value'] = pos[i]


def check_url(url):
    """Check is the Url is valid."""

    r = requests.head(url)
    if r.status_code != 200:
        raise Exception('Error code {} from Url: "{}"'.format(r.status_code, url))
