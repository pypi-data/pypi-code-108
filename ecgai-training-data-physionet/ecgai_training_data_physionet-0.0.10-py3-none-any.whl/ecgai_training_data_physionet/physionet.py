from abc import ABC, abstractmethod

import numpy as np
import wfdb
from ecgai_logging.log_decorator import log
from numpy.distutils.fcompiler import none
from wfdb import Record

from ecgai_training_data_physionet.models import EcgRecord, EcgLeadRecord


def module_name():
    return __name__


class IPhysioNetDataSet(ABC):
    data_set_name: str

    @abstractmethod
    def load(self):
        """
        Download and setup all required files
        """
        NotImplementedError()

    @abstractmethod
    def is_loaded(self) -> bool:
        """

        """

    # noinspection PyTypeChecker
    @abstractmethod
    async def get_records_list(self) -> list[str]:
        """
        Returns a list of all records from a database on physionet
        Returns:
            list[str]:

        """
        NotImplementedError()

    # noinspection PyTypeChecker
    @abstractmethod
    async def get_record(self, record_path_name: str) -> EcgRecord:
        """

        Args:
            record_path_name (str):

        Returns:
            EcgRecord:
        """
        NotImplementedError()

    # noinspection PyTypeChecker
    @staticmethod
    @abstractmethod
    def is_valid_sample_rate(sample_rate: int) -> bool:
        """

        Parameters
        ----------
        sample_rate

        Returns
        -------
        bool

        """
        NotImplementedError()

    # noinspection PyTypeChecker
    @staticmethod
    @abstractmethod
    def is_valid_record_id(record_id: int) -> bool:
        """

        Parameters
        ----------
        record_id

        Returns
        -------
        bool
        """
        NotImplementedError()


class PhysioNetDataSet(IPhysioNetDataSet):
    def is_loaded(self) -> bool:
        pass

    def load(self):
        pass

    # LOCATION = os.path.dirname(os.path.abspath(__file__))

    def __init__(self, data_set_name: str):
        self.data_set_name = data_set_name
        self.data_set_location = "physionet"
        self.load()

    # noinspection PyTypeChecker
    async def get_records_list(self) -> list[str]:
        NotImplementedError()

    # noinspection PyTypeChecker
    async def get_record(self, record_path_name: str) -> EcgRecord:
        NotImplementedError()

    # noinspection PyTypeChecker
    @staticmethod
    def is_valid_sample_rate(sample_rate: int) -> bool:
        NotImplementedError()

    # noinspection PyTypeChecker
    @staticmethod
    def is_valid_record_id(record_id: int) -> bool:
        NotImplementedError()

    @staticmethod
    @log
    def create_signal_array(record: Record) -> list[EcgLeadRecord]:
        """

        Args:
            record (wfdb.Record):

        Returns:
            List[float]:

        """
        try:
            # create an array with the inverse shape of the p_signal array
            # output_leads = np.zeros(shape=[record.p_signal.shape[1], record.p_signal.shape[0]])
            i = 0
            leads = []
            while i < record.n_sig:
                p_lead = np.array(record.p_signal[:, i])
                # output_leads[i] = p_lead
                lead_name = record.sig_name[i]
                # lead_list = p_lead.tolist()
                lead_list = list(p_lead)
                lead = EcgLeadRecord.create(lead_name, lead_list)
                leads.append(lead)
                i += 1
            return leads

        except Exception as e:
            print("Unexpected error:", e.args)


class InValidRecordException(Exception):
    @log
    def __init__(self, record_id: int = none, data_base_name: str = none):
        message = "The record was not found"
        if record_id is not none:
            message += "record name and path %s" % record_id
        if data_base_name is not none:
            message += "from %s" % data_base_name
        super(InValidRecordException, self).__init__(message)


class FileNotDownloadedException(Exception):
    def __init__(self, filename: str):
        message = f"{filename} was not downloaded"
        super(FileNotDownloadedException, self).__init__(message)
