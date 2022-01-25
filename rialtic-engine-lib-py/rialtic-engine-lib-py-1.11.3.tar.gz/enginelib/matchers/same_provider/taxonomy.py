import os
from typing import Dict

from dataUtils.DBClient import DBClient

from enginelib.errors import Error


class RialticDataInterfaceError(Error):
    def __init__(self, message="there was a problem while fetching reference data"):
        super().__init__(f'Error: {message}')


class TaxonomyData:
    cache: Dict[str, str] = dict()

    @classmethod
    def query(cls, taxonomy_code: str) -> str:
        db_client = DBClient.GetDBClient(os.getenv("APIKEY"))

        query = f'''
            SELECT "medicare_specialty_code" 
            FROM demodb.ptxw_records 
            WHERE "provider_taxonomy_code"='{taxonomy_code}' 
            LIMIT 1'''

        ref_data, err = db_client.GetReferenceData("consultMedicareSpecialtyFromTaxCode", query)
        if err:
            raise RialticDataInterfaceError(message=str(err))

        try:
            record = ref_data.pop()
            return record['medicare_specialty_code']
        except AttributeError:
            pass
        return ''

    @staticmethod
    def mock_query(taxonomy_code: str) -> str:
        local_cache = {
            '207NI0002X': '07',
            '152WS0006X': '41'
        }

        return local_cache.get(taxonomy_code, '')

    @classmethod
    def is_taxonomy_code_valid(cls, taxonomy_code: str) -> bool:
        return bool(cls.medicare_specialty_code(taxonomy_code))

    @classmethod
    def medicare_specialty_code(cls, taxonomy_code: str) -> str:
        cache = cls.cache
        if taxonomy_code not in cache:
            cache[taxonomy_code] = cls.query(taxonomy_code)
            # Debugging (next two lines):
            # cache[taxonomy_code] = cls.mock_query(taxonomy_code)
            # print(f'(debugging) taxonomy.py:59 - {taxonomy_code} - {cache[taxonomy_code]};')
        return cache[taxonomy_code]
