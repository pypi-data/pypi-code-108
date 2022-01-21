import importlib
import inspect
import requests
import json

from typing import Optional, Union

from pathlib import Path

from canvas_workflow_kit.patient import Patient
from canvas_workflow_kit.protocol import ClinicalQualityMeasure
from canvas_workflow_kit.api import fetch_patient
from canvas_workflow_kit.internal.string import camelcase


def parse_class_from_python_source(source):
    """
    Parse the python file. Return a ClinicalQualityMeasure class if only one is
    found in the file.
    """

    spec = importlib.util.spec_from_loader('helper', loader=None)
    helper = importlib.util.module_from_spec(spec)

    exec(source, helper.__dict__)

    clinical_quality_measures = []

    for cls_name, cls in inspect.getmembers(helper, inspect.isclass):
        if cls.__module__ != 'helper':
            continue
        if issubclass(cls, ClinicalQualityMeasure):
            clinical_quality_measures.append(cls)

    if len(clinical_quality_measures) == 0:
        raise SyntaxError("No clinical quality measures found.")
    elif len(clinical_quality_measures) > 1:
        raise SyntaxError("More than one clinical quality measures found.")

    return clinical_quality_measures[0]


def send_notification(url, payload={}, headers={}):
    return requests.post(url, data=payload, headers=headers)


def load_patient(patient_key: str, config_name: Optional[str] = None):
    """
    Load a patient's data off a server to test.
    """
    response_json = fetch_patient(patient_key=patient_key, config_name=config_name)
    return Patient(response_json)


def load_local_patient(patient_path: Union[str, Path]) -> Patient:
    """
    Load a patient's data from a local downloaded directory.
    """
    # cast to Path
    if type(patient_path) is str:
        patient_path = Path(patient_path)

    combined_json = {}
    for filepath in patient_path.glob('*.json'):
        with filepath.open('r') as file:
            combined_json[camelcase(filepath.stem)] = json.load(file)  # type: ignore

    if not combined_json:
        raise FileNotFoundError(f'No JSON files were found in "{patient_path}"')

    return Patient(combined_json)
