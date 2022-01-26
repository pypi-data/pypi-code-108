import datetime
from typing import Dict, Union, List

from enginelib.errors import Error
from enginelib.rds.client import db_client, db_name


class ICD10:
    def __init__(self, service_date: datetime.date = None, code_min: str = None, code_max: str = None, code_type: str = "valid"):
        self.icd10_hash: Dict[str, str] = dict()
        self.service_date = service_date
        self.code_min, self.code_max = code_min, code_max
        self.code_type = code_type

    def __contains__(self, code: str) -> bool:
        return self.is_valid(code)

    def description(self, code: str) -> str:
        formatted_code = code.replace(".", "")
        if code not in self.icd10_hash:
            self.icd10_hash[code] = self._fetch_description(formatted_code, self.service_date, self.code_type)

        return self.icd10_hash[code]

    @staticmethod
    def _fetch_description(code: str, service_date: datetime.date, code_type: str) -> str:
        """If 'code' is in the ICD10 dataset pertaining the effective date of the CUE,
        and if the DB query was successful, this function returns a non-zero length description of the given ICD10 code.
        If the DB query was not successful, this function raises a DataError.
        If the DB query was successful, but the code was not in the DB, this
        function returns an empty string."""

        # The validity period of an icd10 dataset for a given year goes from OCT 1 of the previous year
        # to SEP 30 of the next
        # So the validity period of the 2022 dataset goes from OCT 1 2021 to SEP 30 2022
        year = service_date.year
        if service_date >= datetime.date(year, 8, 1):
            year = year + 1

        table_name = f"icd10_{year}" if year is not None else "icd10"
        # noinspection SqlResolve
        query = f'''
        SELECT "description" 
        FROM {db_name}.{table_name}
        WHERE "code"='{code}' AND "code_type"='{code_type}';
        '''

        print(query)
        ref_data, err = db_client.GetReferenceData("multi_policy_prefilter", query)
        if err:
            raise Error(f'Not able to access ICD10 reference data: {err}.')
        try:
            if ref_data is None or not isinstance(ref_data, list) or len(ref_data) == 0:
                return ''
            return ref_data[0]['description'].strip('"')
        except (IndexError, KeyError, TypeError):
            raise Error(f'Not able to access ICD10 reference data to fetch description for code {code}.')

    def is_valid(self, code: str) -> bool:
        description = self.description(code)
        return description != ''

    def in_range(self, code: str) -> bool:
        """The comparison below is alphanumeric (i.e. string)."""
        try:
            return self.code_min <= code <= self.code_max and self.is_valid(code)
        except TypeError:
            raise Error(f"Either the code minimum: {self.code_min} or the code maximum: {self.code_max} "
                        f"is not a string.")


class ICD10Collection:
    """Stores a collection of individual ICD10 codes and/or ICD10 ranges."""
    def __init__(self):
        self._hash: Dict[str, bool] = dict()
        self._ranges: List[ICD10] = list()
        super().__init__()

    def add(self, obj: Union[str, ICD10]):
        if isinstance(obj, str):
            self._hash[obj] = True
        else:
            self._ranges.append(obj)

    def __contains__(self, code: str) -> bool:
        if code in self._hash:
            return True
        for _range in self._ranges:
            if _range.in_range(code):
                return True
        return False

    @classmethod
    def construct(cls, icd_list_of_codes_and_ranges: str, service_date: datetime.date = None) -> 'ICD10Collection':
        # Split given list using comma or pipe as a separator
        normalized_icd_list = icd_list_of_codes_and_ranges.replace(',', '|')
        items = [item.strip() for item in normalized_icd_list.split('|')]

        icd10_collection = ICD10Collection()
        for item in items:
            if '-' in item:
                try:
                    code_min, code_max = [code.strip() for code in item.split('-')]
                except ValueError:
                    raise Error(f'The entry {item} is a malformed range of ICD10 codes.')
                icd10_collection.add(ICD10(service_date, code_min, code_max))
            else:
                icd10_collection.add(item)

        return icd10_collection
