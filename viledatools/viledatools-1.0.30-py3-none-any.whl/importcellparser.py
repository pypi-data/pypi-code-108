# coding=utf-8
"""
(C) FHCS GmbH

Class parsing value from MS Excel cell given, depending on Excel field key provided
"""

import inspect
import types
from datetime import datetime, timedelta
from typing import Any, List, Optional, Tuple, Union

import openpyxl
from openpyxl.cell.cell import Cell

from .fatask import FATask
from .viledaexceptions import ImportCellParserException
from .apiutils import strnorm


# noinspection PyPep8Naming
class ImportCellParser:
    """
    Class parsing value from MS Excel cell given, depending on Excel field key provided
    """
    def __init__(self, fieldkey: Optional[str] = None):
        """
        Gets the Excel field key and provides parse method for that value

        :param fieldkey: case insensitive string field key as specified in the Excel sheet
        """
        # Get class parsers list for field keys, method name have to start with "IQF" same as field key in Excel
        self._parsers_list = [n.upper() for n, v in inspect.getmembers(self, inspect.ismethod)
                              if (isinstance(v, types.MethodType) and n.upper()[:3] == "IQF")]
        if fieldkey is not None:
            if fieldkey not in self._parsers_list:
                raise ImportCellParserException(f"Unknown field key: {fieldkey}")
            self._method = getattr(self, fieldkey)

    def parse(self, cellobject: openpyxl.cell.cell.Cell) -> Any:
        """
        Parse value given cell object with chosen key field

        :param cellobject: openpyxl cell object to parse
        :return: value parsed from the cell
        """
        return self._method(cellobject)

    def getfieldtags(self):
        """
        Returns list of field key tags
        """
        return self._parsers_list

    def _parsenames(self, cellobject: openpyxl.cell.cell.Cell, sep: str) -> Union[List[str], None]:
        """
        Parse list of task owners from cell value, use given separator string

        :param cellobject: openpyxl cell object to parse
        :param sep: string to use as separator for str.split()
        :return: normalized task owners' names in a list() parsed from the cell
        """
        _value = cellobject.value
        # Trim and split by separators
        _value_raw_list = _value.strip().split(sep)
        # Normalize each item and filter out empty ones, fill filtered list
        _value_users_list = list()
        for _item in _value_raw_list:
            _trimmed_item = _item.strip()
            if _trimmed_item:
                _value_users_list.append(chr(0x0020).join(strnorm(_trimmed_item)))
        return _value_users_list if _value_users_list else None

    def _parse_spaces_list(self, cellobject: openpyxl.cell.cell.Cell, sep: str) -> Union[List[str], None]:
        """
        Parse list of space names from cell value, use given separator string

        :param cellobject: openpyxl cell object to parse
        :param sep: string to use as separator for str.split()
        :return: normalized task spaces' names in a list() parsed from the cell
        """
        _value = cellobject.value
        # Trim and split by separators
        _value_raw_list = _value.strip().split(sep)
        # Normalize each item and filter out empty ones, fill filtered list
        _value_spaces_list = list()
        for _item in _value_raw_list:
            _trimmed_item = _item.strip()
            if _trimmed_item:
                _value_spaces_list.append(chr(0x0020).join(strnorm(_trimmed_item)))
        return _value_spaces_list if _value_spaces_list else None

    def _parseyesno(self, cellobject: openpyxl.cell.cell.Cell) -> Union[bool, None]:
        """
        Parse "yes" / "no" type of values, it stringifies, trims, uppercases and matches with "yes" in
        the parsed list, in english, russian and german languages. So to return True this function have to find at least
        one "yes" in any of languages. If it is not found - it returns False.

        :param cellobject: openpyxl cell object to parse
        :return: True if cell value is parsed as yes, False otherwise
        """
        # Trim, uppercase and compare
        if str(cellobject.value).upper().strip() in ["ДА", "АГА", "Д", "YES", "YEP", "Y", "YEAH", "JA", "J"]:
            return True
        return False

    def _parseintseq(self, cellobject: openpyxl.cell.cell.Cell, allowedvals: List[int]) -> Union[List[str], None]:
        """
        Parse value of cell containing string with semicolon separated integers into a list of stringified integers,
        values in the MS Excel sheet must be given with ; (semicolon) separator

        :param cellobject: openpyxl cell object to parse
        :param allowedvals: list of allowed integers, if parsed integer not from this list, exception is raised
        :return: list of stringified integers parsed from the cell
        """
        # Trim and split by semicolons
        _value_raw_list = str(cellobject.value).strip().split(";")
        # Trim each item and filter out empty ones, fill filtered list
        _value_numbers_set = set()
        for _item in _value_raw_list:
            _trimmed_item = _item.strip()
            if _trimmed_item:
                try:
                    _trimmed_item_int = int(_trimmed_item)
                except Exception:
                    raise ImportCellParserException((f"_parseintseq(): Wrong value in the cell: "
                                                     f"{_trimmed_item}, values in the list must be integers divided by "
                                                     f"semicolons"))
                if _trimmed_item_int in allowedvals:
                    _value_numbers_set.add(str(_trimmed_item_int))
                else:
                    raise ImportCellParserException((f"_parseintseq(): Wrong value in the cell: "
                                                     f"{_trimmed_item_int}, integer values in the list must belong to "
                                                     f"{allowedvals}"))
        _value_numbers_list = list(_value_numbers_set)
        _value_numbers_list.sort()
        return _value_numbers_list

    def IQF001SITE(self, cellobject: openpyxl.cell.cell.Cell) -> Union[str, None]:
        """
        Parse site name, normalize with strnorm()

        :param cellobject: openpyxl cell object to parse
        :return: normalized site name string parsed from the cell
        """
        if not isinstance(cellobject, Cell):
            raise TypeError(f"Provided cell object type {type(cellobject)}, type openpyxl.cell.cell.Cell required")
        if cellobject.value is None:
            return None
        return chr(0x0020).join(strnorm(cellobject.value))

    def IQF002FLOOR(self, cellobject: openpyxl.cell.cell.Cell) -> Union[str, None]:
        """
        Parse floor name, normalize with strnorm()

        :param cellobject: openpyxl cell object to parse
        :return: normalized floor name parsed from the cell
        """
        if not isinstance(cellobject, Cell):
            raise TypeError(f"Provided cell object type {type(cellobject)}, type openpyxl.cell.cell.Cell required")
        if cellobject.value is None:
            return None
        return chr(0x0020).join(strnorm(cellobject.value))

    def IQF003SPACE(self, cellobject: openpyxl.cell.cell.Cell) -> Union[str, None]:
        """
        Parse space name, normalize with strnorm()

        :param cellobject: openpyxl cell object to parse
        :return: normalized space name parsed from the cell
        """
        if not isinstance(cellobject, Cell):
            raise TypeError(f"Provided cell object type {type(cellobject)}, type openpyxl.cell.cell.Cell required")
        if cellobject.value is None:
            return None
        return chr(0x0020).join(strnorm(cellobject.value))

    def IQF004TASKOWNERS(self, cellobject: openpyxl.cell.cell.Cell) -> Union[List[str], None]:
        """
        Parse list of task owners from cell value, return list of normalized names with strnorm(). In the
        MS Excel sheet cell value user names must be separated with ; (semicolon) symbol, empty values between
        separators will be just ignored.

        :param cellobject: openpyxl cell object to parse
        :return: normalized task owners' names in a list() parsed from the cell
        """
        if not isinstance(cellobject, Cell):
            raise TypeError(f"Provided cell object type {type(cellobject)}, type openpyxl.cell.cell.Cell required")
        if cellobject.value is None:
            return None
        if not isinstance(cellobject.value, str):
            raise ImportCellParserException((f"IQF004TASKOWNERS: Cell contents type is {type(cellobject.value)}, "
                                             f"string type required"))
        return self._parsenames(cellobject, ";")

    def IQF005TASKTIME(self, cellobject: openpyxl.cell.cell.Cell) -> Union[Tuple[timedelta, timedelta], None]:
        """
        Parse task start time and task end time into tuple

        :param cellobject: openpyxl cell object to parse
        :return: tuple (start time, end time) parsed from the cell
        """
        if not isinstance(cellobject, Cell):
            raise TypeError(f"Provided cell object type {type(cellobject)}, type openpyxl.cell.cell.Cell required")
        if cellobject.value is None:
            return None
        _value = cellobject.value
        if not isinstance(_value, str):
            raise ImportCellParserException((f"IQF005TASKTIME: Cell contents type is {type(_value)}, "
                                             f"string type required"))
        _value_split = _value.strip().split("-")
        if len(_value_split) != 2:
            raise ImportCellParserException((f"IQF005TASKTIME: Wrong cell contents {_value.strip()}, "
                                             f"must be strictly in format H:M-H:M"))
        _output = []
        for _value_split_item in _value_split:
            _value_split_item_split = _value_split_item.strip().split(":")
            if len(_value_split_item_split) != 2:
                raise ImportCellParserException((f"IQF005TASKTIME: Wrong cell contents {_value.strip()}, "
                                                 f"must be strictly in format H:M-H:M"))
            _value_h = _value_split_item_split[0].strip()
            _value_m = _value_split_item_split[1].strip()
            if _value_h and _value_m:
                try:
                    _value_h_int = int(_value_h)
                    _value_m_int = int(_value_m)
                    if 0 <= _value_h_int <= 23 and 0 <= _value_m_int <= 59:
                        _output.append(timedelta(hours=_value_h_int, minutes=_value_m_int))
                    else:
                        raise Exception
                except Exception:
                    raise ImportCellParserException((f"IQF005TASKTIME: Wrong cell contents {_value.strip()}, "
                                                     f"must be strictly in format H:M-H:M"))
            else:
                raise ImportCellParserException((f"IQF005TASKTIME: Wrong cell contents {_value.strip()}, "
                                                 f"must be strictly in format H:M-H:M"))
        return _output[0], _output[1]

    def IQF006TASKTITLE(self, cellobject: openpyxl.cell.cell.Cell) -> Union[str, None]:
        """
        Parse task title, apply spaces trimming

        :param cellobject: openpyxl cell object to parse
        :return: trimmed task title parsed from the cell
        """
        if not isinstance(cellobject, Cell):
            raise TypeError(f"Provided cell object type {type(cellobject)}, type openpyxl.cell.cell.Cell required")
        if cellobject.value is None:
            return None
        return str(cellobject.value).strip()

    def IQF007TASKDESCR(self, cellobject: openpyxl.cell.cell.Cell) -> Union[str, None]:
        """
        Parse task description, apply spaces trimming

        :param cellobject: openpyxl cell object to parse
        :return: trimmed task description text parsed from the cell
        """
        if not isinstance(cellobject, Cell):
            raise TypeError(f"Provided cell object type {type(cellobject)}, type openpyxl.cell.cell.Cell required")
        if cellobject.value is None:
            return None
        return str(cellobject.value).strip()

    def IQF008STARTDATE(self, cellobject: openpyxl.cell.cell.Cell) -> Union[datetime, None]:
        """
        Parse starting date for task reccurence planning, and if the task is planned as standalone, this is the date
        when this task is to be planned

        :param cellobject: openpyxl cell object to parse
        :return: task start date parsed from the cell
        """
        if not isinstance(cellobject, Cell):
            raise TypeError(f"Provided cell object type {type(cellobject)}, type openpyxl.cell.cell.Cell required")
        if cellobject.value is None:
            return None
        _value = cellobject.value
        if isinstance(_value, datetime):
            # Cell in MS Excel sheet formatted in date / time Excel format,
            # extract year, month, day from it as it is
            return datetime(_value.year, _value.month, _value.day)
        elif isinstance(_value, (int, float)):
            # Cell in MS Excel sheet formatted in numeric format, convert to the datetime
            if _value < 2:
                raise ImportCellParserException((f"IQF008STARTDATE: Start date provided as numeric value: {_value}, "
                                                 f"but the value is out of range, numerical date value must be not "
                                                 f"less than 2"))
            return datetime(1900, 1, 1) + timedelta(days=(_value - 2))
        elif isinstance(_value, str):
            # Cell in MS Excel sheet formatted as string, in this case it have to be formatted as %Y-%m-%d,
            # otherwise wrong result will be returned
            return datetime.strptime(_value, "%Y-%m-%d")

    def IQF009FREQTYPE(self, cellobject: openpyxl.cell.cell.Cell) -> Union[str, None]:
        """
        Parse frequency type for task planning, apply spaces trimming and uppercase

        :param cellobject: openpyxl cell object to parse
        :return: trimmed & uppercased frequency type parsed from the cell
        """
        if not isinstance(cellobject, Cell):
            raise TypeError(f"Provided cell object type {type(cellobject)}, type openpyxl.cell.cell.Cell required")
        if cellobject.value is None:
            return None
        _value_stripped_upper = str(cellobject.value).strip().upper()
        if _value_stripped_upper not in FATask.supportedfreqs():
            raise ImportCellParserException((f"IQF009FREQTYPE: Frequency type not supported by "
                                             f"parser: {_value_stripped_upper}"))
        return _value_stripped_upper

    def IQF010FREQINTVL(self, cellobject: openpyxl.cell.cell.Cell) -> Union[int, None]:
        """
        Parse frequency interval as integer, defines frequency of task planned recurrence

        :param cellobject: openpyxl cell object to parse
        :return: integer recurrence interval parsed from the cell
        """
        if not isinstance(cellobject, Cell):
            raise TypeError(f"Provided cell object type {type(cellobject)}, type openpyxl.cell.cell.Cell required")
        if cellobject.value is None:
            return None
        _value = cellobject.value
        try:
            _value_int = int(_value)
        except Exception:
            raise ImportCellParserException(f"IQF010FREQINTVL: Wrong value in the cell: {_value}, must be integer")
        if _value_int < 1:
            raise ImportCellParserException((f"IQF010FREQINTVL: Value in the cell: {_value} out of range, "
                                             f"frequency interval must be greater than 0"))
        return _value_int

    def IQF011FREQDAYS(self, cellobject: openpyxl.cell.cell.Cell) -> Union[List[str], None]:
        """
        Parse task recurrence days as list of stringified integers, where ["1", "2", "3", "4", "5", "6", "7"]
        corresponds to [Mon, Tue, Wed, Thu, Fri, Sat, Sun], list values in the MS Excel sheet must
        be given with ; (semicolon) separator

        :param cellobject: openpyxl cell object to parse
        :return: list of stringified integers parsed from the cell
        """
        if not isinstance(cellobject, Cell):
            raise TypeError(f"Provided cell object type {type(cellobject)}, type openpyxl.cell.cell.Cell required")
        if cellobject.value is None:
            return None
        if not isinstance(cellobject.value, (str, int)):
            raise ImportCellParserException((f"IQF011FREQDAYS: Cell contents type is {type(cellobject.value)}, "
                                             f"string type required"))
        return self._parseintseq(cellobject, [1, 2, 3, 4, 5, 6, 7])

    def IQF012ATMID(self, cellobject: openpyxl.cell.cell.Cell) -> Union[int, None]:
        """
        Made for mosklining domain

        Parse ATM ID, convert to int

        :param cellobject: openpyxl cell object to parse
        :return: int ATM ID parsed from the cell
        """
        if not isinstance(cellobject, Cell):
            raise TypeError(f"Provided cell object type {type(cellobject)}, type openpyxl.cell.cell.Cell required")
        if cellobject.value is None:
            return None
        _value = cellobject.value
        try:
            _value_int = int(_value)
        except Exception:
            raise ImportCellParserException(f"IQF012ATMID: Wrong value in the cell: {_value}, must be integer")
        if _value_int < 0:
            raise ImportCellParserException((f"IQF012ATMID: Value in the cell: {_value} out of range, "
                                             f"frequency interval can not be less than 0"))
        return _value_int

    def IQF013ATMADDR(self, cellobject: openpyxl.cell.cell.Cell) -> Union[str, None]:
        """
        Made for mosklining domain

        Parse address, trim spaces

        :param cellobject: openpyxl cell object to parse
        :return: stringified and trimmed cell value
        """
        if not isinstance(cellobject, Cell):
            raise TypeError(f"Provided cell object type {type(cellobject)}, type openpyxl.cell.cell.Cell required")
        if cellobject.value is None:
            return None
        return str(cellobject.value).strip()

    def IQF014ATMISOFFICE(self, cellobject: openpyxl.cell.cell.Cell) -> Union[bool, None]:
        """
        Made for mosklining domain

        Parse yes or no if ATM is in the office, trim spaces

        :param cellobject: openpyxl cell object to parse
        :return: True if cell value is parsed as yes, False otherwise
        """
        if not isinstance(cellobject, Cell):
            raise TypeError(f"Provided cell object type {type(cellobject)}, type openpyxl.cell.cell.Cell required")
        if cellobject.value is None:
            return None
        return self._parseyesno(cellobject)

    def IQF015ATMISPUBLIC(self, cellobject: openpyxl.cell.cell.Cell) -> Union[bool, None]:
        """
        Made for mosklining domain

        Parse yes or no if ATM is in publicly accessible area, trim spaces

        :param cellobject: openpyxl cell object to parse
        :return: True if cell value is parsed as yes, False otherwise
        """
        if not isinstance(cellobject, Cell):
            raise TypeError(f"Provided cell object type {type(cellobject)}, type openpyxl.cell.cell.Cell required")
        if cellobject.value is None:
            return None
        return self._parseyesno(cellobject)

    def IQF016ATMISNFC(self, cellobject: openpyxl.cell.cell.Cell) -> Union[bool, None]:
        """
        Made for mosklining domain

        Parse yes or no if ATM has NFC functionality, trim spaces

        :param cellobject: openpyxl cell object to parse
        :return: True if cell value is parsed as yes, False otherwise
        """
        if not isinstance(cellobject, Cell):
            raise TypeError(f"Provided cell object type {type(cellobject)}, type openpyxl.cell.cell.Cell required")
        if cellobject.value is None:
            return None
        return self._parseyesno(cellobject)

    def IQF017ATMMODEL(self, cellobject: openpyxl.cell.cell.Cell) -> Union[str, None]:
        """
        Made for mosklining domain

        Parse ATM model string, trim spaces

        :param cellobject: openpyxl cell object to parse
        :return: stringified and trimmed cell value
        """
        if not isinstance(cellobject, Cell):
            raise TypeError(f"Provided cell object type {type(cellobject)}, type openpyxl.cell.cell.Cell required")
        if cellobject.value is None:
            return None
        return str(cellobject.value).strip()

    def IQF018ATMCURR(self, cellobject: openpyxl.cell.cell.Cell) -> Union[str, None]:
        """
        Made for mosklining domain

        Parse ATM available currencies description, trim spaces

        :param cellobject: openpyxl cell object to parse
        :return: stringified and trimmed cell value
        """
        if not isinstance(cellobject, Cell):
            raise TypeError(f"Provided cell object type {type(cellobject)}, type openpyxl.cell.cell.Cell required")
        if cellobject.value is None:
            return None
        return str(cellobject.value).strip()

    def IQF019ATMSERIAL(self, cellobject: openpyxl.cell.cell.Cell) -> Union[str, None]:
        """
        Made for mosklining domain

        Parse ATM serial number, trim spaces

        :param cellobject: openpyxl cell object to parse
        :return: stringified and trimmed cell value
        """
        if not isinstance(cellobject, Cell):
            raise TypeError(f"Provided cell object type {type(cellobject)}, type openpyxl.cell.cell.Cell required")
        if cellobject.value is None:
            return None
        return str(cellobject.value).strip()

    def IQF020ATMCOMMENT(self, cellobject: openpyxl.cell.cell.Cell) -> Union[str, None]:
        """
        Made for mosklining domain

        Parse comment cell, trim spaces

        :param cellobject: openpyxl cell object to parse
        :return: stringified and trimmed cell value
        """
        if not isinstance(cellobject, Cell):
            raise TypeError(f"Provided cell object type {type(cellobject)}, type openpyxl.cell.cell.Cell required")
        if cellobject.value is None:
            return None
        return str(cellobject.value).strip()

    def IQF021FREQMONTHS(self, cellobject: openpyxl.cell.cell.Cell) -> Union[List[str], None]:
        """
        Parse task recurrence months as list of stringified integers, where
        ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"] corresponds to
        [Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec], list values in the MS Excel sheet must
        be given with ; (semicolon) separator

        :param cellobject: openpyxl cell object to parse
        :return: list of stringified integers parsed from the cell
        """
        if not isinstance(cellobject, Cell):
            raise TypeError(f"Provided cell object type {type(cellobject)}, type openpyxl.cell.cell.Cell required")
        if cellobject.value is None:
            return None
        if not isinstance(cellobject.value, (str, int)):
            raise ImportCellParserException((f"IQF021FREQMONTHS: Cell contents type is {type(cellobject.value)}, "
                                             f"string type required"))
        return self._parseintseq(cellobject, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])

    def IQF022SAMEDAYOFWEEK(self, cellobject: openpyxl.cell.cell.Cell) -> Union[bool, None]:
        """
        If monthly recurrence is set, then this parameter defines whether task repeats same day of the week, or same
        date of each month

        If "yes" then task will repeat same day of the same week as first date of the task, if "no" - then task
        will repeat same date of the month

        :param cellobject: openpyxl cell object to parse
        :return: True if cell value is parsed as yes, False otherwise
        """
        if not isinstance(cellobject, Cell):
            raise TypeError(f"Provided cell object type {type(cellobject)}, type openpyxl.cell.cell.Cell required")
        if cellobject.value is None:
            return None
        return self._parseyesno(cellobject)

    def IQF023LANGUAGE(self, cellobject: openpyxl.cell.cell.Cell) -> Union[str, None]:
        """
        Parse language, one of suported languages

        :param cellobject: openpyxl cell object to parse
        :return: trimmed & lowercased language
        """
        if not isinstance(cellobject, Cell):
            raise TypeError(f"Provided cell object type {type(cellobject)}, type openpyxl.cell.cell.Cell required")
        if cellobject.value is None:
            return None
        _value_stripped_lower = str(cellobject.value).strip().lower()
        if _value_stripped_lower not in ["ru", "en", "de"]:
            raise ImportCellParserException((f"IQF023LANGUAGE: Language not supported by "
                                             f"parser: {_value_stripped_lower}"))
        return _value_stripped_lower

    def IQF024NFCSPACESBEGIN(self, cellobject: openpyxl.cell.cell.Cell) -> Union[List[str], None]:
        """
        Space list used to detect begin cleaning of the room by NFC linked to the space.

        Parse list of spaces from cell value, return list of normalized names of spaces with strnorm(). In the
        MS Excel sheet cell value space names must be separated with ; (semicolon) symbol, empty values between
        separators will be just ignored.

        :param cellobject: openpyxl cell object to parse
        :return: normalized spaces' names in a list() parsed from the cell
        """
        if not isinstance(cellobject, Cell):
            raise TypeError(f"Provided cell object type {type(cellobject)}, type openpyxl.cell.cell.Cell required")
        if cellobject.value is None:
            return None
        if not isinstance(cellobject.value, str):
            raise ImportCellParserException((f"IQF024NFCSPACESBEGIN: Cell contents type is {type(cellobject.value)}, "
                                             f"string type required"))
        return self._parse_spaces_list(cellobject, ";")

    def IQF025NFCSPACESDONE(self, cellobject: openpyxl.cell.cell.Cell) -> Union[List[str], None]:
        """
        Space list used to detect done cleaning of the room by NFC linked to the space.

        Parse list of spaces from cell value, return list of normalized names of spaces with strnorm(). In the
        MS Excel sheet cell value space names must be separated with ; (semicolon) symbol, empty values between
        separators will be just ignored.

        :param cellobject: openpyxl cell object to parse
        :return: normalized spaces' names in a list() parsed from the cell
        """
        if not isinstance(cellobject, Cell):
            raise TypeError(f"Provided cell object type {type(cellobject)}, type openpyxl.cell.cell.Cell required")
        if cellobject.value is None:
            return None
        if not isinstance(cellobject.value, str):
            raise ImportCellParserException((f"IQF025NFCSPACESDONE: Cell contents type is {type(cellobject.value)}, "
                                             f"string type required"))
        return self._parse_spaces_list(cellobject, ";")

    def IQF026NFCREFORDER(self, cellobject: openpyxl.cell.cell.Cell) -> Union[int, None]:
        """
        NFC task cpmpletion reference order

        :param cellobject: openpyxl cell object to parse
        :return: int order parsed from the cell
        """
        if not isinstance(cellobject, Cell):
            raise TypeError(f"Provided cell object type {type(cellobject)}, type openpyxl.cell.cell.Cell required")
        if cellobject.value is None:
            return None
        _value = cellobject.value
        try:
            _value_int = int(_value)
        except Exception:
            raise ImportCellParserException(f"IQF026NFCREFORDER: Wrong value in the cell: {_value}, must be integer")
        return _value_int

    def IQF027NFCALGORITHM(self, cellobject: openpyxl.cell.cell.Cell) -> Union[str, None]:
        """
        Parse algorithm name for NFC automatic task completion

        :param cellobject: openpyxl cell object to parse
        :return: trimmed & lowercased language
        """
        if not isinstance(cellobject, Cell):
            raise TypeError(f"Provided cell object type {type(cellobject)}, type openpyxl.cell.cell.Cell required")
        if cellobject.value is None:
            return None
        _value_stripped_lower = str(cellobject.value).strip().lower()
        return _value_stripped_lower

    def IQF028TASKDURATION(self, cellobject: openpyxl.cell.cell.Cell) -> Union[timedelta, None]:
        """
        Parse task duration into timedelta

        :param cellobject: openpyxl cell object to parse
        :return: duration timedelta parsed from the cell
        """
        if not isinstance(cellobject, Cell):
            raise TypeError(f"Provided cell object type {type(cellobject)}, type openpyxl.cell.cell.Cell required")
        if cellobject.value is None:
            return None
        _value = cellobject.value
        if not isinstance(_value, str):
            raise ImportCellParserException((f"IQF028TASKDURATION: Cell contents type is {type(_value)}, "
                                             f"string type required"))
        _value_split_item = _value.strip()
        _value_split_item_split = _value_split_item.strip().split(":")
        if len(_value_split_item_split) != 3:
            raise ImportCellParserException((f"IQF028TASKDURATION: Wrong cell contents {_value.strip()}, "
                                             f"must be strictly in format H:M:S"))
        _output = None
        _value_h = _value_split_item_split[0].strip()
        _value_m = _value_split_item_split[1].strip()
        _value_s = _value_split_item_split[2].strip()
        if _value_h and _value_m and _value_s:
            try:
                _value_h_int = int(_value_h)
                _value_m_int = int(_value_m)
                _value_s_int = int(_value_s)
                if 0 <= _value_h_int <= 23 and 0 <= _value_m_int <= 59 and 0 <= _value_s_int <= 59:
                    _output = timedelta(hours=_value_h_int, minutes=_value_m_int, seconds=_value_s_int)
                else:
                    raise Exception
            except Exception:
                raise ImportCellParserException((f"IQF028TASKDURATION: Wrong cell contents {_value.strip()}, "
                                                 f"must be strictly in format H:M:S"))
        else:
            raise ImportCellParserException((f"IQF028TASKDURATION: Wrong cell contents {_value.strip()}, "
                                             f"must be strictly in format H:M:S"))
        return _output

    def IQF029NFCSPACESCONTROL(self, cellobject: openpyxl.cell.cell.Cell) -> Union[List[str], None]:
        """
        Space list used to detect control of cleaning of the room by NFC linked to the space.

        Parse list of spaces from cell value, return list of normalized names of spaces with strnorm(). In the
        MS Excel sheet cell value space names must be separated with ; (semicolon) symbol, empty values between
        separators will be just ignored.

        :param cellobject: openpyxl cell object to parse
        :return: normalized spaces' names in a list() parsed from the cell
        """
        if not isinstance(cellobject, Cell):
            raise TypeError(f"Provided cell object type {type(cellobject)}, type openpyxl.cell.cell.Cell required")
        if cellobject.value is None:
            return None
        if not isinstance(cellobject.value, str):
            raise ImportCellParserException((f"IQF029NFCSPACESCONTROL: Cell contents type is {type(cellobject.value)}, "
                                             f"string type required"))
        return self._parse_spaces_list(cellobject, ";")

    def IQF030NFCSITE(self, cellobject: openpyxl.cell.cell.Cell) -> Union[str, None]:
        """
        Parse site name, normalize with strnorm()

        :param cellobject: openpyxl cell object to parse
        :return: normalized site name string parsed from the cell
        """
        if not isinstance(cellobject, Cell):
            raise TypeError(f"Provided cell object type {type(cellobject)}, type openpyxl.cell.cell.Cell required")
        if cellobject.value is None:
            return None
        return chr(0x0020).join(strnorm(cellobject.value))

    def IQF031NFCFLOOR(self, cellobject: openpyxl.cell.cell.Cell) -> Union[str, None]:
        """
        Parse floor name, normalize with strnorm()

        :param cellobject: openpyxl cell object to parse
        :return: normalized floor name parsed from the cell
        """
        if not isinstance(cellobject, Cell):
            raise TypeError(f"Provided cell object type {type(cellobject)}, type openpyxl.cell.cell.Cell required")
        if cellobject.value is None:
            return None
        return chr(0x0020).join(strnorm(cellobject.value))
