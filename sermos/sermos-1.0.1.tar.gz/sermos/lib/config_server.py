""" A *local* configuration server to serve local pipeline and schedule configs.

This should be used for development purposes only.

Note: `deployment_id` is unused in all endpoints but is included in this
development server for full compatibility with Sermos managed deployments.
"""
import json
import yaml
import logging
from typing import Union
from marshmallow.exceptions import ValidationError
from flask import Flask, request, jsonify
from rho_web.response import abort
from sermos.schedule_config_schema import BaseScheduleSchema

logger = logging.getLogger(__name__)
api = Flask(__name__)
PREFIX = '/api/v1'


def set_api_config(base_dir: str = None,
                   pipelines_yaml: str = None,
                   schedules_json: str = None):
    """ Establish baseline api configuration (where to find config files)
    """
    api.config.update(
        BASE_DIR=base_dir if base_dir else 'dev',
        PIPELINES_YAML=pipelines_yaml if pipelines_yaml else 'pipelines.yaml',
        SCHEDULES_JSON=schedules_json if schedules_json else 'schedules.json')


set_api_config()  # Set by default, can overload manually before starting


def _retrieve_schedules() -> Union[dict, None]:
    """ Load local schedules.json file
    """
    filename = api.config['BASE_DIR'] + '/' + api.config['SCHEDULES_JSON']
    with open(filename, 'r') as f:
        schedules = json.loads(f.read())
    return schedules


def _save_schedules(schedules: dict) -> Union[dict, None]:
    """ Save local schedules.json file
    """
    filename = api.config['BASE_DIR'] + '/' + api.config['SCHEDULES_JSON']
    with open(filename, 'w') as f:
        f.write(json.dumps(schedules))


def _retrieve_pipelines() -> Union[dict, None]:
    """ Load local pipelines.yaml and load a specific pipeline configuration.
    """
    filename = api.config['BASE_DIR'] + '/' + api.config['PIPELINES_YAML']
    with open(filename, 'r') as f:
        pipelines = yaml.safe_load(f.read())
    return pipelines


def _retrieve_pipeline(pipeline_id: str) -> Union[dict, None]:
    """ Load local pipelines.yaml and load a specific pipeline configuration.
    """
    pipelines = _retrieve_pipelines()
    for pipeline in pipelines['pipelines']:
        if pipeline['metadata']['pipelineId'] == pipeline_id:
            return pipeline
    return None


@api.route(PREFIX + '/deployments/<string:deployment_id>/schedule_tasks',
           methods=['GET'])
def get_schedules(deployment_id: str):
    """ Load local schedules.json file.
    """
    logger.debug(f"Retrieving schedules for {deployment_id}")

    schedules = _retrieve_schedules()
    try:
        BaseScheduleSchema().load(schedules)
    except Exception as e:
        logger.error(f"Error retrieving schedules: {e}")
        abort(400, message=e)
    return jsonify(schedules)


@api.route(PREFIX + '/deployments/<string:deployment_id>/schedule_tasks/'
           '<string:task_id>',
           methods=['POST'])
def update_schedules(deployment_id: str):
    """ Update local schedules.json file with values from provided schedule.

    Primarily this is intended to keep the last_run_at and total_run_count
    values up to date.
    """
    logger.debug(f"Updating schedules for {deployment_id}")

    new_schedules = json.loads(request.data)  # Schedules with updates
    schedules = _retrieve_schedules()  # Schedules known to Sermos
    update_vars = ('last_run_at', 'total_run_count')
    for s in schedules['schedules']:
        for new_s in new_schedules['schedules']:
            if s['name'] == new_s['name']:
                for var in update_vars:
                    s[var] = new_s[var]
    try:
        scs = BaseScheduleSchema()
        scs.load(schedules)  # Validate new schedule
    except ValidationError:
        abort(400, message="Invalid new schedule ...")

    _save_schedules(schedules)

    return jsonify({'message': 'Schedules updated ...'})


@api.route(PREFIX + '/deployments/<string:deployment_id>/pipelines',
           methods=['GET'])
def get_pipelines(deployment_id: str):
    """ Load local pipelines.yaml file
    """
    logger.debug(f"Retrieving pipelines for {deployment_id}")

    pipelines = _retrieve_pipelines()

    # Transform into what we expect from Cloud API server. The local
    # pipelines.yaml file format is for your own development and reference
    # if you choose to deploy independently.
    retval = []
    for pipeline in pipelines['pipelines']:
        retval.append(pipeline)
    return jsonify({'data': {'results': retval}})


@api.route(PREFIX + '/pipelines/<string:deployment_id>/<string:pipeline_id>',
           methods=['GET'])
def get_pipeline(deployment_id: str, pipeline_id: str):
    """ Load local pipeline.yaml and retrieve a specific pipeline.
    """
    logger.debug(f"Retrieving pipeline for {deployment_id} / {pipeline_id}")

    pipeline = _retrieve_pipeline(pipeline_id)

    if pipeline is not None:
        return jsonify({'data': pipeline})
    return jsonify({}), 404


@api.route(PREFIX + '/auth', methods=['POST'])
def validate_access_key():
    """ Validate a provided API key.

    NOTE: This is a *mock* endpoint, no actual validation occurs.
    """
    access_key = request.headers.get('accesskey', None)
    if access_key is None:
        abort(401)
    return jsonify({})
