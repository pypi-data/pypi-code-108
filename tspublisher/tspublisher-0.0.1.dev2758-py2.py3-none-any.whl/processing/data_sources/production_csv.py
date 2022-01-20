from __future__ import absolute_import, division, print_function, unicode_literals

import os

import publisher.settings as settings
from publisher.processing.data_sources.utils import read_csv_file


def get_procedure_details(procedure_code, production_data):

    procedure_row = next((r for r in production_data if is_procedure_row(procedure_code, r)), None)
    if not procedure_row:
        raise EOFError("Could not find Procedure: %s in production csv." % procedure_code)
    procedure_name = procedure_row["Procedure Name"] or "%s - UNKNOWN" % procedure_code
    specialty_names = procedure_row["Speciality"].split("~") if procedure_row["Speciality"] else []
    specialties = [specialty_code_from_name(specialty) for specialty in specialty_names]
    channel = procedure_row["Channel"]
    vbs = procedure_row["VBS"]

    return procedure_name, specialties, channel, vbs


def get_procedure_phase_list(procedure_code, production_data):
    return [get_phase_details(r) for r in production_data if is_procedure_row(procedure_code, r)]


def get_phase_data(phase_code, production_data):
    return [get_phase_details(r) for r in production_data if is_phase_row(phase_code, r)]


def get_phase_details(r):
    return {"phase_code": r["Name"], 'phase_name': r['Module Name'], 'procedure_code': r["Procedure Code"],
            'order': r["Module Order"]}


def is_procedure_row(procedure_code, r):
    code = r.get("Procedure Code")
    return code == procedure_code


def is_phase_row(phase_code, r):
    code = r.get("Name")
    return code == phase_code


def get_production_csv_data(type="module"):
    csv_file = "{}.csv".format(type)
    if os.path.isdir(settings.BASE_DATA_DIR):
        module_csv = os.path.join(settings.PRODUCTION_INFO_DIR, csv_file)
    else:
        module_csv = os.path.join(settings.PRODUCTION_INFO_BACKUP_DIR, csv_file)

    headers, rows = read_csv_file(module_csv)
    return rows


def specialty_code_from_name(specialty):
    mappings = {
        "Anaesthetics": 'anaesthetics',
        "Cardiology": 'cardiology',
        "Cardiothoracic": 'cardiothoracic',
        "Dentistry": 'general_dentistry',
        "Ear, Nose & Throat": 'otorhinolaryngology',
        "Emergency Medicine": 'emergency_medicine',
        "General": 'general',
        "Neurosurgery": 'neurosurgery',
        "Obstetrics & Gynaecology": 'obstetrics_gynaecology',
        "Ophthalmic": 'ophthalmology',
        "Oral & Maxillofacial": 'oromaxillofacial',
        "Orthopaedics": 'orthopaedics_and_trauma',
        "Plastic & Reconstructive": 'plastic_reconstructive_aesthetic',
        "Urology": 'urology',
        "Vascular": 'vascular',
    }
    if specialty in mappings:
        return mappings[specialty]
    return specialty
