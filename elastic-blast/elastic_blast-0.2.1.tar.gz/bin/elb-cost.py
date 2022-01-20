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
*NCBI internal application*
Application for reporting GCP/AWS costs. 
In GCP it runs BigQuery queries on a billing data set looking for resources
with a specific run-label and reports aggregate
cost.

In AWS, it produces a rough estimate based on the runtime, machine type, number
of machines and on-demand cost. This is a first draft implementation.

Author: Greg Boratyn boratyng@ncbi.nlm.nih.gov
        Christiam Camacho camacho@ncbi.nlm.nih.gov
"""

import sys, os
import argparse, json
import boto3
import datetime
import getpass
from botocore.exceptions import ClientError

from elastic_blast import VERSION
from elastic_blast.constants import CLUSTER_ERROR, PERMISSIONS_ERROR
from elastic_blast.cost import get_cost, DFLT_BQ_DATASET, DFLT_BQ_TABLE
from elastic_blast.cost import BQ_ERROR, NO_RESULTS_ERROR, CMD_ARGS_ERROR
from elastic_blast.util import SafeExecError, UserReportError
from elastic_blast.aws import handle_aws_error
import elastic_blast.gcp
from elastic_blast.elb_config import generate_cluster_name

DFLT_GCP_PROJECT='nihsgcnlmncbi'

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(prog=os.path.basename(os.path.splitext(sys.argv[0])[0]), 
                                     description='NCBI-only ElasticBLAST cost reporting application.')
    aws_options = parser.add_argument_group('AWS options')
    aws_options.add_argument("--run-summary", metavar='RUN_SUMMARY_OUTPUT_FILE',
                        help='Provides ElasticBLAST configuration to produce an ESTIMATE of the on-demand compute cost, available as soon as elastic-blast completes, but supports limited instance types. Overrides all other arguments!',
                        type=argparse.FileType('r'))
    aws_mutex_group = aws_options.add_mutually_exclusive_group()
    aws_mutex_group.add_argument('--aws-cluster-name', type=str,
                        help='AWS Cluster name')
    aws_mutex_group.add_argument('--aws-results', type=str,
                        help="AWS Results URI, used in conjunction with caller's username to build cluster name")


    gcp_options = parser.add_argument_group('GCP options')
    gcp_options.add_argument(metavar='RUN_LABEL', dest='run_label', type=str,
                        nargs='?', default='ignore-me',
                        help='Run-label, must be of the form <key>:<value>. Ignored if --run-summary is provided')
    gcp_options.add_argument('--table', metavar='STRING', dest='table', type=str,
                        default=DFLT_BQ_TABLE, help='BigQuery table to search, default=' + DFLT_BQ_TABLE)
    gcp_options.add_argument('--project', metavar='STRING', dest='project', type=str,
                        default=DFLT_GCP_PROJECT,
                        help='GCP project that holds billing data, default=' + DFLT_GCP_PROJECT)
    gcp_options.add_argument('--dataset', metavar='STRING', dest='dataset',
                        type=str, default=DFLT_BQ_DATASET,
                        help='BigQuery dataset to search for costs, default=' + DFLT_BQ_DATASET)

    parser.add_argument('--date-range', metavar='STRING', dest='date_range',
                        type=str, help='Search for costs only between given '
                        ' dates. Date range format: yyyy-mm-dd:yyyy-mm-dd.'
                        ' Using date range makes search faster and'
                        ' cheaper.')
    parser.add_argument('--verbose', dest='verbose', action='store_true',
                        help='Print additional information')
    parser.add_argument('--version', action='version',
                        version='%(prog)s ' + VERSION)
    return parser.parse_args()

def main():
    """The main function, entry point of the program"""
    # parse command line parameters
    args = parse_arguments()
    if args.run_summary or args.aws_cluster_name or args.aws_results:
        return aws_cost(args)
    else:
        return gcp_cost(args)


def get_aws_cost_per_sec_for_instance_type(instance_type: str, on_demand: bool = True) -> float:
    ''' Returnes the cost per second for a given AWS instance type '''
    if not on_demand:
        raise NotImplementedError('Getting cost for instances other than on_demand is not supported')
    retval = .0
    # Data mined from https://ec2instances.info/ on 2021-01-27, based on files in share/etc/*ini
    if instance_type == 'm5.8xlarge':
        retval = 1.536/3600.
    elif instance_type == 'm5.16xlarge':
        retval = 3.072/3600.
    elif instance_type == 'r5n.16xlarge':
        retval = 4.768/3600.
    else:
        raise NotImplementedError(f'Getting on-demand cost for {instance_type} instance type is not supported')
    return retval


def aws_cost(args):
    """ Process the cost estimation request for AWS """
    if args.aws_cluster_name or args.aws_results:
        return aws_cost_by_cluster(args)
    else:
        return aws_cost_by_run_summary(args)


def aws_cost_by_run_summary(args):
    """ Process the cost estimation request for AWS """
    returncode = 0
    if not args.run_summary:
        # just a bit of defensive programming
        print('ERROR: run-summary output file not provided', file=sys.stderr)
        return CMD_ARGS_ERROR

    data = json.load(args.run_summary)
    instance_type = data['clusterInfo']['machineType']
    runtime_in_secs = data['runtime']['wallClock']
    num_instances = data['clusterInfo']['numMachines']
    cost_per_second = get_aws_cost_per_sec_for_instance_type(instance_type)
    cost = [ cost_per_second * runtime_in_secs * num_instances ]

    print('WARNING: this is an ESTIMATE for compute only that assumes on demand cost')
    print('${:.2f}'.format(sum(cost)))
    return returncode


@handle_aws_error
def _aws_cost_by_cluster(cluster_name, start_time, end_time):
    """ Calculate cost by calling AWS Cost Explorer API
        Parameters:
            cluster_name - name of CloudFormation ComputeEnvironment to query cost for
            start_time   - start time (with DAILY granularity) to query 
            end_time     - end time (with DAILY granularity) to query 
        Return:
            cost in dollars
    """
    cost = 0.0
    ce = boto3.client('ce')
    res_d = ce.get_cost_and_usage(Granularity='DAILY', TimePeriod={'Start':start_time,'End':end_time},
        Metrics=['UnblendedCost'],
        Filter={'Tags': {'Key':'Name','Values':[cluster_name],'MatchOptions':['EQUALS']}})
    if 'ResultsByTime' in res_d:
        for res in res_d['ResultsByTime']:
            period_cost = float(res['Total']['UnblendedCost']['Amount'])
            cost += period_cost
    return cost


def aws_cost_by_cluster(args):
    returncode = 0
    cost = 0.0
    cluster_name = ''
    if args.aws_cluster_name:
        cluster_name = args.aws_cluster_name
    else:
        cluster_name = generate_cluster_name(args.aws_results)
    if args.date_range:
        start_time, end_time = args.date_range.split(':')
    else:
        end_time = datetime.date.today().strftime('%Y-%m-%d')
        start_time = (datetime.date.today() - datetime.timedelta(days=45)).strftime('%Y-%m-%d')

    try:
        cost = _aws_cost_by_cluster(cluster_name, start_time, end_time)
    except RuntimeError as e:
        returncode = e.args[0]
        print(e.args[1], file=sys.stderr)
    except ValueError as e:
        returncode = 1
        print(e)
    except UserReportError as e:
        returncode = e.returncode
        print(e.message)
    else:
        print('${:.2f}'.format(cost))
    return returncode


def gcp_cost(args):
    """ Process the cost estimation request for GCP """

    # run-label is a mandatory parameter for GCP only
    if not args.run_label:
        print('ERROR: Run-label not provided', file=sys.stderr)
        return CMD_ARGS_ERROR

    # save current default GCP project
    original_project = None
    try:
        original_project = elastic_blast.gcp.get_gcp_project()
    except (SafeExecError, RuntimeError) as err:
        print('Error: Could not get current GCP project')
        print(err, file=sys.stderr)
        # quit if GCP project cannot be aquired
        return BQ_ERROR

    # switch to user supplied GCP project only if current project is unset or
    # different from the supplied one
    if original_project is None or original_project != args.project:
        try:
            elastic_blast.gcp.set_gcp_project(args.project)
        except SafeExecError as err:
            print(err, file=sys.stderr)
            # exit if project cannot be set
            return BQ_ERROR

    # query GCP for the cost
    returncode = 0
    try:
        cost = get_cost(args.run_label, args.date_range, args.dataset, args.table,
                        args.verbose)
    except ValueError as e:
        print(f'Error: {e}', file=sys.stderr)
        return CMD_ARGS_ERROR
    except RuntimeError as e:
        print(f'{e}', file=sys.stderr)
        return BQ_ERROR
    finally:
        # swicth GCP project back to the old one only if it was set to a
        # different value than args.project
        if original_project is not None and original_project != args.project:
            try:
                elastic_blast.gcp.set_gcp_project(original_project)
            except SafeExecError as err:
                print(f'Error: Could not set original GCP project: {original_project}',
                      file=sys.stderr)
                print(err, file=sys.stderr)
                # there may be userful output, so no need to exit yet
                returncode = BQ_ERROR

    if not cost:
        print(f'Error: There are no results for run labeled "{args.run_label}". Please, make sure that run-label is spelled correctly, you are using the correct GCP project, BigQuery dataset, and table, as well as date range, if used was set properly.', file=sys.stderr)
        return NO_RESULTS_ERROR

    # We could have summed the cost in SQL, but then we would not be able to
    # tell the difference between zero cost and no records found.
    print('${:.2f}'.format(sum(cost)))
    return returncode

        
if __name__ == '__main__':
    sys.exit(main())
