from collections.abc import Mapping
from csv import DictReader
import json
from Accuinsight.modeler.core.LcConst.LcConst import RUN_RESULT_PATH, RUN_MODEL_VISUAL_CSV_PATH, \
    RUN_MODEL_VISUAL_JSON_PATH, RUN_MODEL_JSON_PATH, SELECTED_METRICS
from Accuinsight.modeler.protos.life_cycle_pb2 import LcMetric, LcParam
from Accuinsight.modeler.core.Run.ParseRun import Parse_Helper

# get parameter path with run type
# get metric path with run type


def load_parameter(run_meta):
    run_result_path = run_meta[RUN_RESULT_PATH]
    json_path = run_result_path[RUN_MODEL_JSON_PATH]

    with open(json_path) as json_file:
        param_json_data = json.load(json_file)

    return param_json_data


def load_visual_json(run_meta):
    run_result_path = run_meta[RUN_RESULT_PATH]
    json_path = run_result_path[RUN_MODEL_VISUAL_JSON_PATH]

    with open(json_path) as json_file:
        param_json_data = json.load(json_file)

    return param_json_data


def _read_csv_with_csv(run_meta):
    column_dict = {}

    run_result_path = run_meta[RUN_RESULT_PATH]
    csv_path = run_result_path[RUN_MODEL_VISUAL_CSV_PATH]

    with open(csv_path, 'r') as read_csv:
        csv_dict_reader = DictReader(read_csv, delimiter=';')
        column_names = csv_dict_reader.fieldnames

        for row in csv_dict_reader:
            for col_name in column_names:
                column_dict.setdefault(col_name, []).append(row[col_name])

    return column_dict


def load_metric(run_meta):
    column_dict = _read_csv_with_csv(run_meta)

    result_dict = {'metrics': []}
    for key in column_dict:
        if key != 'epoch':
            result_dict['metrics'].append({'key': key, 'values': column_dict[key], 'timestamp': column_dict['epoch'], 'steps': column_dict['epoch']})

    return result_dict


def _append_metrics(metrics, **kwargs):
    values = []
    timestamp = []
    steps = []
    count = 0
    data = kwargs['data']
    key = kwargs['key']

    for v in data:
        values.append(str(v))
        timestamp.append(str(count))
        steps.append(str(count))
        count += 1
    metrics.append({'key': key,
                    'values': values,
                    'timestamp': timestamp,
                    'steps': steps})
    return metrics


def _parse_true_predict(metrics, run_meta):
    param_data = load_visual_json(run_meta)
    true_y = []
    predicted_y = []
    true_y_values = param_data['True_y']
    predicted_y_values = param_data['Predicted_y']

    # check if nested list
    is_nested_true = any(isinstance(elem, list) for elem in true_y_values)
    is_nested_predicted = any(isinstance(elem, list) for elem in predicted_y_values)

    if is_nested_true:
        for elem in true_y_values:
            true_y.append(elem[0])
    else:
        true_y = true_y_values

    if is_nested_predicted:
        for elem in predicted_y_values:
            predicted_y.append(elem[0])
    else:
        predicted_y = predicted_y_values

    metrics = _append_metrics(metrics, data=true_y, key='true_y')
    metrics = _append_metrics(metrics, data=predicted_y, key='predicted_y')
    return metrics


# parse metrics
def _parse_selected_metrics(run_meta):
    # read ~/runs/results-XGBClassifier/model-info-json/*.json
    # get "selected_metrics" field
    # return metrics

    metric_data = load_parameter(run_meta)

    grpc_metrics = []
    if SELECTED_METRICS not in metric_data:
        return grpc_metrics

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


def parse_metric(run_meta):
    metric_data = load_metric(run_meta)
    metrics = metric_data['metrics']
    metrics = _parse_true_predict(metrics, run_meta)

    grpc_metrics = []

    for item in metrics:
        metric = LcMetric(
                key=item['key'],
                values=item['values'],
                timestamp=item['timestamp'],
                steps=item['steps']
            )
        grpc_metrics.append(metric)

    selected_metrics = _parse_selected_metrics(run_meta=run_meta)
    grpc_metrics = grpc_metrics + selected_metrics
    return grpc_metrics


def _parse_optimizer_info(param_data):
    grpc_params = []
    data_version = Parse_Helper.get_data_version(param_data)
    grpc_params.append(data_version)

    optimizer_info = param_data['optimizer_info']
    if isinstance(optimizer_info, Mapping):
        for k, v in optimizer_info.items():
            optimizer = LcParam(
                key='type_of_optimizer',
                value=str(k)
            )
            grpc_params.append(optimizer)
            if isinstance(v, Mapping):
                for k, v in v.items():
                    param = LcParam(
                        key=k,
                        value=str(v)
                    )
                    grpc_params.append(param)
    return grpc_params


def parse_parameter(run_meta):
    param_data = load_parameter(run_meta)

    dummy_data = {
        'model_description': 'keras test',
        'logging_time': '2020-05-06 10:30:50',
        'run_id': '9FCEF776-D830-4353-8961-144491DC03CC',
        'model_type': 'keras_nn',
        'optimizer_info': {
            'RMSprop': {
                'learning_rate': 9.999999747378752e-05,
                'rho': 0.8999999761581421,
                'decay': 0.0,
                'epsilon': 1e-07
            }
        },
        'time_delta': '0:00:14.912202'
    }

    return _parse_optimizer_info(param_data)


def parse_run_result(run_info_json):
    result_dict = {'metrics': None, 'params': None, 'visual': None}

    metric_data = parse_metric(run_meta=run_info_json)
    parameter_data = parse_parameter(run_meta=run_info_json)
    for i in range(len(parameter_data)):
        if parameter_data[i].key == 'data_version':
            result_dict['artifact'] = {}
            result_dict['artifact']['name'] = parameter_data[i].value
            result_dict['artifact']['version'] = ""
            del parameter_data[i]
            break

    result_dict['params'] = parameter_data
    result_dict['metrics'] = metric_data
    return result_dict

