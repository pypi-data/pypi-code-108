from __future__ import annotations
from typing import Union, Iterable
import os, re, functools
import datetime as dt

from dataUtils.DBClient import DBClient
from enginelib.claim_line_focus import ClaimLineFocus
from enginelib.errors import Error

_bad_chars = re.compile(r'[^0-9a-zA-z\-_]')
DB_CLIENT = DBClient.GetDBClient(os.getenv('APIKEY'))
DB_NAME = os.getenv('RIALTIC_REF_DB')


@functools.lru_cache()
def _sql_query(tx_id: str, proc_code: str) -> MFSResultsList:
    # noinspection SqlResolve,SqlNoDataSourceInspection,SqlDialectInspection
    query = f'''
        SELECT * FROM "{_sql_sanitize(DB_NAME)}".mfs 
        WHERE "HCPCS" = '{_sql_sanitize(proc_code)}'
    '''
    rows, error = DB_CLIENT.GetReferenceData(tx_id or "<no_tx_id>", query)
    if not error:
        return MFSResultsList(map(MFSResult, rows or ()), no_results=MFSNoResults.NoMatchingProcedure)
    raise Error(f"Unable to query the MFS set, error: {str(error)}")


def _filter_dates(start_date: dt.date, rows: MFSResultsList) -> MFSResultsList:
    return MFSResultsList(filter(lambda entry: entry.effective_start <= start_date
        < entry.effective_end, rows), no_results=MFSNoResults.NoMatchingDateRange)


def _date_read(string: str) -> dt.date:
    """Convert 'strings' in the `mfs` table to an actual date object."""
    return dt.datetime.strptime(string.strip().zfill(8), "%m%d%Y").date()


def _sql_sanitize(text: str) -> str:
    return _bad_chars.sub("", text)


class MFSQuery:
    """ MFSQuery(clue).first(filter_mods={}, restrict_dates=True).pctc_indicator"""
    def __init__(self, clue: ClaimLineFocus):
        self.clue = clue
        self.sql_rows = _sql_query(clue.request.transaction_id, clue.procedure_code)
        self.effective_rows = _filter_dates(clue.service_period.start, self.sql_rows)

    def first(self, filter_mods=None, restrict_dates=True) -> Union[MFSNoResults, MFSResult]:
        return self.rows(filter_mods, restrict_dates).first()

    def rows(self, filter_mods=None, restrict_dates=True) -> MFSResultsList:
        valid_rows = self.effective_rows if restrict_dates else self.sql_rows
        if filter_mods:
            valid_rows = MFSResultsList(filter(lambda x: x.listed_mod in filter_mods, valid_rows),
                no_results=MFSNoResults.NoMatchingMods)
        return valid_rows


class MFSResultsList(list):
    def __init__(self, rows: Iterable[MFSResult], no_results):
        self.no_results = no_results
        super().__init__(rows)

    def first(self) -> Union[MFSNoResults, MFSResult]:
        if not len(self):
            return self.no_results
        return self[0]


class LocalEnum(type):
    def __new__(mcs, _name, _bases, _dict):
        obj = super().__new__(mcs, _name, _bases, _dict)
        obj.__instances__ = []
        for Name, Value in _dict.items():
            if Name[0] != "_" and isinstance(Value, str):
                option = obj(Name, Value)
                setattr(obj, Name, option)
        return obj

    def __contains__(cls, item):
        return item in cls.__instances__


class MFSNoResults(metaclass=LocalEnum):
    def __init__(self, name, value):
        self.name, self.value = name, value
        self.__class__.__instances__.append(self)

    def __getattr__(self, item):
        return self

    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return f"<NoMFSResults.{self.name}, reason = {self.value}>"

    def __str__(self) -> str:
        return repr(self)

    NoMatchingField = "This field is not contained on the entry."
    NoMatchingProcedure = "No matching procedure code when querying the DB"
    NoMatchingDateRange = "No entry matching the required date range"
    NoMatchingMods = "No entry matching the required mods"


class MFSResult:
    def __init__(self, data):
        self.data = data

    def __getitem__(self, item):
        """ throws KeyError if a field is missing"""
        return self.data[item]

    def get(self, item, default=MFSNoResults.NoMatchingField):
        """ returns MFSNoResults.NoMatchingField if a field is missing"""
        return self.data.get(item, default)

    def float(self, name) -> Union[float, MFSNoResults]:
        """ get value as a float"""
        return _float(self.get(name))

    def string(self, name) -> Union[str, MFSNoResults]:
        """ get value as a stripped string"""
        return _str(self.get(name))

    @property
    def listed_mod(self) -> str:
        return self.string('MOD') or ''
    # rjdrn: I'd rather missing dates fail here than elsewhere
    @property
    def effective_start(self) -> dt.date:
       return _date_read(self['EFFECTIVESTARTDATE'])
    @property
    def effective_end(self) -> dt.date:
        return _date_read(self['EFFECTIVEENDDATE'])
    # rjdrn: IMO, nil values are best handled by individual engines
    @property
    def global_days(self) -> Union[str, MFSNoResults]:
        return self.string('GLOBDAYS')
    @property
    def pctc_indicator(self) -> Union[str, MFSNoResults]:
        return self.string('PCTCIND')
    @property
    def mult_proc(self) -> Union[str, MFSNoResults]:
        return self.string('MULTPROC')
    @property
    def status_code(self) -> Union[str, MFSNoResults]:
        return self.string('STATUSCODE')
    # facilities
    @property
    def facility_total(self) -> Union[float, MFSNoResults]:
        return self.float('FACILITYTOTAL')
    @property
    def non_facility_total(self) -> Union[float, MFSNoResults]:
        return self.float('NONFACILITYTOTAL')
    # surgery
    @property
    def asst_surgeons(self) -> Union[str, MFSNoResults]:
        return self.string('ASSTSURG')
    @property
    def co_surgeons(self) -> Union[str, MFSNoResults]:
        return self.string('COSURG')

def _convert(fn, text):
    return fn(text) if text else text

def _float(text):
    return _convert(float, text)

def _str(text):
    return _convert(lambda x: x.strip(), text)
