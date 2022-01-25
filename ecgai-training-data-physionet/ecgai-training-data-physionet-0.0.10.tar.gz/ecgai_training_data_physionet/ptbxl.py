import asyncio
import functools
import os
import re
from io import StringIO

import pandas as pd
import requests
import wfdb
from ecgai_logging.log_decorator import log
from wfdb import Record

from ecgai_training_data_physionet.models import EcgRecord, DiagnosticCode
from ecgai_training_data_physionet.physionet import PhysioNetDataSet, InValidRecordException, FileNotDownloadedException


class MetaDataRow:
    def __init__(self, ecg_id, patient_id, age, sex, report, scp_codes):
        self.ecg_id = ecg_id
        self.patient_id: int = patient_id
        self.age: int = age
        define_sex = ("male", "female")
        self.sex: str = define_sex[sex]
        self.report = report
        codes_list = scp_codes.split(",")
        codes = []
        for code_item in codes_list:
            c = code_item.split(":")
            code = re.sub(r"[^a-zA-Z0-9_/]", "", c[0])
            meta_data_code = MetaDataCode(code=code, confidence=c[1])
            codes.append(meta_data_code)

        self.scp_codes = codes


class MetaDataCode:
    def __init__(self, code, confidence):
        self.code = code
        self.confidence = confidence


class PtbXl(PhysioNetDataSet):
    # DATA_LOCATION = "./data"
    # DATABASE_METADATA_FILE_NAME = "ptbxl_database.csv"
    # DIAGNOSTIC_CODE_FILE_NAME = "scp_statements.csv"

    @staticmethod
    @log
    def is_valid_sample_rate(sample_rate: int) -> bool:
        return sample_rate in {100, 500}

    @staticmethod
    @log
    def is_valid_record_id(record_id: int) -> bool:
        return record_id >= 1 or record_id <= 21837

    @log
    def load(self):
        if not os.path.isfile(self.get_database_metadata_file_path()):
            self.download_database_metadata()
        if not os.path.isfile(self.get_scp_codes_file_path()):
            self.download_scp_codes()

    @log
    def is_loaded(self) -> bool:
        return bool(
            os.path.isfile(self.get_database_metadata_file_path())
            & os.path.isfile(self.get_scp_codes_file_path())
        )

    @log
    def __init__(
            self,
            data_location: str = "./data",
            database_metadata_filename: str = "ptbxl_database.csv",
            scp_code_filename: str = "scp_statements.csv",
    ):
        self.data_location = data_location
        self.database_metadata_filename = database_metadata_filename
        self.scp_code_filename = scp_code_filename
        super(PtbXl, self).__init__("ptb-xl")

    # @log
    # async def get_records_list(self, sample_rate: int = 500) -> list[str]:
    #     """
    #     Returns all records from PtbXl database on physionet Due to a parsing error with the wfdb software 2 records
    #     are missing from the returned list records100/21000/21837_lr and records500/00000/00001_hr Both records can
    #     still be accessed via record call I may do a work around at some stage if requested
    #
    #     Args: sample_rate (int) :
    #     sample rate of records. Only 100 and 500 are valid sample rates. Any other value returns an ValueError
    #
    #     Returns:
    #         list[str]:
    #
    #     """
    #     # TODO  fix parsing error from the wfdb software
    #
    #     if not self.is_valid_sample_rate(sample_rate):
    #         raise ValueError()
    #
    #     loop = asyncio.get_event_loop()
    #     record_list_task = loop.run_in_executor(
    #         None, wfdb.get_record_list, self.data_set_name
    #     )
    #
    #     if sample_rate == 500:
    #         sub = "records100"
    #     else:
    #         sub = "records500"
    #     wfdb_record_list = await record_list_task
    #
    #     # not in wfdb_record_list is due to the parsing error returning list from wfdb.get_record_list
    #     record_list = [record for record in wfdb_record_list if sub not in record]
    #     return record_list

    @log
    async def get_record(self, record_id: int, sample_rate: int = 500) -> EcgRecord:
        """

        Parameters
        ----------
        record_id
        sample_rate

        Returns
        -------

        """
        # record_name = os.path.basename(record_name)
        # # combine dataset name with record location to create Physionet database internet_directory name
        # internet_directory = self.data_set_name + "/" + os.path.dirname(record_name) + "/"
        record_name, internet_directory = await self.get_record_path(
            record_id=record_id, sample_rate=sample_rate
        )

        try:
            loop = asyncio.get_event_loop()
            record_task = loop.run_in_executor(
                None,
                functools.partial(
                    wfdb.rdrecord, record_name=record_name, pn_dir=internet_directory
                ),
            )

            wfdb_record = await record_task
            if type(wfdb_record) is not Record:
                # Should never be called
                raise InValidRecordException(record_id=record_id, data_base_name=self.data_set_name)
            record = await self.create_ecg_record(record_id=record_id, wfdb_record=wfdb_record)
            # record = EcgRecord.create_from_record(record=wfdb_record)
            return record
        except Exception as e:
            print("Unexpected error:", e.args)
            raise e

    async def get_record_path(self, record_id, sample_rate: int = 500):
        if not self.is_valid_sample_rate(sample_rate):
            raise ValueError()
        if not self.is_valid_record_id(record_id):
            raise InValidRecordException(record_id=record_id)

        try:
            data_row = self.get_database_metadata_row(record_id=record_id)
        except KeyError as e:
            raise InValidRecordException(record_id=record_id)
        path: str
        if sample_rate == 500:
            path = data_row["filename_hr"]
        else:
            path = data_row["filename_lr"]
        record_name = os.path.basename(path)
        # combine dataset name with record location to create Physionet database internet_directory name
        internet_directory = self.data_set_name + "/" + os.path.dirname(path) + "/"
        return record_name, internet_directory

    @log
    async def create_ecg_record(self, record_id: int, wfdb_record: Record) -> EcgRecord:
        signal_array = self.create_signal_array(wfdb_record)
        # record_id = int("".join(ch for ch in wfdb_record.record_name if ch.isdigit()))
        meta_data = self.get_database_metadata(record_id)
        diagnostic_codes = await self.load_diagnostic_codes(meta_data.scp_codes)
        return EcgRecord.create(
            record_id=record_id,
            record_name=wfdb_record.record_name,
            database_name=self.data_set_name,
            sample_rate=wfdb_record.fs,
            leads=signal_array,
            age=meta_data.age,
            sex=meta_data.sex,
            report=meta_data.report,
            diagnostic_codes=diagnostic_codes,
        )

    async def load_diagnostic_codes(self, codes):
        diagnostic_codes: list[DiagnosticCode] = []
        for item in codes:
            scp_code = self.get_scp_code_description(item.code)
            diagnostic_code = DiagnosticCode.create(
                scp_code=scp_code.scp_code,
                description=scp_code.description,
                confidence=item.confidence,
            )
            diagnostic_codes.append(diagnostic_code)
        return diagnostic_codes

    def get_database_metadata_file_path(self):
        return os.path.abspath(
            os.path.join(self.data_location, self.database_metadata_filename)
        )

    def get_scp_codes_file_path(self):
        return os.path.abspath(os.path.join(self.data_location, self.scp_code_filename))

    def get_database_metadata(self, record_id: int) -> MetaDataRow:
        data_row = self.get_database_metadata_row(record_id)
        return MetaDataRow(
            ecg_id=record_id,
            patient_id=data_row["patient_id"],
            age=data_row["age"],
            sex=data_row["sex"],
            report=data_row["report"],
            scp_codes=data_row["scp_codes"],
        )

    def get_database_metadata_row(self, record_id: int):
        if not os.path.isfile(self.get_database_metadata_file_path()):
            raise FileNotDownloadedException(filename='ptbxl_database.csv')
        data_frame = pd.read_csv(self.get_database_metadata_file_path())
        data_frame.set_index("ecg_id", inplace=True)
        return data_frame.loc[record_id]

    def download_database_metadata(self):
        url = "https://www.physionet.org/files/ptb-xl/1.0.1/ptbxl_database.csv?download"
        content = requests.get(url).content
        metadata = pd.read_csv(StringIO(content.decode("utf-8")), index_col=0)
        metadata.to_csv(self.get_database_metadata_file_path())
        if not os.path.isfile(self.get_database_metadata_file_path()):
            raise FileNotDownloadedException(self.database_metadata_filename)
        # return url

    def get_scp_code_description(self, scp_code):
        if not os.path.isfile(self.get_scp_codes_file_path()):
            raise FileNotDownloadedException(filename='scp_statements.csv')
        data_frame = pd.read_csv(self.get_scp_codes_file_path(), index_col=0)
        data_row = data_frame.loc[scp_code]
        return DiagnosticCode.create(scp_code=scp_code, description=data_row[0])

    def download_scp_codes(self):
        url = "https://www.physionet.org/files/ptb-xl/1.0.1/scp_statements.csv?download"

        content = requests.get(url).content
        metadata = pd.read_csv(StringIO(content.decode("utf-8")), index_col=0)
        metadata.to_csv(self.get_scp_codes_file_path())
        if not os.path.isfile(self.get_scp_codes_file_path()):
            raise FileNotDownloadedException(self.scp_code_filename)
