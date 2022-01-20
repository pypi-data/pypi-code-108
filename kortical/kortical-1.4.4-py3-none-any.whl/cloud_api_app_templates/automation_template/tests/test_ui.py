import os
from io import BytesIO
import pandas as pd
import pytest
import requests
import tempfile
from module_placeholder.config import read_config
from module_placeholder.workflows import common
from module_placeholder.api.http_status_codes import HTTP_OKAY
from tests.helpers import root_dir

config = read_config("config.yml")
api_key = config['api_key']
target = config['target']
data_file_name = config['data_file_name']
not_automated_class = config['not_automated_class']
app_url = f"{config['system_url']}/app/module_placeholder"


@pytest.mark.integration
def test_ui_flow():
    df = pd.read_csv(root_dir.from_root_dir(os.path.join("data", data_file_name)))
    _, _, df_test = common.create_train_calibrate_and_test_datasets(df)
    with tempfile.NamedTemporaryFile('w+') as tmp:
        df_test.to_csv(tmp, index=False)
        tmp.flush()
        tmp.seek(0)
        response = requests.post(f'{app_url}/upload_file?api_key={api_key}', files={'file': tmp})
    assert response.status_code == HTTP_OKAY

    file_id = response.json()['file_id']
    row_id = 0
    response = requests.post(f'{app_url}/update_file_prediction?api_key={api_key}', json={
        'file_id': file_id,
        'row_id': row_id,
        'answer': not_automated_class
    })
    assert response.status_code == HTTP_OKAY

    response = requests.get(f'{app_url}/download_file.csv?api_key={api_key}&file_id={file_id}')
    assert response.status_code == HTTP_OKAY

    df = pd.read_csv(BytesIO(response.content))
    assert df.loc[row_id, target] == not_automated_class

