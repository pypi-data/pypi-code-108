import datetime as dt
import functools
import re
from typing import List, Dict, Any

from enginelib.claim_line_focus import ClaimLineFocus
from enginelib.errors import Error
from enginelib.rds.client import db_client, db_name


def execute(transaction_id: str, query: str) -> List[Dict[str, Any]]:
    records, error = db_client.GetReferenceData(transaction_id or "missing", query)
    if error:
        raise Error(f'Not able to access MFS reference data set.')

    return records or list()


_bad_chars = re.compile(r'[^0-9a-zA-z\-_]')
def _sql_sanitize(text: str) -> str:
    return _bad_chars.sub("", text)


@functools.lru_cache()
def mfs_records_for(transaction_id: str, procedure_code: str) -> List[Dict[str, Any]]:
    # noinspection SqlResolve,SqlNoDataSourceInspection,SqlDialectInspection
    query = f'''
        SELECT * FROM "{_sql_sanitize(db_name)}".mfs 
        WHERE "HCPCS" = '{_sql_sanitize(procedure_code)}'
    '''

    return execute(transaction_id, query)


def mfs_relevant_mod(mod_list: List[str]) -> str:
    """When querying the Medicare Physician Fee Schedule (table `mfs`)
    we need to see if one of these modifiers is present to correctly
    get the desired row.

    Content team: these modifiers should never come together in a claim.
    """
    relevant_mod_list = ['53', '26', 'TC']
    for mod in relevant_mod_list:
        if mod in mod_list:
            return mod
    return ''


@functools.lru_cache()
def date_from(string: str) -> dt.date:
    """Convert strings in the `mfs` table to an actual date object."""
    return dt.datetime.strptime(string.zfill(8), "%m%d%Y").date()


def mfs_field_for(field: str, clf: ClaimLineFocus) -> Any:
    """Given the column name in table `mfs` (the Medicare Physician Fee Schedule) in
    the variable `fields`, and given the claim line in variable `clf`, this function
    finds the relevant row in the `mfs` table -- taking into account the service date
    and the modifiers (relevant modifiers are '53', '26' and 'TC') -- and returns the
    value in the desired field for the applicable row that was found."""
    records = mfs_records_for(clf.request.transaction_id, clf.procedure_code)
    mod = mfs_relevant_mod(clf.modifier_codes)
    from_date = clf.service_period.start

    effective_records: List[Dict[str, str]] = list()
    for record in records:
        effective_start = date_from(record['EFFECTIVESTARTDATE'].strip())
        effective_end = date_from(record['EFFECTIVEENDDATE'].strip())
        if effective_start <= from_date < effective_end:
            effective_records.append(record)

    if not effective_records:
        raise Error(f'The date of service in the claim line ({from_date}) does not match any '
                    f'effective period in the MFS reference data set for procedure code '
                    f'{clf.procedure_code}. Unable to determine the value of {field} for '
                    f'this claim line.')

    for record in effective_records:
        record_mod = record['MOD'] or ''
        if record_mod == mod:
            return record[field]

    # If there was no modifier-specific row, use the one with empty MOD.
    for record in effective_records:
        if not record['MOD']:
            # None or empty string will do!
            return record[field]

    required_modifiers = {record["MOD"] for record in effective_records}
    raise Error(f'For the date of service in the claim line ({from_date}), the MFS reference data '
                f'set only contains rows for procedure code {clf.procedure_code} when one of the '
                f'following modifiers is present: {required_modifiers}.')


def global_days(clf: ClaimLineFocus) -> str:
    return str(mfs_field_for('GLOBDAYS', clf)).strip()


def pctc_indicator(clf: ClaimLineFocus) -> str:
    return str(mfs_field_for('PCTCIND', clf)).strip()


def facility_total(clf: ClaimLineFocus) -> float:
    try:
        return float(mfs_field_for('FACILITYTOTAL', clf))
    except ValueError:
        raise Error(f'Value in column "FACILITYTOTAL" for procedure code {clf.procedure_code}, is not a number.')


def non_facility_total(clf: ClaimLineFocus) -> float:
    try:
        return float(mfs_field_for('NONFACILITYTOTAL', clf))
    except ValueError:
        raise Error(f'Value in column "NONFACILITYTOTAL" for procedure code {clf.procedure_code}, is not a number.')


def mult_proc(clf: ClaimLineFocus) -> str:
    return str(mfs_field_for('MULTPROC', clf)).strip()


def status_code(clf: ClaimLineFocus) -> str:
    return str(mfs_field_for('STATUSCODE', clf)).strip().upper()
