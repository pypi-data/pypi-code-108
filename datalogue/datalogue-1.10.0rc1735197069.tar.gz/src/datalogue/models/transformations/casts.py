from typing import List, Union, Optional
from datalogue.errors import DtlError, _property_not_found
from datalogue.models.transformations.commons import Transformation
from datalogue.dtl_utils import _parse_string_list


class ToInt(Transformation):
    """
      Allows to casts a node value to int
      """

    type_str = "ToInt"

    def __init__(self, path: List[str]):
        """
        Builds a Casting transformation to Int

        :param path: path to node to be cast to Int
        """
        Transformation.__init__(self, ToInt.type_str)
        self.path = path

    def __eq__(self, other: "ToInt"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"ToInt({self.path})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["path"] = self.path
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "ToInt"]:
        path = json.get("path")
        if path is None:
            return _property_not_found("path", json)

        path = _parse_string_list(path)
        if isinstance(path, DtlError):
            return path

        return ToInt(path)


class ToDouble(Transformation):
    """
      Allows to casts a node value to double
      """

    type_str = "ToDouble"

    def __init__(self, path: List[str]):
        """
        Builds a Casting transformation to Double

        :param path: path to node to be cast to Double
        """
        Transformation.__init__(self, ToDouble.type_str)
        self.path = path

    def __eq__(self, other: "ToDouble"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"ToDouble(path= {self.path})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["path"] = self.path
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "ToDouble"]:
        path = json.get("path")
        if path is None:
            return _property_not_found("path", json)

        path = _parse_string_list(path)
        if isinstance(path, DtlError):
            return path

        return ToDouble(path)


class JsonStringify(Transformation):
    """
        Selects a tree under the node of the supplied field Address.
        That tree is removed from the adg and is the replaced with a node at the same address.
        That new node has as a value the Json version of the tree that was removed.
      """

    type_str = "JsonStringify"

    def __init__(self, field_address: List[str], optional_input: bool = False):
        """
        Builds a transformation to turn a tree to json

        :param field_address: path to root of the tree to transform as a Json string
        :param optional_input: if the path is not found in the schema, will not return an error
        """
        Transformation.__init__(self, JsonStringify.type_str)
        self.field_address = field_address
        self.optional_input = optional_input

    def __eq__(self, other: "JsonStringify"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"JsonStringify(field_address= {self.field_address}, optional_input= {self.optional_input})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["fieldAddress"] = self.field_address
        base["optionalInput"] = self.optional_input
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "JsonStringify"]:
        path = json.get("fieldAddress")
        if path is None:
            return _property_not_found("fieldAddress", json)

        path = _parse_string_list(path)
        if isinstance(path, DtlError):
            return path

        optional_input = json.get("optionalInput")
        if optional_input is None:
            return _property_not_found("optionalInput", json)

        return JsonStringify(path, optional_input)


class ToDate(Transformation):
    """
    Allows to casts a node value to a date time with timezone.

    You can use the following symbols in the formatting string::

        Symbol  Meaning                     Presentation      Examples
        ------  -------                     ------------      -------
        G       era                         text              AD; Anno Domini; A
        u       year                        year              2004; 04
        y       year-of-era                 year              2004; 04
        D       day-of-year                 number            189
        M/L     month-of-year               number/text       7; 07; Jul; July; J
        d       day-of-month                number            10

        Q/q     quarter-of-year             number/text       3; 03; Q3; 3rd quarter
        Y       week-based-year             year              1996; 96
        w       week-of-week-based-year     number            27
        W       week-of-month               number            4
        E       day-of-week                 text              Tue; Tuesday; T
        e/c     localized day-of-week       number/text       2; 02; Tue; Tuesday; T
        F       week-of-month               number            3

        a       am-pm-of-day                text              PM
        h       clock-hour-of-am-pm (1-12)  number            12
        K       hour-of-am-pm (0-11)        number            0
        k       clock-hour-of-am-pm (1-24)  number            0

        H       hour-of-day (0-23)          number            0
        m       minute-of-hour              number            30
        s       second-of-minute            number            55
        S       fraction-of-second          fraction          978
        A       milli-of-day                number            1234
        n       nano-of-second              number            987654321
        N       nano-of-day                 number            1234000000

        V       time-zone ID                zone-id           America/Los_Angeles; Z; -08:30
        z       time-zone name              zone-name         Pacific Standard Time; PST
        O       localized zone-offset       offset-O          GMT+8; GMT+08:00; UTC-08:00;
        X       zone-offset 'Z' for zero    offset-X          Z; -08; -0830; -08:30; -083015; -08:30:15;
        x       zone-offset                 offset-x          +0000; -08; -0830; -08:30; -083015; -08:30:15;
        Z       zone-offset                 offset-Z          +0000; -0800; -08:00;
        julian  JDE Julian Date Format      text              120060 (equivalent to 29/02/2020, midnight time)
      """

    type_str = "ToDate"

    def __init__(
        self, path: List[str], date_format: Optional[List[str]] = None, optional_input: bool = False,
    ):
        """
        Builds a Casting transformation to a datetime with timezone

        :param path: path to node to be cast to Int
        :param date_format: List of formats to be used to attempt to parse the string. Defaults to [YYYY-MM-DDTHH:mm:ss.VVZ]
        """
        Transformation.__init__(self, ToDate.type_str)
        self.path = path
        self.date_format = date_format
        self.optional_input = optional_input

    def __eq__(self, other: "ToDate"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return (
            f"ToDate(path= {self.path!r}, date_format= {self.date_format!r}, optional_input= {self.optional_input!r})"
        )

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["path"] = self.path
        base["dateFormats"] = self.date_format
        base["optionalInput"] = self.optional_input
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "ToDate"]:
        path = json.get("path")
        dateformats = json.get("dateFormats")
        if path is None:
            return _property_not_found("path", json)

        if dateformats is None:
            return _property_not_found("dateFormats", json)

        optional_input = json.get("optionalInput")
        if optional_input is None:
            optional_input = False

        path = _parse_string_list(path)
        dateformats = _parse_string_list(dateformats)
        if isinstance(path, DtlError):
            return path
        if isinstance(dateformats, DtlError):
            return dateformats

        return ToDate(path, dateformats, optional_input)


class FormatDate(Transformation):
    """
    Formats a timestamp datapoint to a string. For help formatting your date, please follow java guidelines:
    https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/text/SimpleDateFormat.html

    :param path: path to the field to format as a list of strings, e.g. ["DOB"] targets the field "DOB". If there is
    more than one field in the dataset named as such, use a list of strings to provide an address to your target field
    :param output_date_format: output format of the date as a string following java datetime standards
    """

    type_str = "DateStringFormatter"

    def __init__(self, path: List[str], output_date_format: str):
        Transformation.__init__(self, FormatDate.type_str)
        self.path = path
        self.output_date_format = output_date_format

    def __eq__(self, other: "FormatDate"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"FormatDate(path= {self.path!r}, " f"output_date_format= {self.output_date_format!r})"

    def _as_payload(self) -> Union[dict, DtlError]:
        if not isinstance(self.path, List):
            return DtlError("Path must be a list of string describing the path to the target field")
        if not isinstance(self.output_date_format, str):
            return DtlError("Output date format must be a string, following Java guidelines")
        base = {
            "type": "DateStringFormatter",
            "path": self.path,
            "outputDateFormat": self.output_date_format,
        }
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "FormatDate"]:
        path_from_payload = json.get("path")
        output_date_format = json.get("outputDateFormat")
        if path_from_payload is None:
            return _property_not_found("path", json)

        if output_date_format is None:
            return _property_not_found("outputDateFormat", json)

        path = _parse_string_list(path_from_payload)

        if isinstance(path, DtlError):
            return path
        if isinstance(output_date_format, DtlError):
            return output_date_format

        return FormatDate(path, output_date_format,)


class ToMacAddress(Transformation):
    """
      Allows to casts a node value to MacAddress
      """

    type_str = "ToMacAddress"

    def __init__(self, path: List[str]):
        """
        Builds a Casting transformation to MacAddress
        :param path: path to node to be cast to MacAddress
        """
        Transformation.__init__(self, ToMacAddress.type_str)
        self.path = path

    def __eq__(self, other: "ToMacAddress"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"ToMacAddress({self.path})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["path"] = self.path
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "ToMacAddress"]:
        path = json.get("path")
        if path is None:
            return _property_not_found("path", json)

        path = _parse_string_list(path)
        if isinstance(path, DtlError):
            return path

        return ToMacAddress(path)

class ToUUID(Transformation):
    """
    Allows casting of a node value to a UUID
    """
    type_str = "ToUUID"

    def __init__(self, path: List[str]):
        """
        Builds a Casting transformation to UUID

        :param path: path to node to be cast to UUID
        """
        Transformation.__init__(self, ToUUID.type_str)
        self.path = path

    def __eq__(self, other: "ToUUID"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"ToUUID({self.path})"
    
    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["path"] = self.path
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "ToUUID"]:

        path = json.get("path")
        if path is None:
            return _property_not_found("path", json)

        path = _parse_string_list(path)
        if isinstance(path, DtlError):
            return path

        return ToUUID(path)
