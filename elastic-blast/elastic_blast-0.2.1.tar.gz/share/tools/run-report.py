#!/usr/bin/env python3
#                           PUBLIC DOMAIN NOTICE
#              National Center for Biotechnology Information
#  
# This software is a "United States Government Work" under the
# terms of the United States Copyright Act.  It was written as part of
# the authors' official duties as United States Government employees and
# thus cannot be copyrighted.  This software is freely available
# to the public for use.  The National Library of Medicine and the U.S.
# Government have not placed any restriction on its use or reproduction.
#   
# Although all reasonable efforts have been taken to ensure the accuracy
# and reliability of the software and data, the NLM and the U.S.
# Government do not and cannot warrant the performance or results that
# may be obtained by using this software or data.  The NLM and the U.S.
# Government disclaim all warranties, express or implied, including
# warranties of performance, merchantability or fitness for any particular
# purpose.
#   
# Please cite NCBI in any work or product based on this material.

"""
Script to build execution time and cost reports from results of
run summary and elb-cost.

N.B.: This tool is for internal NCBI usage at this time.

Author: Victor Joukov joukovv@ncbi.nlm.nih.gov
"""

import os
import re
import sys
import argparse
import subprocess
import shlex
import json
import logging
import shutil
from typing import Union, List


def safe_exec(cmd: Union[List[str], str]) -> subprocess.CompletedProcess:
    """Wrapper around subprocess.run that raises SafeExecError on errors from
    command line with error messages assembled from all available information"""
    if isinstance(cmd, str):
        cmd = shlex.split(cmd)
    if not isinstance(cmd, list):
        raise ValueError('safe_exec "cmd" argument must be a list or string')

    try:
        logging.debug(' '.join(cmd))
        p = subprocess.run(cmd, check=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        msg = f'The command "{" ".join(e.cmd)}" returned with exit code {e.returncode}\n{e.stderr.decode()}\n{e.stdout.decode()}'
        if e.output is not None:
            '\n'.join([msg, f'{e.output.decode()}'])
            raise RuntimeError(e.returncode, msg)
    return p


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(prog=os.path.basename(os.path.splitext(sys.argv[0])[0]),
                                     description='Report time and cost summary for set of runs')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-l', '--config_list', metavar='FILE_NAME',
                        help='2-column file with config files and result bucket URIs, one, per line',
                        type=argparse.FileType('r'))
    group.add_argument('-c', '--cfg', metavar='ELASTIC_BLAST_CONFIG_FILE',
                        help='ElasticBLAST configuration file',
                        type=argparse.FileType('r'))
    parser.add_argument('-r', '--results', help='URI for ElasticBLAST results')
    parser.add_argument('-o', '--out', metavar='FILE', type=argparse.FileType(mode='w'),
                        help='Output file. Default: stdout', default='-')
    parser.add_argument('-f', '--outfmt', type=str, default='txt',
                        choices=["txt", "csv", "tsv", "jira"])
    return parser.parse_args()

def parse_config_list(f, outfmt, out):
    for line in f:
        parts = line.strip().split()
        config=parts[0]
        results=None
        description=None
        if len(parts) >= 2:
            results=parts[1]
        if len(parts) >= 3:
            description=parts[2]
        report(config, outfmt, out, results, description)


def get_path_to_executable(exe):
    retval = shutil.which(exe)
    if retval is None:
        retval = shutil.which(f'{exe}.py')
    if retval is None:
        raise RuntimeError(f"Cannot find {exe} on PATH")
    return retval


def report(cfg, outfmt, out, results=None, description=None):
    elb = get_path_to_executable("elastic-blast")
    elb_cost = get_path_to_executable("elb-cost")

    cmd = [elb, 'run-summary', '--cfg', cfg]
    if results:
        cmd.append('--results')
        cmd.append(results)
    p = safe_exec(cmd)

    o = json.loads(p.stdout.decode())
    wall_clock = str(o['runtime']['wallClock'])
    cost = str(0.0)
    cluster_name = 'N/A'
    csp = o['clusterInfo']['provider']
    cmd = [ elb_cost ]
    if csp == 'AWS':
        if 'name' in o['clusterInfo'] and len(o['clusterInfo']['name']) > 0:
            cluster_name = o['clusterInfo']['name']
            cmd.append('--aws-cluster-name')
            cmd.append(cluster_name)
        elif results:
            cmd.append('--aws-results')
            cmd.append(results)
        else:
            raise RuntimeError(f'Cannot compute cost for {cfg}')
    else:
        #cmd.append(f'owner:{}')
        # FIXME: use date
        cmd.append('--help')

    p = safe_exec(cmd)
    res = p.stdout.decode()
    mo = re.search(r'[$](\d+.\d*)', res)
    if mo:
        cost = '$' + str(mo.group(1))
    if description is not None:
        if outfmt == 'txt':
            print(f'Cluster {cluster_name}, Description {description}, time {wall_clock}, cost {cost}, provider {csp}', file=out)
        elif outfmt in ('csv', 'tsv', 'jira'):
            separator = {'csv': ',', 'tsv': '\t', 'jira': '|'}[outfmt]
            if outfmt == 'jira':
                fields = ['', cluster_name, description, wall_clock, cost, csp, '']
            else:
                fields = [cluster_name, description, wall_clock, cost, csp]
            print(separator.join(fields), file=out)
    else:
        if outfmt == 'txt':
            print(f'Cluster {cluster_name}, time {wall_clock}, cost {cost}, provider {csp}', file=out)
        elif outfmt in ('csv', 'tsv', 'jira'):
            separator = {'csv': ',', 'tsv': '\t', 'jira': '|'}[outfmt]
            if outfmt == 'jira':
                fields = ['', cluster_name, wall_clock, cost, csp, '']
            else:
                fields = [cluster_name, wall_clock, cost, csp]
            print(separator.join(fields), file=out)


def main():
    """The main function, entry point of the program"""
    args = parse_arguments()
    if args.outfmt == 'jira':
        print('||Cluster||Runtime(s)||Cost($)||Provider||', file=args.out)
    if args.config_list:
        parse_config_list(args.config_list, args.outfmt, args.out)
    else:
        report(args.cfg.name, args.outfmt, args.out, args.results)
    return 0


if __name__ == '__main__':
    sys.exit(main())
