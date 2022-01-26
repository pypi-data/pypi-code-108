import requests

from typing import Optional

from canvas_workflow_kit import settings

from os.path import join


def fetch_patient(patient_key: str, config_name: Optional[str] = None):
    config = settings.read_config(config_name)

    response = requests.get(join(
        config['url'], f'api/PatientProtocolInput/{patient_key}'
    ), headers={'Authorization': config['api_key']})
    response.raise_for_status()
    return response.json()
