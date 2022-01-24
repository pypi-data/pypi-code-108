#!python

import os
import sys

cur_file_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append('/opt')
sys.path.append('/opt/app')

import json

# noinspection PyUnresolvedReferences, PyPackageRequirements
from pipeline import pipeline



if __name__ == '__main__':

    nodename = os.getenv('NODENAME')
    assert nodename, "needs NODENAME env var"

    client_id = os.environ.get('HOSTNAME')
    print(f'client_id: {client_id}')
     
    # read nodes
    with open('pipeline.json', 'r') as fp:
        pipeline_cfg = json.load(fp)

    nodes = pipeline_cfg['nodes']

    # run instance with cfg
    instance = pipeline.nodes[nodename]()    
    instance.start(None)
