import json
from Accuinsight.modeler.core.LcConst.LcConst import RUN_OBJ_JSON_PATH, RUN_BASE_PATH
from Accuinsight.modeler.core.LcConst.LcConst import ALL_MODEL_PARAMS, SELECTED_METRICS, SELECTED_PARAMS
from Accuinsight.modeler.protos.life_cycle_pb2 import LcParam, LcMetric


# load json data
def _load_current_run(run_info_json):
    data_path = run_info_json[RUN_BASE_PATH] + run_info_json[RUN_OBJ_JSON_PATH]

    with open(data_path) as json_file:
        json_data = json.load(json_file)

    return json_data


def _makeLcParam(selected_params, all_model_params):
    grpc_params = []

    for param_key in selected_params:

        param = LcParam(
            key=param_key,
            value=str(all_model_params[param_key])
        )
        grpc_params.append(param)
    return grpc_params


# parse parameters
def parse_run_parameters(json_data):
    selected_params = json_data[SELECTED_PARAMS]
    all_model_params = json_data[ALL_MODEL_PARAMS]

    grpc_params = _makeLcParam(selected_params=selected_params, all_model_params=all_model_params)
    return grpc_params


# parse metrics
def parse_run_metrics(json_data):
    grpc_metrics = []

    # selected_metrics
    selected_metrics = json_data[SELECTED_METRICS]
    metric_keys = selected_metrics.keys()

    result_dict = {'metrics': []}

    count = 0
    for key in metric_keys:
        timestamp = [str(count)]
        steps = [str(count)]
        values = [str(selected_metrics[key])]

        count += 1

        result_dict['metrics'].append({'key': key,
                                       'values': values,
                                       'timestamp': timestamp,
                                       'steps': steps})

    metrics = result_dict['metrics']

    for item in metrics:
        metric = LcMetric(
                key=item['key'],
                values=item['values'],
                timestamp=item['timestamp'],
                steps=item['steps']
            )
        grpc_metrics.append(metric)

    return grpc_metrics


def parse_run_result(run_info_json):
    result_dict = {'metrics': '', 'params': ''}
    json_data = _load_current_run(run_info_json)
    grpc_params = parse_run_parameters(json_data=json_data)
    grpc_metrics = parse_run_metrics(json_data=json_data)

    result_dict['metrics'] = grpc_metrics
    result_dict['params'] = grpc_params
    return result_dict

