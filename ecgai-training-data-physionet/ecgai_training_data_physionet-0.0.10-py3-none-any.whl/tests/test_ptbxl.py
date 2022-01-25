import asyncio
import configparser
import json
import logging
import os

import pytest
from fluentcheck import Is

from ecgai_training_data_physionet import physionet
from ecgai_training_data_physionet.models import EcgRecord, DiagnosticCode
from ecgai_training_data_physionet.physionet import InValidRecordException
from ecgai_training_data_physionet.ptbxl import PtbXl, MetaDataRow

invalid_sample_rate = {0, -1, 55, 3256}
valid_sample_rate = {100, 500}


def module_logging_level():
    return logging.CRITICAL


def logger_name():
    physionet.module_name()


# @pytest.mark.parametrize("a", [r"qwe/\abc"])
def test_fixture(tmp_path):
    assert tmp_path.is_dir()
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("sample_rate", invalid_sample_rate)
@pytest.mark.asyncio
async def test_get_records_list_invalid_sample_rate_raise_exception(
    sample_rate: int, caplog
):
    with caplog.at_level(level=module_logging_level(), logger=logger_name()):
        sut = PtbXl()
        with pytest.raises(ValueError):
            await sut.get_record(record_id=1, sample_rate=sample_rate)


# @pytest.mark.parametrize("sample_rate", valid_sample_rate)
# @pytest.mark.asyncio
# async def test_get_records_list_valid_sample_rate(sample_rate, caplog):
#     with caplog.at_level(level=module_logging_level(), logger=logger_name()):
#         sut = PtbXl()
#         task = asyncio.create_task(sut.get_records_list())
#
#         records_list = await task
#
#         Is(records_list).of_type(list)
#         record_count = len(records_list)
#         expected_record_count = 21836
#         Is(record_count).at_least(expected_record_count).at_most(expected_record_count)


def test_get_database_metadata_row(caplog):
    with caplog.at_level(level=module_logging_level(), logger=logger_name()):
        sut = PtbXl()
        # task = asyncio.create_task(sut.get_database_metadata(2))
        #
        # data_row = await task
        data_row = sut.get_database_metadata_row(2)
        assert data_row is not None


valid_record_path_name = {
    "records500/00000/00001_hr",
    "records500/00000/00002_hr",
    "records500/21000/21837_hr",
    "records100/00000/00001_lr",
    "records100/00000/00002_lr",
    "records100/21000/21837_lr",
}

valid_record_id = {1, 2, 6, 45, 100, 343, 1029, 7678, 21345, 8765, 4567, 9876}


@pytest.fixture(scope="session")
def data_directory(tmpdir_factory):
    return tmpdir_factory.mktemp("data")


# @pytest.mark.asyncio
# async def test_get_record(caplog):
#     with caplog.at_level(level=module_logging_level(), logger=logger_name()):
#         # Arrange
#         print(data_directory)
#         sut = PtbXl()
#         # Act
#         record_task = asyncio.create_task(sut.get_record(record_id=9876, sample_rate=100))
#         result = await record_task
#         Is(result).of_type(EcgRecord)


@pytest.mark.parametrize("record_id", valid_record_id)
@pytest.mark.asyncio
async def test_get_record_with_valid_record_id_and_valid_100_sample_rate(
    record_id, caplog, data_directory
):
    with caplog.at_level(level=module_logging_level(), logger=logger_name()):
        # Arrange
        print(data_directory)
        sut = PtbXl(data_location=data_directory)
        # Act
        record_task = asyncio.create_task(
            sut.get_record(record_id=record_id, sample_rate=100)
        )
        result = await record_task
        # Assert
        Is(result).of_type(EcgRecord)
        # name = os.path.basename(record_name)
        assert result.record_id == record_id
        assert result.sample_rate == 100

        assert result.age is not None
        assert result.sex is not None
        assert len(result.diagnostic_codes) > 0


@pytest.mark.parametrize("record_id", valid_record_id)
@pytest.mark.asyncio
async def test_get_record_with_valid_record_id_and_valid_500_sample_rate(
    record_id, caplog, data_directory
):
    with caplog.at_level(level=module_logging_level(), logger=logger_name()):
        # Arrange
        print(data_directory)
        sut = PtbXl(data_location=data_directory)
        # Act
        record_task = asyncio.create_task(sut.get_record(record_id=record_id))
        result = await record_task
        # Assert
        Is(result).of_type(EcgRecord)
        # name = os.path.basename(record_name)
        assert result.record_id == record_id
        assert result.sample_rate == 500
        assert result.age is not None
        assert result.sex is not None
        assert len(result.diagnostic_codes) > 0


valid_record_path_name_to_json = {
    "records500/00000/00001_hr",
    "records500/00000/00002_hr",
    "records500/00000/00003_hr",
    "records500/00000/00004_hr",
    "records500/00000/00005_hr",
    "records500/00000/00006_hr",
    "records500/00000/00007_hr",
    "records500/00000/00008_hr",
    "records500/00000/00009_hr",
    "records500/00000/00010_hr",
}


@pytest.mark.parametrize("record_id", valid_record_id)
@pytest.mark.asyncio
async def test_get_record_with_valid_path_write_to_json(
    record_id, caplog, data_directory
):
    with caplog.at_level(level=module_logging_level(), logger=logger_name()):
        sut = PtbXl(data_location=data_directory)
        # record_task = asyncio.create_task(sut.get_record(record_path_name=record_path_name))
        record_task = asyncio.create_task(sut.get_record(record_id=record_id))
        result = await record_task
        assert type(result) is EcgRecord
        # print(result)
        json_value = result.json(by_alias=True)
        file_name = result.record_name + ".json"
        file_path = os.path.join(data_directory, file_name)
        # cleanup_test_json_data(file_name=file_name)
        with open(file_path, "w") as outfile:
            json.dump(json_value, outfile)
        assert os.path.isfile(file_path) is True

        # check is valid json EcgRecord
        with open(file_path) as json_file:
            data = json.load(json_file)
        record = EcgRecord.from_json(data)
        assert type(record) is EcgRecord
        # cleanup_test_json_data(file_name=file_name)


def test_read_ini(tmpdir, caplog):
    with caplog.at_level(level=module_logging_level(), logger=logger_name()):
        print(
            tmpdir
        )  # /private/var/folders/ry/z60xxmw0000gn/T/pytest-of-gabor/pytest-14/test_read0
        d = tmpdir.mkdir("subdir")
        fh = d.join("config.ini")
        fh.write(
            """
            [application]
            user  =  foo
            password = secret  
            """
        )

        print(fh.basename)  # data.txt
        print(
            fh.dirname
        )  # /private/var/folders/ry/z60xxmw0000gn/T/pytest-of-gabor/pytest-14/test_read0/subdir
        filename = os.path.join(fh.dirname, fh.basename)

        config = configparser.ConfigParser()
        config.read(filename)

        assert config.sections() == ["application"]
        assert config["application"], {"user": "foo", "password": "secret"}


invalid_record_path_name = {
    "records500/00000/000401_hr",
    "records500/003000/00002_hr",
    "records4500/21000/21837_hr",
    "records100/000500/002001_lr",
    "records100/000400/00002_lr",
    "records100/21000/218327_lr",
}

invalid_record_id = {23423423, 35634534, 234234, 123123, 3643634}


@pytest.mark.parametrize("record_id", invalid_record_id)
@pytest.mark.asyncio
async def test_get_record_with_invalid_path_raise_exception(record_id, caplog):
    with caplog.at_level(level=module_logging_level(), logger=logger_name()):
        sut = PtbXl()
        with pytest.raises(InValidRecordException):
            await sut.get_record(record_id=record_id)


# def test_get_scp_codes(caplog):
#     with caplog.at_level(level=module_logging_level(), logger=logger_name()):
#         sut = PtbXl()
#         codes = sut.get_scp_codes()
#         assert len(codes) == 71


def test_get_database_metadata(caplog):
    with caplog.at_level(level=module_logging_level(), logger=logger_name()):
        sut = PtbXl()
        codes = sut.get_database_metadata(100)
        Is(codes).of_type(MetaDataRow)
        assert codes.ecg_id == 100


def test_get_scp_code(caplog):
    with caplog.at_level(level=module_logging_level(), logger=logger_name()):
        sut = PtbXl()
        codes = sut.get_scp_code_description("NDT")
        Is(codes).of_type(DiagnosticCode)
        assert codes.description == "non-diagnostic T abnormalities"


def test_metadata_is_loaded_true(caplog, data_directory):
    with caplog.at_level(level=module_logging_level(), logger=logger_name()):
        sut = PtbXl(data_location=data_directory)
        assert sut.is_loaded() is True
