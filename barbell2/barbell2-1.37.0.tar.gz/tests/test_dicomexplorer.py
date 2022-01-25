import os
import pytest

from barbell2.dicomexplorer.dicomexplorer import DicomExplorer


COHORT_DIR = '/Volumes/USB_SECURE1/data/radiomics/projects/deepseg/data/mega/processed/NEWEPOC'
COHORT_DCM_FILE = '/Volumes/USB_SECURE1/data/radiomics/projects/deepseg/data/mega/processed/NEWEPOC/003001_pre_PV_L3.dcm'
COHORT_TAG_FILE = '/Volumes/USB_SECURE1/data/radiomics/projects/deepseg/data/mega/processed/NEWEPOC/003001_pre_PV_L3.tag'
COHORT_DCM_HEADER_NR_ENTRIES = 86
COHORT_NR_FILES = 156
DICOM_DICT_NR_ENTRIES = 4253
PATIENT_ID_NR_ENTRIES = 6


@pytest.fixture
def explorer():
    return DicomExplorer()


def test_load_dir(explorer):
    explorer.load_dir(COHORT_DIR, verbose=False)
    assert len(explorer.files) == COHORT_NR_FILES


def test_load_dicom_file(explorer):
    explorer.load_file(COHORT_DCM_FILE, verbose=False)
    assert len(explorer.files) == 1


def test_load_non_dicom_file(explorer):
    explorer.load_file(COHORT_TAG_FILE, verbose=False)
    assert len(explorer.files) == 0


def test_get_all_tags(explorer):
    outputs = explorer.get_tags(verbose=False)
    assert len(outputs) == DICOM_DICT_NR_ENTRIES


def test_get_patient_id_tag(explorer):
    outputs = explorer.get_tags(key_word='PatientID', verbose=False)
    assert len(outputs) == PATIENT_ID_NR_ENTRIES


def test_get_header(explorer):
    d = explorer.get_header(COHORT_DCM_FILE, verbose=False)
    assert len(list(d.elements())) == COHORT_DCM_HEADER_NR_ENTRIES


def test_get_pixels(explorer):
    p = explorer.get_pixel_data(COHORT_DCM_FILE)
    assert p.shape == (512, 512)
