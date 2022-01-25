import json
import logging
import os
from typing import List

import numpy as np
import pytest
from fluentcheck import Is

from ecgai_training_data_physionet import models
from ecgai_training_data_physionet.models import EcgRecord, EcgLeadRecord, DiagnosticCode


def module_logging_level():
    return logging.ERROR


def logger_name():
    models.module_name()


def setup_test_record_data():
    from definitions import ROOT_DIR
    path = os.path.join(ROOT_DIR, "tests", "test_data", "00001_hr.json")
    with open(path) as json_file:
        data = json.load(json_file)
    record = EcgRecord.from_json(data)
    assert type(record) is EcgRecord
    return record


@pytest.mark.asyncio
def test_create_data_set_record(caplog):
    # try:
    with caplog.at_level(level=module_logging_level(), logger=logger_name()):
        random_signals = np.random.random(50)
        test_signal: List[float] = random_signals.tolist()
        test_lead = EcgLeadRecord.create("II", test_signal)
        test_leads = [test_lead]
        record = EcgRecord.create(
            record_id=1,
            record_name="messageId",
            database_name="database",
            sample_rate=200,
            leads=test_leads,
        )
        assert record.sample_rate == 200
        assert type(record) is EcgRecord


@pytest.mark.asyncio
def test_read_from_json(caplog):
    with caplog.at_level(level=module_logging_level(), logger=logger_name()):
        record = setup_test_record_data()
        assert type(record) is EcgRecord


def test_create_description_code(caplog):
    with caplog.at_level(level=module_logging_level(), logger=logger_name()):
        scp_code = "DEF"
        description = "This is my class"
        sut = DiagnosticCode.create(scp_code=scp_code, description=description)
        Is(sut).of_type(DiagnosticCode)
        Is(sut.scp_code).not_empty.matches(scp_code)
        Is(sut.description).not_empty.matches(description)
