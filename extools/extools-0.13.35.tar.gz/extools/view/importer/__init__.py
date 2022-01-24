import warnings
import openpyxl

from pathlib import Path

from extools.message import logger_for_module
from extools.error_stack import consume_errors

class ExcelImporter():

    def __init__(self):
        self.objects_imported = []
        self.errors = []
        self.log = logger_for_module("extools.excel_importer")
        self.log.debug("Excel Importer initialized.")

    def open_worksheet(self, filepath):
        """Open and validate a worksheet.

        Opens the worksheet, sets it on the class, and runs
        ``worksheet_validators`` against it.

        :param path: a path-like object for the file to import.
        :type path: pathlib.Path
        :returns: (valid, [[obj, action, error_message], ... ])
        :rtype: (bool, [[str, str, str], ... ])
        """
        errors = []
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.wb = openpyxl.load_workbook(
                        filepath.open('rb'), read_only=True, data_only=True)
        except Exception as err:
            msg = "Couldn't open workbook at {}: {}.".format(filepath, err)
            errors.append(['excel', 'open', msg, ])
            return (False, errors)

        if len(self.wb.worksheets) > 0:
            self.ws = self.wb.worksheets[0]
        else:
            msg = "Unable to find any worksheets in {}.".format(filepath)
            errors.append(['excel', 'open', msg, ])
            return (False, errors)

        self.ws.calculate_dimension(force=True)
        worksheet_validators = [method for method in self.__dir__()
                                if method.startswith('validate_worksheet')]

        for validator in worksheet_validators:
            if hasattr(self, validator):
                valid, msg = getattr(self, validator)(self.ws)
                if not valid:
                    errors.append(['excel', 'validate', msg])

        self.log.debug("Opened workbook {}. Errors: {}".format(filepath, errors))
        return (self.ws, errors, )
