# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from dateutil import parser
from collections import OrderedDict
from azureml._cli_common.constants import TABLE_OUTPUT_TIME_FORMAT
from azureml._cli.run.run_commands import _get_minimal_run, _run_to_output_dict
from azureml._model_management._constants import AKS_ENDPOINT_TYPE


# MLC transforms
def transform_mlc_resource(result_tuple):
    result, verbose = result_tuple

    if result is None:
        return result

    if verbose:
        return result

    to_print = {
        'name': result['name'],
        'provisioningState': result['properties']['provisioningState'],
        'location': result['location'],
        'provisioningErrors': result['properties']['provisioningErrors']
    }

    return to_print


# MLC transforms
def transform_amlcompute_identity_resource(result_tuple):
    result, verbose = result_tuple

    if result is None:
        return result

    if verbose:
        return result

    to_print = {}
    if result['type'] == "SystemAssigned":
        to_print = {
            'type': result['type'],
            'principalId': result['principalId'],
            'tenantId': result['tenantId']
        }
    else:
        to_print = {
            'type': result['type'],
            'userAssignedIdentities': result['userAssignedIdentities'],
        }

    return to_print


def table_transform_mlc_resource(result):
    return OrderedDict([
        ('name', result['name']),
        ('provisioningState', result['provisioningState']),
        ('location', result['location'])
    ])


def transform_mlc_resource_list(result_tuple):
    result_list, verbose = result_tuple

    return [transform_mlc_resource((obj, verbose)) for obj in result_list]


def table_transform_mlc_resource_list(result):
    return [
        OrderedDict([
            ('name', resource['name']),
            ('provisioningState', resource['provisioningState']),
        ])
        for resource in result]


def transform_mlc_delete(result_tuple):
    result, verbose = result_tuple

    if verbose:
        return result

    return {
        'id': result['id']
    }


def table_transform_mlc_delete(result):
    return OrderedDict([
        ('id', result['id'])
    ])


def transform_mlc_get_creds(result_tuple):
    result, verbose = result_tuple

    # Not using verbose, as result is already relatively minimal json. Including for consistency and future use.
    return result


def table_transform_mlc_get_creds(result):
    # The JSON is too long to reasonably display in a table.
    raise NotImplementedError()


# Model result transforms
def transform_model_show(result_tuple):
    result, verbose = result_tuple

    if verbose:
        return result

    resource_configuration = result.get('resourceConfiguration')
    return {
        'name': result['name'],
        'id': result['id'],
        'version': result['version'],
        'framework': result['framework'],
        'frameworkVersion': result['frameworkVersion'],
        'createdTime': result['createdTime'],
        'tags': result['tags'] if result['tags'] else '',
        'properties': result['properties'] if result['properties'] else '',
        'description': result['description'] or '',
        'experimentName': result['experimentName'] or '',
        'runId': result['runId'] or '',
        'cpu': resource_configuration.get('cpu', '') if resource_configuration else '',
        'memoryInGB': resource_configuration.get('memoryInGB', '') if resource_configuration else '',
        'gpu': resource_configuration.get('gpu', '') if resource_configuration else '',
        'sampleInputDatasetId': result['sampleInputDatasetId'] or '',
        'sampleOutputDatasetId': result['sampleOutputDatasetId'] or '',
    }


def table_transform_model_show(result):
    return OrderedDict([('name', result['name']),
                        ('id', result['id']),
                        ('version', result['version']),
                        ('framework', result['framework']),
                        ('frameworkVersion', result['frameworkVersion']),
                        ('createdTime', _convert_time(result['createdTime']).strftime(TABLE_OUTPUT_TIME_FORMAT)),
                        ('tags', result['tags'] if result['tags'] else ''),
                        ('properties', result['properties'] if result['properties'] else ''),
                        ('experimentName', result['experimentName'] or ''),
                        ('runId', result['runId'] or '')])


def transform_model_list(result_tuple):
    result_list, verb = result_tuple

    if verb:
        return result_list

    return [
        {
            'name': result['name'],
            'id': result['id'],
            'version': result['version'],
            'framework': result['framework'],
            'frameworkVersion': result['frameworkVersion'],
            'createdTime': result['createdTime']
        }
        for result in result_list]


def table_transform_model_list(result_list):
    return [
        OrderedDict([('name', result['name']),
                     ('id', result['id']),
                     ('version', result['version']),
                     ('framework', result['framework']),
                     ('frameworkVersion', result['frameworkVersion']),
                     ('createdTime', _convert_time(result['createdTime']).strftime(TABLE_OUTPUT_TIME_FORMAT))])
        for result in result_list]


def transform_model_delete(result_tuple):
    result, verbose = result_tuple

    if verbose:
        return result

    return {
        'id': result['id']
    }


def table_transform_model_delete(result):
    return OrderedDict([('id', result['id'])])


# Model optimize result transforms
def transform_model_optimize(result_tuple):
    result, verbose = result_tuple

    if verbose:
        return result

    # do not return optimization_resp if no verbose specified
    if 'optimization_resp' in result.keys():
        result.pop('optimization_resp')

    return result


def table_transform_model_optimize(result):
    """
    :param result:
    :type result: dict
    :return:
    :rtype: OrderedDict
    """
    objs = []
    for k, v in result.items():
        objs.append((k, v))
    return OrderedDict(objs)


# Model package result transforms
def transform_model_package(result_tuple):
    result, verbose = result_tuple

    if verbose:
        return result

    return {
        'name': result['name'],
        'id': result['id'],
        'version': result['version'],
        'createdTime': result['createdTime'],
        'creationState': result['creationState'],
        'description': result['description'] or '',
        'modelIds': result['modelIds'],
        'tags': result['tags'] if result['tags'] else ''
    }


def table_transform_model_package(result):
    return OrderedDict([('name', result['name']),
                        ('id', result['id']),
                        ('version', result['version']),
                        ('createdTime', _convert_time(result['createdTime']).strftime(TABLE_OUTPUT_TIME_FORMAT)),
                        ('creationState', result['creationState']),
                        ('modelIds', result['modelIds']),
                        ('tags', result['tags'])])


# Model profile transforms
def transform_model_profile(result_tuple):
    result, verbose = result_tuple

    return result


def table_transform_model_profile(result):
    cli_success_keys = [
        'name',
        'state',
        'recommendedCpu',
        'recommendedMemoryInGB',
        'recommendationLatencyInMs',
        'maxUtilizedMemoryInGB',
        'maxUtilizedCpu',
        'averageLatencyInMs',
        'latencyPercentile50InMs',
        'latencyPercentile90InMs',
        'latencyPercentile95InMs',
        'latencyPercentile99InMs',
        'latencyPercentile999InMs',
        'measuredQueriesPerSecond',
        'totalQueries',
        'successQueries',
        'successRate',
        'requestedCpu',
        'requestedMemoryInGB',
        'error'
    ]
    cli_failure_keys = [
        'name',
        'state',
        'error',
        'errorLogsUri'
    ]

    if result['state'] == 'Succeeded':
        return OrderedDict([(k, result[k]) for k in cli_success_keys if result.get(k) is not None])
    return OrderedDict([(k, result[k]) for k in cli_failure_keys if result.get(k) is not None])


# Image result transforms
def transform_image_show(result_tuple):
    result, verbose = result_tuple

    if verbose:
        return result

    return {
        'name': result['name'],
        'id': result['id'],
        'version': result['version'],
        'createdTime': result['createdTime'],
        'creationState': result['creationState'],
        'description': result['description'] or '',
        'modelIds': result['modelIds'],
        'tags': result['tags'] if result['tags'] else ''
    }


def table_transform_image_show(result):
    return OrderedDict([('name', result['name']),
                        ('id', result['id']),
                        ('version', result['version']),
                        ('createdTime', _convert_time(result['createdTime']).strftime(TABLE_OUTPUT_TIME_FORMAT)),
                        ('creationState', result['creationState']),
                        ('modelIds', result['modelIds']),
                        ('tags', result['tags'])])


# Endpoint result transforms
def transform_endpoint_show(result_tuple):
    result, verbose = result_tuple

    if verbose:
        return result

    return_dict = {
        'name': result['name'],
        'updatedAt': result['updatedTime'],
        'computeType': result['computeType'],
        'scoringUri': result["scoringUri"] if 'scoringUri' in result else '',
        'state': result['state'],
        'tags': result['tags'] if result['tags'] else '',
        'properties': result['properties'] if result['properties'] else ''
    }

    if 'versions' in result:
        version_result = {}
        for version_name in result['versions'].keys():
            version_result[version_name] = transform_service_show((result['versions'][version_name], verbose))

        return_dict['versions'] = version_result
    return return_dict


def table_transform_endpoint_show(result):
    version_result = {}
    if 'versions' in result:
        for version_name in result['versions'].keys():
            version_result[version_name] = table_transform_service_show(result['versions'][version_name])

    return OrderedDict([('name', result['name']),
                        ('updatedAt', _convert_time(result['updatedAt']).strftime(TABLE_OUTPUT_TIME_FORMAT)),
                        ('state', result['state']),
                        ('computeType', result['computeType']),
                        ('scoringUri', result['scoringUri']),
                        ('tags', result['tags']),
                        ('properties', result['properties']),
                        ('versions', version_result)])


def transform_endpoint_list(result_tuple):
    result_list, verbose = result_tuple

    if verbose:
        return result_list

    return [
        transform_endpoint_show((result, verbose))
        for result in result_list]


def table_transform_endpoint_list(result_list):
    return [
        table_transform_endpoint_show(result)
        for result in result_list]


# Service result transforms
def transform_service_show(result_tuple):
    result, verbose = result_tuple

    if verbose:
        return result

    return_dict = {}
    if result['computeType'].lower() != AKS_ENDPOINT_TYPE.lower():
        return_dict = {
            'name': result['name'],
            'imageId': result['imageId'] if result['computeType'].lower() != AKS_ENDPOINT_TYPE.lower() else '',
            'updatedAt': result['updatedTime'],
            'computeType': result['computeType'],
            'scoringUri': result["scoringUri"] if 'scoringUri' in result else '',
            'state': result['state'],
            'tags': result['tags'] if result['tags'] else '',
            'properties': result['properties'] if result['properties'] else '',
            'environmentDetails': result.get('environmentDetails')
        }
    else:
        return_dict = transform_endpoint_show(result_tuple)
    return return_dict


def table_transform_service_show(result):
    return OrderedDict([('name', result['name']),
                        ('updatedAt', _convert_time(result['updatedAt']).strftime(TABLE_OUTPUT_TIME_FORMAT)),
                        ('state', result['state']),
                        ('computeType', result['computeType']),
                        ('scoringUri', result['scoringUri']),
                        ('tags', result['tags']),
                        ('properties', result['properties'])])


def transform_compute_target_show(result_tuple):
    result, verbose = result_tuple

    if verbose:
        return result

    return_dict = {
        "id": result["id"],
        "name": result["name"],
        "tags": result["tags"],
        "location": result["location"],
        "properties": result["properties"]
    }

    return return_dict


def table_transform_compute_target_show(result):
    return OrderedDict([('id', result['id']),
                        ('name', result['name']),
                        ('tags', result['tags']),
                        ('location', result['location']),
                        ('properties', result['properties'])])


def transform_run_submit_notebook(result):
    return _run_to_output_dict(result)


def table_transform_run_submit_notebook(result):
    return _get_minimal_run([result])


def transform_service_list(result_tuple):
    result_list, verbose = result_tuple

    if verbose:
        return result_list

    return [
        transform_service_show((result, verbose))
        for result in result_list]


def table_transform_service_list(result_list):
    return [
        OrderedDict([('name', result['name']),
                     ('updatedAt', _convert_time(result['updatedAt']).strftime(TABLE_OUTPUT_TIME_FORMAT)),
                     ('state', result['state']),
                     ('scoringUri', result['scoringUri'])])
        for result in result_list]


def transform_service_run(result_tuple):
    result, verbose = result_tuple

    # 1. We ignore the verbosity flag, as "service run" just has a single property right now. Keeping it here for
    #    consistency with the rest of the CLI, and in case future SDK responses have more fields
    # 2. The SDK already attempts to return a JSON object from run, so we will just pass that along
    return result


def table_transform_service_run(result):
    return OrderedDict([
        ('result', result)
    ])


def transform_service_delete(result_tuple):
    result, verbose = result_tuple

    if verbose:
        return result

    return {
        'name': result['name']
    }


def table_transform_service_delete(result):
    return OrderedDict([
        ('name', result['name'])
    ])


def transform_service_keys(result_tuple):
    # Maintaining verbosity flag for consistency with rest of CLI, and in case of future additions
    result, verbose = result_tuple

    return result


def table_transform_service_keys(result):
    return OrderedDict([
        ('primaryKey', result['primaryKey']),
        ('secondaryKey', result['secondaryKey'])
    ])


def transform_access_tokens(result_tuple):
    # Maintaining verbosity flag for consistency with rest of CLI, and in case of future additions
    result, verbose = result_tuple

    return result


def table_transform_access_tokens(result):
    return OrderedDict([
        ('accessToken', result['accessToken']),
        ('tokenType', result['tokenType']),
        ('refreshAfter', result['refreshAfter']),
        ('expiryOn', result['expiryOn'])
    ])


def _convert_time(time_str):
    time_obj = parser.parse(time_str)
    time_obj = time_obj.replace(microsecond=0, tzinfo=None)
    return time_obj


def transform_package(result_tuple):
    # Maintaining verbosity flag for consistency with rest of CLI, and in case of future additions
    result, verbose = result_tuple

    return result


def table_transform_package(result):
    return OrderedDict([
        ('generateDockerfile', result['generateDockerfile']),
        ('state', result['state']),
        ('location', result['location'])
    ])


def transform_submit_rl(result_tuple):
    # Maintaining verbosity flag for consistency with rest of CLI, and in case of future additions
    result, verbose = result_tuple

    return result


def transform_computeinstance_resource(result_tuple):
    result, verbose = result_tuple

    if result is None:
        return result

    if verbose:
        return result

    to_print = {
        "id": result["id"],
        "name": result["name"],
        "tags": result["tags"],
        "location": result["location"],
        "state": result["properties"]["status"]["state"],
        "errors": result["properties"]["status"]["errors"]
    }

    return to_print


def table_transform_computeinstance_resource(result):
    return OrderedDict([
        ('id', result['id']),
        ('name', result['name']),
        ('tags', result['tags']),
        ('location', result['location']),
        ('state', result['properties']['status']['state']),
        ('errors', result['properties']['status']['errors'])
    ])
