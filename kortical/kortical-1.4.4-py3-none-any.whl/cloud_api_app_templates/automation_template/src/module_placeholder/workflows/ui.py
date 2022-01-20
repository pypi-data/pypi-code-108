import json
from uuid import uuid4
from kortical import api
from module_placeholder.config import read_config
from module_placeholder.workflows import predict, common


config = read_config("config.yml")
target = config['target']
not_automated_class = config['not_automated_class']
instance_name = config['instance_name']


def get_automation_accuracy():
    deployment_name = 'Production'
    instance = api.instance.Instance.create_or_select(instance_name)
    deployment = instance.get_deployment(deployment_name)
    model = deployment.get_live_model()
    if model is None:
        raise Exception(f"There is no live model for instance [{instance_name}] deployment [{deployment_name}].")
    # Get calibration data based on model id
    calibration_data = common.storage.get(common.get_calibration_data_storage_name(model.id))
    return calibration_data[target]['automation_accuracy']


def upload_file(df):
    file_id = uuid4()

    # Do predictions
    df = predict.predict(df)

    del df[target]
    df[target] = df[f"predicted_{target}"]
    del df[f"predicted_{target}"]

    # Save file
    common.storage.store(f"file_{file_id}", df)

    # Get subset of rows not automated and row indices
    df_for_review = df[df[target] == not_automated_class]
    df_for_review['row_id'] = df_for_review.index

    # Get metadata about predictions
    response = {
        'file_id': file_id,
        'total_items': len(df),
        'num_automated': len(df[df[target] != not_automated_class]),
        'num_for_review': len(df_for_review),
        'accuracy': get_automation_accuracy() * 100
    }
    response['num_automated_percentage'] = response['num_automated'] / response['total_items'] * 100
    response['num_for_review_percentage'] = response['num_for_review'] / response['total_items'] * 100
    response['items_for_review'] = json.loads(df_for_review.to_json(orient='split'))
    del response['items_for_review']['index']
    response['items_for_review']['target'] = target
    response['items_for_review']['labels'] = [x.replace("yhat_probs_", "") for x in df.columns if x.startswith("yhat_probs_")]

    # Return JSON
    return response


def update_file_prediction(file_id, row_id, answer):
    df = common.storage.get(f"file_{file_id}")

    df.loc[row_id, target] = answer

    common.storage.store(f"file_{file_id}", df, allow_overwrite=True)


def download_file(file_id):
    df = common.storage.get(f"file_{file_id}")
    return df
