import csv
import logging
import os

TRUSTED_CHECK_AND_LIBS_FILE = os.path.join(
    os.path.dirname(__file__), "lib_files", "trusted_file_hashes.csv"
)
UNTRUSTED_CHECK_AND_LIBS_FILE = os.path.join(
    os.path.dirname(__file__), "lib_files", "untrusted_file_hashes.csv"
)


logger = logging.getLogger(__name__)


class TrustedDataCollector(object):
    """
    collect trusted data
    """

    def __init__(
        self,
        trusted_check_and_lib_file=TRUSTED_CHECK_AND_LIBS_FILE,
        untrusted_check_and_libs_file=UNTRUSTED_CHECK_AND_LIBS_FILE,
    ):

        self._trusted_check_and_libs_file = trusted_check_and_lib_file
        self._untrusted_check_and_libs_file = untrusted_check_and_libs_file
        self._trusted_check_and_libs = set()
        self._untrusted_check_and_libs = set()
        self._process_trusted_data()

    def get_trusted_check_and_libs(self):
        return self._trusted_check_and_libs

    def get_untrusted_check_and_libs(self):
        return self._untrusted_check_and_libs

    def _process_trusted_data(self):
        if os.path.exists(self._trusted_check_and_libs_file):
            for check_name, file_hash in self._read_lib_file(
                self._trusted_check_and_libs_file
            ):
                self._trusted_check_and_libs.add((check_name, file_hash))
        else:
            logger.warning(
                "trustedlibs source file `%s` is not found",
                self._trusted_check_and_libs_file,
            )

        if os.path.exists(self._untrusted_check_and_libs_file):
            for check_name, file_hash in self._read_lib_file(
                self._untrusted_check_and_libs_file
            ):
                self._untrusted_check_and_libs.add((check_name, file_hash))
        else:
            logger.warning(
                "trustedlibs source file `%s` is not found",
                self._untrusted_check_and_libs_file,
            )

    @staticmethod
    def _read_lib_file(source_file):

        with open(source_file, "r") as f:
            filereader = csv.DictReader(f)
            for line in filereader:
                yield line["check_name"], line["file_hash"]
