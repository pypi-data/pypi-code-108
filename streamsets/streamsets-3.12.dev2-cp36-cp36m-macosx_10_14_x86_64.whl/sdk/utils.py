# Copyright 2019 StreamSets Inc.

"""Assorted utility functions."""

import base64
import copy
import logging
import os
import random
import re
import string
from collections import OrderedDict
from datetime import datetime
from decimal import Decimal
from time import sleep, time

from inflection import camelize

logger = logging.getLogger(__name__)

# These are the current modes for transformer and sdc. Assuming there won't be an overlap between the modes for SDC and
# transformer.
TRANSFORMER_EXECUTION_MODES = {'BATCH', 'STREAMING'}
TRANSFORMER_DEFAULT_EXECUTION_MODE = 'BATCH'
# pipelineType is NOT THE SAME THING as executionMode, even though the value happens to also be a value for executionMode
# see patch in SDC-10960 which introduced this parameter name to the backend
TRANSFORMER_PIPELINE_TYPE = 'STREAMING'
SDC_DEFAULT_EXECUTION_MODE = 'STANDALONE'

# This is hardcoded in domainserver over here https://git.io/Jecwm
DEFAULT_PROVISIONING_SPEC = '''apiVersion: apps/v1
kind: Deployment
metadata:
  name: datacollector-deployment
  namespace: streamsets
spec:
  replicas: 1
  selector:
    matchLabels:
      app: datacollector-deployment
  template:
    metadata:
      labels:
        app: datacollector-deployment
    spec:
      containers:
      - name: datacollector
        image: streamsets/datacollector:latest
        ports:
        - containerPort: 18630
        env:
        - name: HOST
          valueFrom:
            fieldRef:
              fieldPath: status.podIP
        - name: PORT0
          value: "18630"'''


def get_random_string(characters=string.ascii_letters, length=8):
    """
    Returns a string of the requested length consisting of random combinations of the given
    sequence of string characters.
    """
    return ''.join(random.choice(characters) for _ in range(length))


def get_random_file_path(prefix='/tmp', extension='txt'):
    """Returns a random file path with specified prefix and extension

    Args:
        prefix (:obj:`str`, optional): Prefix path. Default: ``'/tmp'``.
        extension (:obj:`str`, optional): File extension to use. Default: ``'txt'``.
    """
    return os.path.join(prefix, '{}.{}'.format(get_random_string, extension))


def join_url_parts(*parts):
    """
    Join a URL from a list of parts. See http://stackoverflow.com/questions/24814657 for
    examples of why urllib.parse.urljoin is insufficient for what we want to do.
    """
    return '/'.join([piece.strip('/') for piece in parts if piece is not None])


def get_params(parameters, exclusions=None):
    """Get a dictionary of parameters to be passed as requests methods' params argument.

    The typical use of this method is to pass in locals() from a function that wraps a
    REST endpoint. It will then create a dictionary, filtering out any exclusions (e.g.
    path parameters) and unset parameters, and use camelize to convert arguments from
    ``this_style`` to ``thisStyle``.
    """
    return {camelize(arg, uppercase_first_letter=False): value
            for arg, value in parameters.items()
            if value is not None and arg not in exclusions}


class VersionSplit:
    """Util function to hold various parts of a version.

    Args:
        name (:obj:`str`)
        delimiter1 (:obj:`str`)
        version (:obj:`str`)
        delimiter2 (:obj:`str`)
        specifier (:obj:`str`)
    """
    __slots__ = ['name', 'delimiter1', 'version', 'delimiter2', 'specifier']
    def __init__(self, name, delimiter1, version, delimiter2, specifier):
        self.name = name
        self.delimiter1 = delimiter1
        self.version = version
        self.delimiter2 = delimiter2
        self.specifier = specifier

    def __iter__(self):
        for attr in self.__slots__:
            yield getattr(self, attr)


class Version:
    """Maven version string abstraction.

    Use this class to enable correct comparison of Maven versioned projects. For our purposes,
    any version is equivalent to any other version that has the same 4-digit version number (i.e.
    3.0.0.0-SNAPSHOT == 3.0.0.0-RC2 == 3.0.0.0).

    Args:
        version (:obj:`str`) or (:obj:`int`) or (:obj:`float`): Version string (e.g. '2.5.0.0-SNAPSHOT').
    """
    # pylint: disable=protected-access,too-few-public-methods
    def __init__(self, version):
        self._pattern = '(^[a-zA-Z]+)?(-)?([\d.]+)(-)?(\w+)?'
        # name (^[a-zA-Z]+) May or may not exist
        # delimiter1 (-)? May or may not exist e.g. - or None
        # version ([\d.]+) Version number e.g. 3.8.2
        # delimiter2 (-)? May or may not exist e.g. - or None
        # specifier (\w*) May or may not exist e.g. RC2

        # Handle the case where version is int or float.
        if isinstance(version, (int, float)):
            version = str(version)

        self._str = version

        groups = re.search(self._pattern, self._str).groups()
        version_split = VersionSplit(*groups)

        # Parse the numeric part of versions.
        numeric_version_list = [int(i) for i in version_split.version.split('.')]

        # Add additional 0's to keep a min length of version. Not so pythonic but, probably is more readable and simple.
        while len(numeric_version_list) < 4:
            numeric_version_list.append(0)

        # Update version_split with appended zeros.
        version_split.version = numeric_version_list

        self._version_split = version_split
        self._tuple = tuple(version_split)

    def __repr__(self):
        return str(self._tuple)

    def __eq__(self, other):
        return (self._version_split.name == other._version_split.name and
                self._version_split.version == other._version_split.version)

    def __lt__(self, other):
        if not isinstance(other, Version):
            raise TypeError('Comparison can only be done for two Version instances.')
        if self._version_split.name != other._version_split.name:
            raise TypeError('Comparison can only be done between two Version instances with same name.')
        return self._version_split.version < other._version_split.version

    def __gt__(self, other):
        return other.__lt__(self)

    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)

    def __le__(self, other):
        return other.__ge__(self)


def sdc_value_reader(value):
    """Helper function which can parse SDC Record value (Record JSON in dict format for example)
    and convert to SDC implied Python collection with necessary types being converted from SDC
    to Python.

    Args:
        value: SDC Record value.

    Returns:
        The value.
    """
    # Note: check instance of OrderedDict before dict to avoid superfluous
    # check of OrderedDict getting evaluated for dict
    type_to_function_map = {"LIST_MAP": lambda x: sdc_value_reader(OrderedDict([(key, x[key])
                                                                                for key in range(len(x))])),
                            "LIST": lambda x: sdc_value_reader(x),
                            "MAP": lambda x: sdc_value_reader(x),
                            "SHORT": lambda x: int(x),
                            "INTEGER": lambda x: int(x),
                            "LONG": lambda x: int(x),
                            "CHAR": lambda x: x,
                            "STRING": lambda x: x,
                            "DATE": lambda x: datetime.utcfromtimestamp(x/1000),
                            "DATETIME": lambda x: datetime.utcfromtimestamp(x/1000),
                            "TIME": lambda x: datetime.utcfromtimestamp(x/1000),
                            "BOOLEAN": lambda x: x,
                            "BYTE": lambda x: str(x).encode(),
                            "DOUBLE": lambda x: float(x),
                            "FLOAT" : lambda x: float(x),
                            "DECIMAL": lambda x: Decimal(str(x)),
                            "BYTE_ARRAY": lambda x: base64.b64decode(x)}
    if isinstance(value, OrderedDict):
        return OrderedDict([(value['dqpath'].split('/')[-1], sdc_value_reader(value))
                            for key, value in value.items()])
    elif isinstance(value, dict):
        if 'type' in value and 'value' in value:
            # value['type'] in some cases could also be a dict
            if (value['value'] is None or not isinstance(value['type'], str) or
                value['type'] not in type_to_function_map):
                return value['value']
            return type_to_function_map[value['type']](value['value'])
        else:
            return {key: sdc_value_reader(value) for key, value in value.items()}
    elif isinstance(value, list):
        return [sdc_value_reader(item) for item in value]
    else:
        return value['value']


def st_value_reader(value):
    """Helper function which can parse ST Record value (Record JSON in dict format for example)
    and convert to ST implied Python collection with necessary types being converted from ST to Python.

    Args:
        value: ST Record value.

    Returns:
        The value.
    """
    # Note: check instance of OrderedDict before dict to avoid superfluous
    # check of OrderedDict getting evaluated for dict
    type_to_function_map = {"LIST_MAP": lambda x: st_value_reader(OrderedDict([(key, x[key])
                                                                               for key in range(len(x))])),
                            "LIST": lambda x: st_value_reader(x),
                            "MAP": lambda x: st_value_reader(x),
                            "SHORT": lambda x: int(x),
                            "INTEGER": lambda x: int(x),
                            "LONG": lambda x: int(x),
                            "CHAR": lambda x: x,
                            "STRING": lambda x: x,
                            "DATE": lambda x: datetime.utcfromtimestamp(x/1000),
                            "DATETIME": lambda x: datetime.utcfromtimestamp(x/1000),
                            "TIME": lambda x: datetime.utcfromtimestamp(x/1000),
                            "BOOLEAN": lambda x: x,
                            "BYTE": lambda x: str(x).encode(),
                            "DOUBLE": lambda x: float(x),
                            "FLOAT" : lambda x: float(x),
                            "DECIMAL": lambda x: Decimal(str(x)),
                            "BYTE_ARRAY": lambda x: base64.b64decode(x)}
    if isinstance(value, OrderedDict):
        return OrderedDict([(value['dqpath'].split('/')[-1], st_value_reader(value))
                            for key, value in value.items()])
    elif isinstance(value, dict):
        if 'type' in value and 'value' in value:
            # value['type'] in some cases could also be a dict
            if (value['value'] is None or not isinstance(value['type'], str) or
                value['type'] not in type_to_function_map):
                return value['value']
            return type_to_function_map[value['type']](value['value'])
        else:
            return {key: st_value_reader(value) for key, value in value.items()}
    elif isinstance(value, list):
        return [st_value_reader(item) for item in value]
    else:
        return value['value']


def pipeline_json_encoder(o):
    """Default method for JSON encoding of custom classes."""
    if hasattr(o, '_data'):
        return o._data
    raise TypeError('{} is not JSON serializable'.format(repr(o)))


def format_log(log_records):
    return '\n'.join([('{timestamp} [user:{user}] [pipeline:{entity}] '
                       '[runner:{runner}] [thread:{thread}] {severity} '
                       '{category} - {message} {exception}').format(timestamp=rec.get('timestamp'),
                                                                    user=rec.get('s-user'),
                                                                    entity=rec.get('s-entity'),
                                                                    runner=rec.get('s-runner'),
                                                                    thread=rec.get('thread'),
                                                                    severity=rec.get('severity'),
                                                                    category=rec.get('category'),
                                                                    message=rec.get('message'),
                                                                    exception=rec.get('exception'))
                      for rec in log_records])


def format_sch_log(log_records):
    return '\n'.join([('{timestamp} [requestId:{request_id}] [app:{app}] '
                        '[componentId:{component_id}] [user:{user}] [thread:{thread}] '
                        '{exception_level} {message}').format(timestamp=rec.get('timestamp'),
                                                              request_id=rec.get('request_id'),
                                                              app=rec.get('app'),
                                                              component_id=rec.get('component_id'),
                                                              user=rec.get('user'),
                                                              thread=rec.get('thread'),
                                                              exception_level=rec.get('exception_level'),
                                                              message=rec.get('message'))
                      for rec in log_records])


# The `#:` constructs at the end of assignments are part of Sphinx's autodoc functionality.
DEFAULT_TIME_BETWEEN_CHECKS = 1  #:
DEFAULT_TIMEOUT = 60  #:
def wait_for_condition(condition, condition_args=None, condition_kwargs=None,
                       time_between_checks=DEFAULT_TIME_BETWEEN_CHECKS, timeout=DEFAULT_TIMEOUT,
                       time_to_success=0, success=None, failure=None):
  """Wait until a condition is satisfied (or timeout).

  Args:
      condition: Callable to evaluate.
      condition_args (optional): A list of args to pass to the
          ``condition``. Default: ``None``
      condition_kwargs (optional): A dictionary of kwargs to pass to the
          ``condition``. Default: ``None``
      time_between_checks (:obj:`int`, optional): Seconds between condition checks.
          Default: :py:const:`DEFAULT_TIME_BETWEEN_CHECKS`
      timeout (:obj:`int`, optional): Seconds to wait before timing out.
          Default: :py:const:`DEFAULT_TIMEOUT`
      time_to_success (:obj:`int`, optional): Seconds for the condition to hold true
          before it is considered satisfied. Default: ``0``
      success (optional): Callable to invoke when ``condition`` succeeds. A ``time``
          variable will be passed as an argument, so can be used. Default: ``None``
      failure (optional): Callable to invoke when timeout occurs. ``timeout`` will
          be passed as an argument. Default: ``None``

  Raises:
      :py:obj:`TimeoutError`
  """
  start_time = time()
  stop_time = start_time + timeout

  success_start_time = None

  while time() < stop_time:
      outcome = condition(*condition_args or [], **condition_kwargs or {})
      if outcome:
          success_start_time = success_start_time or time()
          if time() >= success_start_time + time_to_success:
              if success is not None:
                  success(time='{:.3f}'.format(time() - start_time))
              return
      else:
          success_start_time = None
      sleep(time_between_checks)

  if failure is not None:
      failure(timeout=timeout)


class SeekableList(list):
    def get(self, **kwargs):
        try:
            return next(i for i in self if all(getattr(i, k) == v for k, v in kwargs.items()))
        except StopIteration:
            raise ValueError('Instance ({}) is not in list'.format(', '.join('{}={}'.format(k, v)
                                                                             for k, v in kwargs.items())))

    def get_all(self, **kwargs):
        return SeekableList(i for i in self if all(getattr(i, k) == v for k, v in kwargs.items()))


class MutableKwargs:
    """Util class with functions to update kwargs.

    Args:
        defaults (:obj:`dict`): default kwargs for the function.
        actuals (:obj:`dict`): actual kwargs passed to the function.
    """

    def __init__(self, defaults, actuals):
        self._defaults = defaults
        self._actuals = actuals

    def union(self):
        """Unions defaults with actuals.

        Returns:
            A py:obj:`dict` of unioned args.
        """
        unioned_kwargs = dict(self._defaults)
        unioned_kwargs.update(self._actuals)
        return unioned_kwargs

    def subtract(self):
        """Returns the difference between actuals and defaults based on keys.

        Returns:
            A py:obj:`dict` of subtracted kwargs.
        """
        return {key: self._actuals[key] for key in self._actuals.keys() - self._defaults.keys()}


def update_acl_permissions(api_client, resource_type, permission):
    """Util function mapping various api_client functions (update_acl_permissions) to the resource_type.

    Args:
        api_client (py:class:`streamsets.sdk.sch_api.ApiClient`): An instance of API client.
        resource_type (:obj:`str`): Type of resource eg. 'JOB', 'PIPELINE'.
        permission (:py:class:`streamsets.sdk.sch_models.Permission`): A Permission object.
    """
    function_call_mapping = {'JOB': api_client.update_job_permissions,
                             'PIPELINE': api_client.update_pipeline_permissions,
                             'SDC': api_client.update_sdc_permissions,
                             'REPORT_DEFINITION': api_client.update_report_definition_permissions,
                             'CONNECTION': api_client.update_connection_permissions,
                             'TOPOLOGY': api_client.update_topology_permissions,
                             'EVENT_SUBSCRIPTION': api_client.update_subscription_permissions,
                             'DEPLOYMENT': api_client.update_deployment_permissions,
                             'SCHEDULER_JOB': api_client.update_scheduled_task_permissions,
                             'ALERT': api_client.update_alert_permissions}
    return function_call_mapping[resource_type](permission, permission['resourceId'], permission['subjectId'])


def set_acl(api_client, resource_type, resource_id, acl_json):
    """Util function mapping various api_client functions (set_acl) to the resource_type.

    Args:
        api_client (py:class:`streamsets.sdk.sch_api.ApiClient`): An instance of API client.
        resource_type (:obj:`str`): Type of resource eg. 'JOB', 'PIPELINE'.
        resource_id (:obj:`str`): Id of the resource (pipeline, job etc.).
        acl_json (:py:class:`streamsets.sdk.sch_models.Permission`): A Permission object.
    """
    function_call_mapping = {'JOB': api_client.set_job_acl,
                             'PIPELINE': api_client.set_pipeline_acl,
                             'SDC': api_client.set_executor_acl,
                             'REPORT_DEFINITION': api_client.set_report_definition_acl,
                             'CONNECTION': api_client.update_connection_acl,
                             'TOPOLOGY': api_client.set_topology_acl,
                             'EVENT_SUBSCRIPTION': api_client.set_subscription_acl,
                             'DEPLOYMENT': api_client.set_deployment_acl,
                             'SCHEDULER_JOB': api_client.set_scheduled_task_acl,
                             'ALERT': api_client.set_alert_acl}
    return function_call_mapping[resource_type](resource_id, acl_json)


def reversed_dict(forward_dict):
    """Reverse the key: value pairs to value: key pairs.

    Args:
        forward_dict (:obj:`dict`): Original key: value dictionary.

    Returns:
        An instance of (:obj:`dict`) with value: key mapping.
    """
    values = list(forward_dict.values())
    if len(set(values)) < len(values):
        logger.warning('The dictionary provided, is not one-one mapping. This could cause some consistency problems.')
    return dict(reversed(item) for item in forward_dict.items())


def get_open_output_lanes(stages):
    """Util function to get open output lanes from a set of stages.

    Args:
        stages (:py:obj:`streamsets.sdk.utils.SeekableList`) or
               (:obj:`list`): List of :py:class:`streamsets.sdk.sdc_models.Stage` instances.

    Returns:
        A (:obj:`set`) of open output (:obj:`str`) lanes.
    """
    output_lanes = set()
    input_lanes = set()
    for stage in stages:
        output_lanes.update({output_lane for output_lane in stage.output_lanes})
        input_lanes.update({input_lane for input_lane in stage._data['inputLanes']})
    return output_lanes - input_lanes


def determine_fragment_label(stages, number_of_open_output_lanes):
    """Util function to determine Pipeline Fragment Label.

    Args:
        stages (:py:obj:`streamsets.sdk.utils.SeekableList`) or
               (:obj:`list`): List of :py:class:`streamsets.sdk.sdc_models.Stage` instances.
        number_of_open_output_lanes (:obj:`int`): Number of open output lanes.

    Returns:
        An instance of :obj:`str`.
    """
    stage_types = {stage['uiInfo']['stageType'] for stage in stages}
    # Logic taken from: https://git.io/fjlL2
    label = 'Processors'
    if 'SOURCE' in stage_types:
        label = 'Origins'
    if number_of_open_output_lanes == 0:
        label = 'Destinations'
    return label


def build_tag_from_raw_tag(raw_tag, organization):
    """Build tag json from raw tag string.

    Args:
        raw_tag (:obj:`str`): Raw tag
        organization (:obj:`str`): SCH Organization

    Returns:
        An instance of :obj:`dict`
    """
    # Logic as seen at https://git.io/JfPhk
    parent_id = ('{}:{}'.format('/'.join(raw_tag.split('/')[:-1]), organization) if
                 raw_tag.split('/')[0:-1] else None)
    return {'id': '{}:{}'.format(raw_tag, organization),
            'tag': raw_tag.split('/')[-1],
            'parentId': parent_id,
            'organization': organization}


def get_topology_nodes(jobs, pipeline, pipeline_definition, x_pos, y_pos, selected_topology_node=None,
                       postfix=None):
    """Create a topology node for the specified jobs in JSON format, and update any existing nodes as required.

    Instead of calling this method directly, all users should instead use the methods available to the
        :py:class:`streamsets.sdk.sch_models.TopologyBuilder` and :py:class:`streamsets.sdk.sch_models.Topology` classes
        respectively.

    Args:
        jobs (:obj:`list`): A list of jobs, in JSON format, to create topology nodes for.
        pipeline (:obj:`dict`): A Pipeline object, in JSON format, that the jobs are based on.
        pipeline_definition (:obj:`dict`): The definition of the pipeline, in JSON format.
        x_pos (:obj:`int`): An integer representing the position of the node on the X-axis.
        y_pos (:obj:`int`): An integer representing the position of the node on the Y-axis.:
        selected_topology_node (:py:class:`streamsets.sdk.sch_models.TopologyNode`, optional): A TopologyNode object to
            attach the node to. Default: ``None``
        postfix (:obj:`int`, optional): An integer to attach to the postfix datetime. Default: ``None``
    Returns:
        A :obj:`list` of Topology nodes in JSON format.
    """
    # Based off of https://git.io/JBFgn
    topology_node_json = {'nodeType': None, 'instanceName': None, 'library': None, 'stageName': None,
                          'stageVersion': None, 'jobId': None, 'pipelineId': None, 'pipelineCommitId': None,
                          'pipelineVersion': None, 'inputLanes': [], 'outputLanes': [], 'uiInfo': {}}
    error_discard_stage_name = 'com_streamsets_pipeline_stage_destination_devnull_ToErrorNullDTarget'
    stats_aggr_null_stage_name = 'com_streamsets_pipeline_stage_destination_devnull_StatsNullDTarget'
    stats_aggr_dpm_stage_name = 'com_streamsets_pipeline_stage_destination_devnull_StatsDpmDirectlyDTarget'
    fragment_source_stage_name = 'com_streamsets_pipeline_stage_origin_fragment_FragmentSource'
    fragment_processor_stage_name = 'com_streamsets_pipeline_stage_processor_fragment_FragmentProcessor'
    fragment_target_stage_name = 'com_streamsets_pipeline_stage_destination_fragment_FragmentTarget'
    topology_nodes = []
    source_system_nodes = []
    job_nodes = []
    stage_instances = pipeline_definition['stages']
    source_stage_instances = [source_stage for source_stage in stage_instances
                              if source_stage['uiInfo']['stageType'] == 'SOURCE']
    target_stage_instances = [target_stage for target_stage in stage_instances
                              if target_stage['uiInfo']['stageType'] == 'TARGET'
                              or target_stage['uiInfo']['stageType'] == 'EXECUTOR']
    first_job = jobs[0]
    postfix = int((datetime.utcnow().timestamp() * 1000 + postfix) if postfix else
                  datetime.utcnow().timestamp() * 1000)

    if selected_topology_node and selected_topology_node['nodeType'] == 'SYSTEM':
        source_system_nodes = [selected_topology_node]
    else:
        for count, source_stage_instance in enumerate(source_stage_instances):
            source_system_node = copy.deepcopy(topology_node_json)
            source_system_node['nodeType'] = 'SYSTEM'
            source_system_node['instanceName'] = '{}:SYSTEM:{}'.format(source_stage_instance['instanceName'],
                                                                       postfix)
            source_system_node['library'] = source_stage_instance['library']
            source_system_node['stageName'] = source_stage_instance['stageName']
            source_system_node['stageVersion'] = source_stage_instance['stageVersion']
            source_system_node['jobId'] = first_job._data['id']
            source_system_node['pipelineId'] = first_job._data['pipelineId']
            source_system_node['pipelineCommitId'] = first_job._data['pipelineCommitId']
            source_system_node['pipelineVersion'] = pipeline['version']
            source_system_node['outputLanes'] = ['{}:LANE:1{}'.format(source_system_node['instanceName'], postfix)]
            source_system_node['uiInfo']['label'] = source_stage_instance['uiInfo']['label']
            source_system_node['uiInfo']['colorIcon'] = (source_stage_instance['uiInfo']['colorIcon'] if 'colorIcon'
                                                         in source_stage_instance['uiInfo'] else '')
            source_system_node['uiInfo']['xPos'] = x_pos
            source_system_node['uiInfo']['yPos'] = y_pos + (len(jobs) * 150) / 2 + +(count * 175)
            topology_nodes.append(source_system_node)
            source_system_nodes.append(source_system_node)

    for count, job in enumerate(jobs):
        job_node = copy.deepcopy(topology_node_json)
        job_node['nodeType'] = 'JOB'
        job_node['instanceName'] = '{}:JOB:{}{}'.format(source_stage_instances[0]['instanceName'], postfix, count)
        job_node['library'] = source_stage_instances[0]['library']
        job_node['stageName'] = source_stage_instances[0]['stageName']
        job_node['stageVersion'] = source_stage_instances[0]['stageVersion']
        job_node['jobId'] = job._data['id']
        job_node['pipelineId'] = job._data['pipelineId']
        job_node['pipelineCommitId'] = job._data['pipelineCommitId']
        job_node['pipelineVersion'] = pipeline['version']
        job_node['inputLanes'] = [node['outputLanes'][0] for node in source_system_nodes]
        job_node['uiInfo']['label'] = job._data['name']
        job_node['uiInfo']['xPos'] = x_pos + 220
        job_node['uiInfo']['yPos'] = y_pos + (len(target_stage_instances) * 150) / 2 + count * 150
        job_node['uiInfo']['outputStreamLabels'] = []
        job_node['uiInfo']['outputStreamTexts'] = []
        job_node['uiInfo']['statsAggr'] = ('statsAggregatorStage' in pipeline_definition and
                                           pipeline_definition['statsAggregatorStage']['stageName'] !=
                                           stats_aggr_null_stage_name and
                                           pipeline_definition['statsAggregatorStage']['stageName'] !=
                                           stats_aggr_dpm_stage_name)
        job_node['uiInfo']['executorType'] = job._data['executorType']
        topology_nodes.append(job_node)
        job_nodes.append(job_node)

    for count, target_stage_instance in enumerate(target_stage_instances):
        target_instance_name = target_stage_instance['instanceName']
        if target_stage_instance['stageName'] in [fragment_source_stage_name,
                                                  fragment_processor_stage_name,
                                                  fragment_target_stage_name]:
            fragment_id = target_stage_instance['uiInfo']['fragmentId']
            fragment_instance_id = target_stage_instance['uiInfo']['fragmentInstanceId']
            selected_fragment = next((fragment for fragment in pipeline_definition['fragments'] if
                                     fragment['fragmentId'] == fragment_id and
                                     fragment['fragmentInstanceId'] == fragment_instance_id), None)
            if selected_fragment and 'stages' in selected_fragment and len(selected_fragment['stages']):
                target_instance_name = selected_fragment['stages'][0]['instanceName']
        new_output_lane = '{}:LANE:{}{}'.format(target_instance_name, postfix, count + 1)

        for job_node in job_nodes:
            job_node['outputLanes'].append(new_output_lane)
            job_node['uiInfo']['outputStreamLabels'].append(target_stage_instance['uiInfo']['label'])
            job_node['uiInfo']['outputStreamTexts'].append(target_stage_instance['uiInfo']['label'][0:1])
        target_system_node = copy.deepcopy(topology_node_json)
        target_system_node['nodeType'] = 'SYSTEM'
        target_system_node['instanceName'] = '{}:SYSTEM:{}'.format(target_stage_instance['instanceName'],
                                                                   postfix)
        target_system_node['library'] = target_stage_instance['library']
        target_system_node['stageName'] = target_stage_instance['stageName']
        target_system_node['stageVersion'] = target_stage_instance['stageVersion']
        target_system_node['jobId'] = first_job._data['id']
        target_system_node['pipelineId'] = first_job._data['pipelineId']
        target_system_node['pipelineCommitId'] = first_job._data['pipelineCommitId']
        target_system_node['pipelineVersion'] = pipeline['version']
        target_system_node['inputLanes'] = [new_output_lane]
        target_system_node['outputLanes'] = ['{}OutputLane1{}'.format(target_system_node['instanceName'],
                                                                      postfix)]
        target_system_node['uiInfo']['label'] = target_stage_instance['uiInfo']['label']
        target_system_node['uiInfo']['colorIcon'] = (target_stage_instance['uiInfo']['colorIcon'] if 'colorIcon'
                                                     in target_stage_instance['uiInfo'] else '')
        target_system_node['uiInfo']['xPos'] = x_pos + 500
        target_system_node['uiInfo']['yPos'] = y_pos + count * 175
        topology_nodes.append(target_system_node)

    if pipeline_definition['errorStage']:
        error_stage_instance = pipeline_definition['errorStage']
        new_output_lane = '{}:LANE:{}{}'.format(error_stage_instance['instanceName'],
                                                postfix,
                                                len(target_stage_instances) + 1)

        for job_node in job_nodes:
            job_node['outputLanes'].append(new_output_lane)
            job_node['uiInfo']['outputStreamLabels'].append(error_stage_instance['uiInfo']['label'])
            job_node['uiInfo']['outputStreamTexts'].append(error_stage_instance['uiInfo']['label'][0:1])
            job_node['uiInfo']['errorStreamIndex'] = len(target_stage_instances)
        error_system_node = copy.deepcopy(topology_node_json)
        error_system_node['nodeType'] = 'SYSTEM'
        error_system_node['instanceName'] = '{}:SYSTEM:{}'.format(error_stage_instance['instanceName'], postfix)
        error_system_node['library'] = error_stage_instance['library']
        error_system_node['stageName'] = error_stage_instance['stageName']
        error_system_node['stageVersion'] = error_stage_instance['stageVersion']
        error_system_node['jobId'] = first_job._data['id']
        error_system_node['pipelineId'] = first_job._data['pipelineId']
        error_system_node['pipelineCommitId'] = first_job._data['pipelineCommitId']
        error_system_node['pipelineVersion'] = pipeline['version']
        error_system_node['inputLanes'] = [new_output_lane]
        error_system_node['outputLanes'] = (['{}OutputLane1{}'.format(error_system_node['instanceName'], postfix)]
                                            if error_stage_instance['stageName'] != error_discard_stage_name
                                            else [])
        error_system_node['uiInfo']['label'] = error_stage_instance['uiInfo']['label']
        error_system_node['uiInfo']['xPos'] = x_pos + 500
        error_system_node['uiInfo']['yPos'] = y_pos + len(target_stage_instances) * 175
        topology_nodes.append(error_system_node)

    return topology_nodes
