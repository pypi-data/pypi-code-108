""" General utilities used frequently in configuration-related tasks.

More specifically, these are methods that help interact with Pipeline and
Schedule configurations that originate from your `sermos.yaml` file. These
utility functions make it easy to switch between `local` and `cloud` modes
based on the value of `DEFAULT_BASE_URL` in your environment.

- If the base url is `local`, then all config tasks will read directly from
your local `sermos.yaml` file. Update operations will *not* do anything (that
is, your sermos.yaml file will not be updated).

- If the base url is anything other than `local`, this will assume a cloud
api url was provided (if None is set in environment, Sermos will default to
the Sermos Cloud base API assuming this is a Sermos Cloud deployment). You can
provide your own cloud API endpoints if desired, look to documentation for best
practices.

TODO Need to remove the dependency on Redis and make caching behavior optional.
"""
import os
import logging
import json
from typing import Union, Any
from urllib.parse import urljoin
import requests
from rhodb.redis_conf import RedisConnector
from sermos.constants import DEFAULT_BASE_URL, PIPELINE_CONFIG_CACHE_KEY, \
    SCHEDULE_CONFIG_CACHE_KEY, CONFIG_REFRESH_RATE, USING_SERMOS_CLOUD, \
    LOCAL_DEPLOYMENT_VALUE, DEFAULT_CONFIG_RETRIEVAL_PAGE_SIZE
from sermos.sermos_yaml import load_sermos_config
from sermos.pipeline_config_schema import BasePipelineSchema
from sermos.schedule_config_schema import BaseScheduleSchema

logger = logging.getLogger(__name__)
redis_conn = RedisConnector().get_connection()


def get_access_key(access_key: Union[str, None] = None,
                   env_var_name: str = 'SERMOS_ACCESS_KEY'):
    """ Simple helper to get admin server access key in a standard fashion. If
    one is provided, return it back. If not, look in environment for
    `env_var_name`. If that doesn't exist, raise useful error.

    If this is a local deployment, no access key is required/relevant,
    so simply return 'local'
    """
    if access_key is not None:
        return access_key

    if not USING_SERMOS_CLOUD:
        return LOCAL_DEPLOYMENT_VALUE  # e.g. 'local'

    try:
        return os.environ[env_var_name]
    except KeyError:
        raise KeyError(
            f"{env_var_name} not found in this environment. Find a valid "
            "access key in your Sermos Cloud administration console.")


# TODO cast to UUID?
def get_deployment_id(deployment_id: Union[str, None] = None,
                      env_var_name: str = 'SERMOS_DEPLOYMENT_ID'):
    """ Simple helper to get the deployment id in a standard fashion. Look in
    the environment for `env_var_name`. If that doesn't exist, raise useful
    error.

    If this is a local deployment, no deployment id is required/relevant,
    so this will simply return 'local' in the event the DEFAULT_BASE_URL is
    set to the LOCAL_DEPLOYMENT_VALUE ('local' by default) in the environment.
    """
    if deployment_id is not None:
        return deployment_id

    if not USING_SERMOS_CLOUD:
        return LOCAL_DEPLOYMENT_VALUE  # e.g. 'local'

    try:
        return os.environ[env_var_name]
    except KeyError:
        raise KeyError(
            f"{env_var_name} not found in this environment. Note: this is "
            "required when running a Celery worker as `beat`. Find this ID "
            "in your administration console. For local development, this can "
            "be any arbitrary string.")


def load_json_config_from_redis(key: str) -> Any:
    """ Load a json key from redis. Special carve out for keys explicitly set
    to "none".
    """
    val = redis_conn.get(key)
    if val is None or val.decode('utf-8').lower() == 'none':
        return None
    return json.loads(val)


def set_json_config_to_redis(key: str,
                             data: Union[dict, None],
                             refresh_rate: int = CONFIG_REFRESH_RATE):
    """ For Admin API actions (e.g. schedules/pipelines), deployments cache
    results. The standard method for doing this is through a refresh key, which
    is set in redis to expire after the CONFIG_REFRESH_RATE. This will set
    the cached key.

    Rationale for manually setting a "None" key instead of simply skipping
    is to protect against case of a spammed config request for an unknown
    pipeline, for example. This will still limit our requests to Sermos Cloud
    based on the refresh rate even in that scenario.
    """
    if data is None:
        data = 'None'
    else:
        data = json.dumps(data)

    redis_conn.setex(key, refresh_rate, data)


def _generate_api_url(endpoint: str = ''):
    """ Provide a normalized url based on the base url and endpoint and add in
    the deployment_id to the url, which is required for all default
    pipeline/schedule endpoints if using Sermos Cloud.

    The Sermos Cloud API spec bases everything on the notion of `deployments`,
    so if you are rolling your own 'non-local' API, you will need to mock this
    concept in order to use the built in helper functions for retrieving
    pipelines and schedules from an API source.
    """
    deployment_id = get_deployment_id()  # From env if None
    return urljoin(DEFAULT_BASE_URL, f'deployments/{deployment_id}/{endpoint}')


def _retrieve_and_cache_config(key: str,
                               admin_api_endpoint: str,
                               access_key: str,
                               refresh_rate: int = CONFIG_REFRESH_RATE) -> Any:
    """ Attempt to load a configuration (pipeline/schedule) from cache If not available,
    retrieve API response from Sermos Config Server and cache the response for
    CONFIG_REFRESH_RATE seconds in local Redis.
    """
    conf = load_json_config_from_redis(key)
    if conf is not None:
        return conf

    # Ask Sermos Cloud (Note: Sermos Cloud's API expects `apikey`)
    headers = {
        'apikey': access_key,
    }

    params = {
        'page_size': DEFAULT_CONFIG_RETRIEVAL_PAGE_SIZE,
        'page': 1
    }

    r = requests.get(admin_api_endpoint, headers=headers, verify=True,
                     params=params)

    data = None
    if r.status_code == 200:
        data = r.json()
    else:
        logger.warning(f"Non-200 response retrieving {admin_api_endpoint}: "
                       f"{r.status_code}, {r.reason}")

    # There's a chance we need to request ALL schedule configs from sermos cloud
    # for the scheduled tasks.  Lets loop and grab all of them.
    while key == SCHEDULE_CONFIG_CACHE_KEY and \
            len(data['data']['results']) < data['data']['count']:
        params['page'] += 1
        r = requests.get(admin_api_endpoint, headers=headers, verify=True,
                         params=params)
        if r.status_code == 200:
            paginated_data = r.json()
            data['data']['results'] = data['data']['results'] + \
                                      paginated_data['data']['results']
        else:
            logger.warning(f"Non-200 response retrieving {admin_api_endpoint}: "
                       f"{r.status_code}, {r.reason}")
            break

    # Cache result
    if data is not None:
        set_json_config_to_redis(key, data, refresh_rate)

    return data


def retrieve_latest_pipeline_config(
        pipeline_id: Union[str, None] = None,
        access_key: Union[str, None] = None,
        refresh_rate: int = CONFIG_REFRESH_RATE) -> Union[dict, list]:
    """ Retrieve the 'latest' pipeline configuration.

    Sermos can be deployed in 'local' mode by setting DEFAULT_BASE_URL=local
    in your environment. In this case, Sermos will retrieve the latest
    configuration from the local filesystem, specifically looking inside the
    sermos.yaml file.

    If the DEFAULT_BASE_URL is anything else, this will assume that it is a
    valid API base url and make a request. The request will be formatted to
    match what Sermos Cloud expects for seamless Sermos Cloud deployments.
    However, you can provide any base url and stand up your own API if desired!

    This utilizes redis (required for Sermos-based pipelines/scheduled tasks)
    to cache the result for a predetermined amount of time before requesting an
    update. This is because pipelines/tasks can be invoked rapidly but do not
    change frequently.
    """
    # If this is a LOCAL deployment, look to sermos.yaml directly
    if not USING_SERMOS_CLOUD:
        sermos_config = load_sermos_config()
        if 'pipelines' in sermos_config:
            pipelines = []
            found_pipeline = None
            for p_id, config in sermos_config['pipelines'].items():
                config['sermosPipelineId'] = p_id
                if pipeline_id == p_id:
                    found_pipeline = config
                    break
                pipelines.append(config)

            if pipeline_id:
                if found_pipeline:
                    return found_pipeline
                raise ValueError(f'Invalid pipeline {pipeline_id}')

            return pipelines
        return None

    # If this is a CLOUD deployment, generate a valid API url and ask the API
    # service for pipeline configuration. If this deployment is set up to
    # cache results, do so.
    cache_key = PIPELINE_CONFIG_CACHE_KEY.format(pipeline_id)
    access_key = get_access_key(access_key)  # From env if None

    # Generate pipeline specific API endpoint. If pipeline_id
    # is None, then we're asking for 'all' pipelines.
    api_url = _generate_api_url('pipelines')
    if pipeline_id is not None:
        api_url = urljoin(api_url + '/', pipeline_id)  # Add pipeline ID

    # Retrieve (and cache) result - this will be the exact result from the
    # API response.
    data = _retrieve_and_cache_config(cache_key, api_url, access_key,
                                      refresh_rate)
    if data:
        if pipeline_id:
            return data['data']
        return data['data']['results']
    return None


def retrieve_latest_schedule_config(access_key: Union[str, None] = None,
                                    refresh_rate: int = CONFIG_REFRESH_RATE):
    """ Retrieve the 'latest' scheduled tasks configuration.

    Sermos can be deployed in 'local' mode by setting DEFAULT_BASE_URL=local
    in your environment. In this case, Sermos will retrieve the latest configuration
    from the local filesystem, specifically looking inside the sermos.yaml file.

    If the DEFAULT_BASE_URL is anything else, this will assume that it is a valid
    API base url and make a request. The request will be formatted to match what
    Sermos Cloud expects for seamless Sermos Cloud deployments. However, you can
    provide any base url and stand up your own API if desired!

    This utilizes redis (required for Sermos-based pipelines/scheduled tasks) to
    cache the result for a predetermined amount of time before requesting an
    update. This is because pipelines/tasks can be invoked rapidly but do not
    change frequently.
    """
    if not USING_SERMOS_CLOUD:
        sermos_config = load_sermos_config()
        if 'scheduledTasks' in sermos_config:
            tasks = []
            for task_id, config in sermos_config['scheduledTasks'].items():
                config['sermosScheduledTasksId'] = task_id
                tasks.append(config)
            return tasks
        return None

    cache_key = SCHEDULE_CONFIG_CACHE_KEY
    access_key = get_access_key(access_key)  # From env if None

    api_url = _generate_api_url('scheduled_tasks')

    data = _retrieve_and_cache_config(cache_key, api_url, access_key,
                                      refresh_rate)

    schedules = []
    for schedule in data['data']['results']:
        ScheduleSchema = \
            BaseScheduleSchema.get_by_version(schedule['schemaVersion'])
        schema = ScheduleSchema()
        _schedule = schema.load(schedule)
        _schedule['id'] = schedule['id']
        schedules.append(_schedule)

    return schedules


def update_schedule_config(new_schedule_config: dict,
                           access_key: Union[str, None] = None,
                           schedule_config_endpoint: Union[str, None] = None):
    """ Tell Sermos to update a deployment's schedule with new version.
    """

    # Don't send status to sermos-cloud if we're running in local mode
    if not USING_SERMOS_CLOUD:
        return True

    access_key = get_access_key(access_key)  # From env if None
    api_url = _generate_api_url('scheduled_tasks')

    # Ask Sermos Cloud (Note: Sermos Cloud's API expects `apikey`)
    headers = {'apikey': access_key}

    for scheduled_task in new_schedule_config['schedules']:
        copy_task = dict(scheduled_task)
        task_id = copy_task.pop('id')
        url = f"{api_url}/{task_id}"
        r = requests.put(url, json=copy_task, headers=headers, verify=True)
        if r.status_code != 200:
            logger.error("Unable to update schedule task in sermos cloud")
            logger.error(r.json())
            return False

    return True
