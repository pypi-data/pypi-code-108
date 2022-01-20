from kortical import api
from module_placeholder.config import read_config
from module_placeholder.workflows import common

config = read_config("config.yml")
target = config['target']
instance_name = config['instance_name']


def predict(df, deployment_name="Production"):
    api.init(config['system_url'])

    # Do custom processing
    common.preprocessing(df)

    instance = api.instance.Instance.create_or_select(instance_name)
    deployment = instance.get_deployment(deployment_name)
    model = deployment.get_live_model()
    if model is None:
        raise Exception(f"There is no live model for instance [{instance_name}] deployment [{deployment_name}].")

    df = deployment.predict(df)

    # Get calibration data based on model id
    calibration_data = common.storage.get(common.get_calibration_data_storage_name(model.id))
    if calibration_data is None:
        raise Exception("No matching calibration data for UAT model.")

    # do Superhuman Calibration
    api.superhuman_calibration.apply(
        df,
        calibration_data,
        in_place=True
    )

    df = common.postprocessing(df)

    return df