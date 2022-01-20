import os
from io import BytesIO
import pandas as pd
import pytest
import requests
import tempfile
from kortical import api
from module_placeholder.config import read_config
from module_placeholder.workflows import common, business_case
from module_placeholder.api.http_status_codes import HTTP_OKAY
from tests.helpers import root_dir

config = read_config("config.yml")
api_key = config['api_key']
system_url = config['system_url']
target = config['target']
app_url = f"{system_url}/app/automation-template"
instance_name = config['instance_name']
data_file_name = config['data_file_name']


@pytest.mark.skip
@pytest.mark.unit
def test_business_case_local(client):
    df = pd.read_csv(root_dir.from_root_dir(os.path.join("data", data_file_name)))
    _, _, df_test = common.create_train_calibrate_and_test_datasets(df)
    with tempfile.NamedTemporaryFile('w+') as tmp:
        df_test.to_csv(tmp, index=False)
        tmp.flush()
        tmp.seek(0)
        response = client.post(
            f'/predict.csv?api_key={api_key}', data={'file': (BytesIO(tmp.read().encode('utf-8')), 'input.csv')},
            content_type='multipart/form-data')
    assert response.status_code == HTTP_OKAY, response.content
    df = pd.read_csv(BytesIO(response.data))


@pytest.mark.integration
@pytest.mark.smoke
def test_business_case():
    df = pd.read_csv(root_dir.from_root_dir(os.path.join("data", data_file_name)))
    _, _, df_test = common.create_train_calibrate_and_test_datasets(df)
    with tempfile.NamedTemporaryFile('w+') as tmp:
        df_test.to_csv(tmp, index=False)
        tmp.flush()
        tmp.seek(0)
        response = requests.post(f'{app_url}/predict.csv?api_key={api_key}', files={'file': tmp})
    assert response.status_code == HTTP_OKAY, response.text

    # Test results
    df_out = pd.read_csv(BytesIO(response.content))
    api.init(system_url)
    instance = api.instance.Instance.create_or_select(instance_name)
    uat_deployment = instance.get_deployment('UAT')
    model = uat_deployment.get_live_model()
    calibration_data = common.storage.get(common.get_calibration_data_storage_name(model.id))
    df_test = df_test.reset_index()
    df_test[f'predicted_{target}'] = df_out[f'predicted_{target}']
    calibration_results = api.superhuman_calibration.score(df_test, calibration_data)

    # Calculate business case
    savings = business_case.calculate(calibration_results, print_results=True)
    assert savings > 3_000_000

