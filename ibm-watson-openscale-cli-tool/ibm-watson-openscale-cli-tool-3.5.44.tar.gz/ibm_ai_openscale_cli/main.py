# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

# coding=utf-8
from __future__ import print_function
import argparse
import logging
import os
import platform
import warnings
from urllib3.exceptions import InsecureRequestWarning

from ibm_ai_openscale_cli import logging_temp_file
from ibm_ai_openscale_cli.enums import ResetType, MLEngineType
from ibm_ai_openscale_cli.environments import Environments
from ibm_ai_openscale_cli.openscale_ops import OpenScaleOps
from ibm_ai_openscale_cli.reset_ops import ResetOps
from ibm_ai_openscale_cli.utility_classes.fastpath_logger import FastpathLogger, TIMER

logger = FastpathLogger(__name__)

SERVICE_NAME = 'Watson OpenScale'

with open(os.path.join(os.path.dirname(__file__), 'VERSION'), 'r') as f_ver:
    __version__ = f_ver.read()


def get_argument_parser():
    """
    generate a CLI arguments parser
    Returns:
       argument parser
    """
    description = 'IBM Watson Openscale "express path" configuration tool. This tool allows the user to get started quickly with Watson OpenScale: 1) If needed, provision a Lite plan instance for IBM Watson OpenScale\n2) If needed, provision a Lite plan instance for IBM Watson Machine Learning\n3) Drop and re-create the IBM Watson OpenScale datamart instance and datamart database schema\n4) Optionally, deploy a sample machine learning model to the WML instance\n5) Configure the sample model instance to OpenScale, including payload logging, fairness checking, feedback, quality checking, and explainability\n6) Optionally, store up to 7 days of historical payload, fairness, and quality data for the sample model'
    parser = argparse.ArgumentParser(description=description)
    # required parameters
    required_args_group = parser.add_argument_group('required arguments (only one needed)')
    required_args = required_args_group.add_mutually_exclusive_group(required=True)
    required_args.add_argument('-a', '--apikey', help='IBM Cloud platform user APIKey. If "--env icp" is also specified, APIKey value is not used.')
    required_args.add_argument('-i', '--iam-token', help='IBM Cloud authentication IAM token, or IBM Cloud private authentication IAM token. Format can be (--iam-token "Bearer <token>") or (--iam-token <token>)')
    # Optional parameters
    optional_args = parser._action_groups.pop()
    parser.add_argument('--env', default='ypprod', help='Environment. Default "ypprod"', choices=['ypprod', 'frprod', 'ypqa', 'ypcr', 'ys1dev', 'icp'])
    parser.add_argument('--resource-group', default='default', help='Resource Group to use. If not specified, then "default" group is used')
    parser.add_argument('--postgres', help='Path to postgres credentials file for the datamart database. If --postgres, --icd, and --db2 all are not specified, then the internal {} database is used'.format(SERVICE_NAME))
    parser.add_argument('--icd', help='Path to IBM Cloud Database credentials file for the datamart database')
    parser.add_argument('--db2', help='Path to IBM DB2 credentials file for the datamart database')
    parser.add_argument('--cos', help='Path to IBM Cloud Object Storage credentials file')
    # Due to #18825
    parser.add_argument('--wml', help='Path to IBM WML credentials file')
    # parser.add_argument('--azure-studio', help='Path to Microsoft Azure credentials file for Microsoft Azure ML Studio')
    # parser.add_argument('--azure-service', help='Path to Microsoft Azure credentials file for Microsoft Azure ML Service')
    # parser.add_argument('--spss', help='Path to SPSS credentials file')
    # parser.add_argument('--custom', help='Path to Custom Engine credentials file')
    # parser.add_argument('--aws', help='Path to Amazon Web Services credentials file')
    parser.add_argument('--deployment-name', help='Name of the existing deployment to use. Required for Azure ML Studio, SPSS Engine and Custom ML Engine, but optional for Watson Machine Learning. Required for custom models')
    parser.add_argument('--keep-schema', action='store_true', help='Use pre-existing datamart schema, only dropping all tables. If not specified, datamart schema is dropped and re-created')
    parser.add_argument('--username', help='ICP username. Required if "icp" environment is chosen, not required if --iam-token is specified')
    parser.add_argument('--password', help='ICP password. Required if "icp" environment is chosen, not required if --iam-token is specified')
    parser.add_argument('--url', help='ICP url. Required if "icp" environment is chosen')
    parser.add_argument('--datamart-id', help='Specify data mart id, For icp environment, default is "00000000-0000-0000-0000-000000000000"')
    parser.add_argument('--datamart-name', help='Specify data mart name and database schema, default is the datamart database connection username. For internal database, the default is "wosfastpath"')
    parser.add_argument('--history', default=0, help='Days of history to preload. Default is 0', type=int)
    parser.add_argument('--history-only', action='store_true', help='Store history only for existing deployment and datamart. Requires --extend and --deployment-name also be specified')
    parser.add_argument('--history-first-day', default=0, help='Starting day for history. Default is 0', type=int)
    parser.add_argument('--model', default='GermanCreditRiskModel', help='Sample model to set up with Watson OpenScale (default "GermanCreditRiskModel")')
    parser.add_argument('--list-models', action='store_true', help='Lists all available models. If a ML engine is specified, then modesl specific to that engine are listed')
    parser.add_argument('--custom-model', help='Name of custom model to set up with Watson OpenScale. If specified, overrides the value set by --model. Also requires that --custom-model-directory')
    parser.add_argument('--custom-model-directory', help='Directory with model configuration and metadata files. Also requires that --custom-model be specified')
    parser.add_argument('--extend', action='store_true', help='Extend existing datamart, instead of deleting and recreating it')
    parser.add_argument('--protect-datamart', action='store_true', help='If specified, the setup will exit if an existing datamart setup is found')
    parser.add_argument('--reset', choices=['metrics', 'monitors', 'datamart', 'model', 'all'], help='Reset existing datamart and/or sample models then exit')
    parser.add_argument('--verbose', action='store_true', help='verbose flag')
    parser.add_argument('--wml-plan', default='lite', help='If no WML instance exists, then provision one with the specified plan. Default is "lite", other plans are paid plans', choices=['lite', 'standard', 'professional', 'v2-standard', 'v2-professional'])
    parser.add_argument('--openscale-plan', default='lite', help='If no OpenScale instance exists, then provision one with the specified plan. Default is "lite", other plans are paid plans', choices=['lite', 'standard', 'standard-v2'])
    parser.add_argument('--version', action='version', version='%(prog)s {version}'.format(version=__version__))
    # parser.add_argument('--bkpi', action='store_true', help='Enable Business KPI support, if also specified in the model configuration')
    parser.add_argument('--mrm', action='store_true', help=argparse.SUPPRESS)  # enable MRM support, only used by fastpath service for credit risk model in CP4D with WML v4
    parser.add_argument("--iam-integration", action="store_true", help="To be specified when running in a Cloud Pak for Data environment where IAM integration is enabled.") # Refer #21708 for more details
    parser.add_argument("--bedrock-url", help="The bedrock URL of the Cloud Pak for Data environment for token generation.") # Refer #22439 for more details

    # undocumented optional arguments for use as a client load generator
    parser.add_argument('--v3', action='store_true', help=argparse.SUPPRESS,)
    parser.add_argument('--model-first-instance', default=1, help=argparse.SUPPRESS, type=int)  # First "instance" (copy) of each model. Default 1 means to start with the base model instance
    parser.add_argument('--model-instances', default=1, help=argparse.SUPPRESS, type=int)  # Number of additional instances beyond the first.
    parser.add_argument('--pause-between-models', default=0.0, help=argparse.SUPPRESS, type=float)  # Pause in seconds between main loops. Intended to help stagger fairness checks more evenly.
    parser.add_argument('--skip-scoring-data', action='store_true', help=argparse.SUPPRESS)  # If true, skip using scoring data, even if provided, and instead score from the training data. The default is to use scoring data if provided
    parser.add_argument('--score-sequential', action='store_true', help=argparse.SUPPRESS)  # If true, generate score request values from sequential, not random, rows from the scoring data. The default is to score with random rows
    parser.add_argument('--score-columns', action='store_true', help=argparse.SUPPRESS)  # If true, generate score requests with random values from the scoring/training data columns. The default is to score with values from random rows
    parser.add_argument('--num-scores', default=1, help=argparse.SUPPRESS, type=int)  # Number of live scoring requests to generate. Default is 1
    parser.add_argument('--values-per-score', default=100, help=argparse.SUPPRESS, type=int)  # Number of scores per score request. Default is 100, and value cannot be 0. Values greater than 1 only supported for WML deployments
    parser.add_argument('--pause-between-scores', default=0.0, help=argparse.SUPPRESS, type=float)  # Pause in seconds between score requests. Only applicable to WML deployments
    parser.add_argument('--async-checks', action='store_true', help=argparse.SUPPRESS)  # If true, make fairness and quality checks asynchronous (default is synchronous)
    parser.add_argument('--no-checks', action='store_true', help=argparse.SUPPRESS)  # If true, skip the fairness and quality checks
    parser.add_argument('--num-explains', default=1, help=argparse.SUPPRESS, type=int)  # Number of explain requests. Default is 1
    parser.add_argument('--max-explain-candidates', default=0, help=argparse.SUPPRESS, type=int)  # Maximum number of candidate scores for explain. Default is 0, interpreted to mean the same as the number of explain requests
    parser.add_argument('--explain-start-sync', action='store_true', help=argparse.SUPPRESS)  # After getting explain candidates, user input requred before sending explain requests
    parser.add_argument('--pause-between-explains', default=0.0, help=argparse.SUPPRESS, type=float)  # Pause in seconds between explain requests.
    parser.add_argument('--async-explains', action='store_true', help=argparse.SUPPRESS)  # If true, make explain requests asynchronous (default is synchronous)
    parser.add_argument('--explain-no-cem', action='store_true', help=argparse.SUPPRESS)  # If true, don't include cem "contrastive" explains, but lime only (default is both lime and cem)
    parser.add_argument('--no-new-feedback', action='store_true', help=argparse.SUPPRESS)  # If true, don't upload new feedback data even if available

    # undocumented optional arguments for using credentials json instead of vcap file:
    parser.add_argument('--postgres-json', help=argparse.SUPPRESS)  # Postgres credentials in JSON format
    parser.add_argument('--icd-json', help=argparse.SUPPRESS)  # IBM Cloud Database credentials for the datamart database in JSON format
    parser.add_argument('--db2-json', help=argparse.SUPPRESS)  # IBM DB2 credentials for the datamart database in JSON format:  \'{"username":"<USERNAME>","password":"<PASSWORD>","hostname":"<hostname>","port":"<port>","db":"<db>","ssl":"Optional - set to true if db2 connection should use ssl. Default is false","certificate_base64":"Optional - Base64 encoded SSL certificate, required when using self signed certificates"}\' #pragma: allowlist secret

    # Due to #18825
    # parser.add_argument('--wml-json', help=argparse.SUPPRESS)  # IBM WML credentials in JSON format
    # parser.add_argument('--spss-json', help=argparse.SUPPRESS)  # SPSS credentials in JSON format: \'{ "username": "<USERNAME>", "password": "<PASSWORD", "url": "<URL>" }\' #pragma: allowlist secret
    # parser.add_argument('--custom-json', help=argparse.SUPPRESS)  # Custom Engine credentials in JSON format: \'{ "url": "<URL>" }\'
    # parser.add_argument('--aws-json', help=argparse.SUPPRESS)  # Amazon Web Services credentials in JSON format: \'{ "access_key_id": "<ACCESS_KEY_ID", "secret_access_key": "<SECRET_ACCESS_KEY", "region": "<REGION>" }\'
    # parser.add_argument('--azure-studio-json', help=argparse.SUPPRESS)  # Microsoft Azure credentials in JSON format for Microsoft Azure ML Studio: \'{ "client_id": "<CLIENT_ID", "client_secret": "<CLIENT_SECRET", "tenant": "<TENANT>", "subscription_id": "<SUBSCRIPTION_ID" }\' #pragma: allowlist secret
    # parser.add_argument('--azure-service-json', help=argparse.SUPPRESS)  # Microsoft Azure credentials in JSON format for Microsoft Azure ML Service: \'{ "client_id": "<CLIENT_ID", "client_secret": "<CLIENT_SECRET", "tenant": "<TENANT>", "subscription_id": "<SUBSCRIPTION_ID" }\' #pragma: allowlist secret

    # undocumented optional arguments used for model development
    parser.add_argument('--generate-statistics', action='store_true', help=argparse.SUPPRESS)  # generate to stdout the training_data_statistics.json file based on the configuration.json and training_data.csv
    parser.add_argument('--generate-payload-history', action='store_true', help=argparse.SUPPRESS)  # generate to stdout PayloadRecord json for scoring requests made in this run (if any)
    parser.add_argument('--generate-drift-history', action='store_true', help=argparse.SUPPRESS)  # generate drift history live instead of using history. Also needed for August 2019 GA backward compatibility.

    # other undocumented optional arguments
    parser.add_argument('--training-data-json', help=argparse.SUPPRESS)
    parser.add_argument('--bx', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--organization', help=argparse.SUPPRESS, required=False)
    parser.add_argument('--space', help=argparse.SUPPRESS, required=False)
    parser.add_argument('--summary', action='store_true', help=argparse.SUPPRESS, required=False)  # Generate and print a report of failed metric checks
    parser.add_argument('--database-counts', action='store_true', help=argparse.SUPPRESS, required=False)  # Display counts of all the datamart tables at key points
    parser.add_argument('--timers', action='store_true', help=argparse.SUPPRESS, required=False)  # Display TIMERs to STDOUT, not just log
    parser.add_argument('--subscription-details', action='store_true', help=argparse.SUPPRESS, required=False)  #  save subscription details

    parser._action_groups.append(optional_args)
    return parser


def log_error_raise_exception(error_msg):
    logger.log_error(error_msg)
    raise Exception(error_msg)


def initialize(args):
    """
    Initialize and validate necessary entities
    """
    def _validate_deployment_name_specified(deployment_name, model_name=None, env_name='ypprod'):
        if args.ml_engine_type is MLEngineType.WML:
            if deployment_name and model_name == 'all':
                log_error_raise_exception('ERROR: A model name is required when a deployment is specified for {}'.format(args.ml_engine_type.value))
        else:
            if not args.list_models and not deployment_name:
                log_error_raise_exception('ERROR: A deployment name is required when {} is used with {}'.format(SERVICE_NAME, args.ml_engine_type.value))

    def _validate_is_icp(env_name):
        if not env_name == 'icp':
            log_error_raise_exception('ERROR: {} is only supported on {} on IBM Cloud Private (ICP)'.format(args.ml_engine_type.value, SERVICE_NAME))

    def _validate_db_provided(postgres, icd, db2):
        if not (postgres or icd or db2):
            log_error_raise_exception('ERROR: Database must be provided to setup {} on IBM Cloud Private (ICP)'.format(SERVICE_NAME))

    # token
    if args.iam_token:
        array = args.iam_token.split(' ')
        if array:
            if len(array) == 2 and array[0].lower().startswith('bearer'):
                args.iam_token = array[1]

    # validate environment
    if 'throw' in args:
        log_error_raise_exception(args.throw)

    logging.addLevelName(TIMER,'TIMER')
    if args.verbose:
        logging.getLogger().handlers[1].setLevel(logging.DEBUG)
        logging.getLogger('handle_response').setLevel(logging.DEBUG)
        logging.getLogger('ibm_watson_openscale.utils.client_errors').setLevel(logging.DEBUG)
    elif args.timers:
        logging.getLogger().handlers[1].setLevel(TIMER)
        logging.getLogger('handle_response').setLevel(TIMER)
        logging.getLogger('ibm_watson_openscale.utils.client_errors').setLevel(TIMER)

    # setup the loger
    logger.log_info('ibm-ai-openscale-cli-{}'.format(__version__))
    logger.log_info('Log file: {0}'.format(logging_temp_file.name))

    # initialize args
    args.is_icp = False
    args.service_name = SERVICE_NAME
    if not args.v3:
        args.v4 = True
    # if args.azure_studio or args.azure_studio_json:
    #     args.ml_engine_type = MLEngineType.AZUREMLSTUDIO
    #     _validate_deployment_name_specified(args.deployment_name)
    # elif args.azure_service or args.azure_service_json:
    #     args.ml_engine_type = MLEngineType.AZUREMLSERVICE
    #     _validate_deployment_name_specified(args.deployment_name)
    # elif args.spss or args.spss_json:
    #     args.ml_engine_type = MLEngineType.SPSS
    #     _validate_is_icp(args.env)
    #     _validate_deployment_name_specified(args.deployment_name)
    # elif args.custom or args.custom_json:
    #     args.ml_engine_type = MLEngineType.CUSTOM
    #     _validate_deployment_name_specified(args.deployment_name)
    # elif args.aws or args.aws_json:
    #     args.ml_engine_type = MLEngineType.SAGEMAKER
    #     _validate_deployment_name_specified(args.deployment_name)
    # else:
    #     args.ml_engine_type = MLEngineType.WML
    args.ml_engine_type = MLEngineType.WML
    _validate_deployment_name_specified(args.deployment_name, args.model, args.env)
    env_dict = Environments(args).get_attributes()
    args.env_dict = env_dict
    if args.reset:
        args.reset_type = ResetType(args.reset)
    if args.env == "icp":
        _validate_db_provided(args.postgres, args.icd, args.db2)
        args.is_icp = True
        logger.log_info('SSL verification is not used for requests against ICP Environment, disabling "InsecureRequestWarning"')
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', InsecureRequestWarning)
        if not args.datamart_id:
            args.datamart_id = "00000000-0000-0000-0000-000000000000"
    if args.history_only and (not args.deployment_name or not args.extend):
        log_error_raise_exception('ERROR: --history-only requires that both --extend and --deployment-name also be specified')
    if args.values_per_score > 1 and not args.ml_engine_type == MLEngineType.WML:
        args.num_scores = args.values_per_score * args.num_scores
        args.values_per_score = 1
        logger.log_info('FYI: Only WML supports more than 1 value per score request. Continuing with each value in its own score request')
    if args.values_per_score < 1:
        log_error_raise_exception('ERROR: Values per score request must be at least 1')
    if args.score_sequential and args.score_columns:
        log_error_raise_exception('ERROR: Sequential scoring rows and scoring by columns cannot both be specified')
    if args.mrm and not (args.ml_engine_type == MLEngineType.WML and args.v4
            and (args.model == 'GermanCreditRiskModel' or args.model == 'SmallCreditRiskModel' or args.model == 'MediumCreditRiskModel' )):
        log_error_raise_exception('ERROR: --mrm only supported for WML v4 GermanCreditRiskModel, SmallCreditRiskModel, or MediumCreditRiskModel')


def show_finish_prompt(dashboard_url):
    logger.log_info('Process complete')
    if dashboard_url.startswith('https://api.'):
        dashboard_url = dashboard_url.replace('https://api.', 'https://')
    logger.log_info('The {} dashboard can be accessed at: {}/aiopenscale'.format(SERVICE_NAME, dashboard_url))


def main(arguments=None):

    args = arguments if arguments else get_argument_parser().parse_args()
    initialize(args)

    # operations
    if args.generate_statistics:
        from ibm_ai_openscale_cli.utility_classes.statistics_generator import StatisticsGenerator
        generator = StatisticsGenerator(args)
        logger.log_info(generator.generate_statistics())
    elif args.list_models:
        logger.log_info('\nList of models for {} ...'.format(args.ml_engine_type.value))
        model_names_list = OpenScaleOps(args)._model_names
        for name in model_names_list:
            logger.log_info(' * {}'.format(name))
        logger.log_info('')
    elif args.reset:
        ResetOps(args).execute()
    else:
        OpenScaleOps(args).execute()

    # finish
    show_finish_prompt(args.env_dict['aios_url'])
