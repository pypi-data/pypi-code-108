import json
from Accuinsight.modeler.core.LcConst.LcConst import RUN_RESULT_PATH, RUN_MODEL_JSON_PATH
from Accuinsight.modeler.core.LcConst.LcConst import ALL_MODEL_PARAMS, SELECTED_METRICS, SELECTED_PARAMS
from Accuinsight.modeler.protos.life_cycle_pb2 import LcParam, LcMetric
from Accuinsight.modeler.core.Run.ParseRun import ParserVisualJaon, Parse_Helper


# load json data
def _load_current_run(run_info_json):
    run_results = {'json':'', 'visual':'', 'run_mata': ''}

    run_result_path = run_info_json[RUN_RESULT_PATH]
    data_path = run_result_path[RUN_MODEL_JSON_PATH]

    with open(data_path) as json_file:
        json_data = json.load(json_file)

    run_results['json'] = json_data
    run_results['run_mata'] = run_info_json

    return run_results


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
    # read ~/runs/results-XGBClassifier/model-info-json/*.json
    # return parameters

    param_data = json_data['json']
    selected_params = param_data[SELECTED_PARAMS]
    all_model_params = param_data[ALL_MODEL_PARAMS]

    grpc_params = _makeLcParam(selected_params=selected_params, all_model_params=all_model_params)

    data_version = Parse_Helper.get_data_version(param_data)
    grpc_params.append(data_version)

    return grpc_params


# parse metrics
def parse_run_metrics(json_data):
    # read ~/runs/results-XGBClassifier/model-info-json/*.json
    # get "selected_metrics" field
    # return metrics

    metric_data = json_data['json']
    grpc_metrics = []

    # selected_metrics
    selected_metrics = metric_data[SELECTED_METRICS]
    metric_keys = selected_metrics.keys()

    result_dict = {'metrics': []}

    count = 0
    timestamp = []
    steps = []
    values = []
    for key in metric_keys:
        values.append(str(selected_metrics[key]))
        timestamp.append(str(count))
        steps.append(key)
        count += 1

    result_dict['metrics'].append({
        'values': values,
        'timestamp': timestamp,
        'steps': steps})

    metrics = result_dict['metrics']

    for item in metrics:
        metric = LcMetric(
            key=SELECTED_METRICS,
            values=item['values'],
            timestamp=item['timestamp'],
            steps=item['steps']
        )
        grpc_metrics.append(metric)

    return grpc_metrics


# parse metrics
def _append_visual_data(visual_data, key):
    result_dict = {'metrics': []}

    count = 0
    timestamp = []
    steps = []
    values = []

    for k, v in visual_data.items():
        timestamp.append(str(count))
        count += 1

        steps.append(k)

        values.append(v)

    result_dict['metrics'].append({'key': key,
                                   'values': values,
                                   'timestamp': timestamp,
                                   'steps': steps})
    return result_dict


def _make_steps(steps_value):
    steps_list = []
    for value in steps_value:
        steps_list.append(str(value))
    return steps_list


def parse_run_result(run_info_json):
    result_dict = {'metrics': '', 'params': ''}
    result_data = _load_current_run(run_info_json)

    grpc_params = parse_run_parameters(json_data=result_data)
    grpc_metrics = parse_run_metrics(json_data=result_data)

    grpc_visuals = ParserVisualJaon.parse_run_visual(run_mata=result_data['run_mata'])

    result_dict['params'] = grpc_params
    result_dict['metrics'] = grpc_metrics
    result_dict['visual'] = grpc_visuals

    for i in range(len(grpc_params)):
        if grpc_params[i].key == 'data_version':
            result_dict['artifact'] = {}
            result_dict['artifact']['name'] = grpc_params[i].value
            result_dict['artifact']['version'] = ""
            del grpc_params[i]
            break

    return result_dict

