import logging
from collections import defaultdict
from typing import List, Dict, Set, Sequence, Union
from datetime import datetime
from packaging.version import parse, Version
import numpy as np
import ase
from ase.db import connect
from .version import __version__  # Avoid triggering other imports

logger = logging.getLogger(__name__)

# Global switch for emergency disabling checking of version checks
REQUIRE_COMPATIBLE_TABLE_VERISON = True


def toggle_require_compatible_table_version() -> None:
    """Toggle to disable/enable the "require_reconfigure_table" function."""
    global REQUIRE_COMPATIBLE_TABLE_VERISON  # pylint: disable=global-statement
    new = not REQUIRE_COMPATIBLE_TABLE_VERISON
    logger.info('Toggling global "REQUIRE_COMPATIBLE_TABLE_VERISON" from %s to %s.',
                REQUIRE_COMPATIBLE_TABLE_VERISON, new)
    REQUIRE_COMPATIBLE_TABLE_VERISON = new


class MetaTableKeys:
    """Container for keys in the meta table"""
    # Key where we store what version a database has been configured on
    CLEASE_CONFIGURE_VERSION = 'clease_config_version'
    # External table with clease table metadata
    CLEASE_META_TABLE = 'clease_metadata'
    TIME = 'time'
    ENCODE_DELIMITER = '__'  # Delimiter splitting encoding a table-name/table-key pair


class OutOfDateTable(Exception):
    """Exception for having an out-of-date table which requires an update/reconfigure"""


class InvalidMetaKey(Exception):
    """Exception when passing an invalid key in the metadata"""


# Type aliasing
_TABLE = Dict[str, Union[int, float, str, np.integer, np.floating]]  # Alias for a table
_ROW = ase.db.row.AtomsRow
_CONNECTION = ase.db.core.Database


def get_metadata(ase_connection: _CONNECTION, *ids) -> _TABLE:
    """Get a the metadata from a a database, without using the ASE API,
    as that causes loading of the entire database, which can be slow
    for larger databases. Therefore, we only extract what we need.
    If no metadata is present in the database, an empty dictionary is returned.

    Returns the decoded version of the meta data, i.e. a nested dictionary
    with metadata for each table.

    :param ase_connection: The ASE connection to the database.
    :param *ids: One or more ID's to get meta data for. Must be integers.
    """
    table_name = MetaTableKeys.CLEASE_META_TABLE
    # pylint: disable=protected-access
    if not ase_connection._external_table_exists(table_name):
        logger.debug('No metadata table was found')
        return {}
    sql = f"SELECT key,value,id FROM {table_name}"
    logger.info('Grabbing metadata with querry %s', sql)
    with ase_connection.managed_connection() as con:
        cur = con.cursor()
        cur.execute(sql)
        metadata = defaultdict(dict)
        for key, value, row_id in cur.fetchall():
            if row_id in ids:
                metadata[row_id].update({key: value})
    logger.debug('%s', metadata)
    return {k: decode_meta(v) for k, v in metadata.items()}


def require_reconfigure_table(ase_connection: _CONNECTION, table_name: str, *ids) -> bool:
    """Core function which checks the version the database was configured with.
    Returns a boolean indicating if the correlation functions of the
    database needs to be reconfigured, based on verison changes.

    The "REQUIRE_COMPATIBLE_TABLE_VERISON" global can be set to ``False`` to disable
    this functionality.

    :param ase_connection: The ASE connection to the database.
    :param table_name: ``str``, name of the table to check if
        it requires reconfiguration.
    :param *ids: One or more ID's to get meta data for. Must be integers.
    """

    if REQUIRE_COMPATIBLE_TABLE_VERISON is False:
        # Short circuit, for debugging/emergency situations
        return False

    if len(ids) == 0:
        raise ValueError("Must pass at least 1 id to test for reconfigure")

    metadata_many = get_metadata(ase_connection, *ids)
    for uid in ids:
        meta = metadata_many.get(uid, {})

        table = meta.get(table_name, {})

        value = table.get(MetaTableKeys.CLEASE_CONFIGURE_VERSION, None)
        if value is None:
            # Configured prior to 0.10.1
            # or not a CLEASE database
            return True
        vers = parse(value)
        if vers < Version('0.10.1'):
            # 0.10.1 introduced a change, requiring a reconfigure
            return True
    return False  # We're up-to-date


def _make_meta_for_table(**kwargs) -> _TABLE:
    """Update the metadata for a table. Preserves any other metadata placed into
    the table. If no table is given, a new one is created."""

    meta = {}
    now = datetime.now().strftime('%H:%M:%S %d-%m-%Y')  # Store a timestamp of the config
    version = str(__version__)
    meta.update({
        MetaTableKeys.TIME: now,
        MetaTableKeys.CLEASE_CONFIGURE_VERSION: version,
        **kwargs
    })
    return meta


def _check_key(key, delim=MetaTableKeys.ENCODE_DELIMITER) -> None:
    """Ensure that a key does not contain the delimiter used for encoding"""
    if delim in key:
        raise InvalidMetaKey(f'Encoding delimiter "{delim}" cannot be present in key, got: {key}')


def encode_meta_key(table_name, key, delim=MetaTableKeys.ENCODE_DELIMITER):
    """Encode a key for metadata, combining a table name with the key.

    E.g.
    >>> from clease.db_util import encode_meta_key
    >>> encode_meta_key('poly_cf', 'time')
    'poly_cf__time'

    :param table_name: String, name of the table
    :param key: String, the key to encode
    :param delim: Optional, what delimiter to use. Should usually not be changed.
        Defaults to '__'.
    """
    # Check the delimiter is not present in the keys
    for k in (table_name, key):
        _check_key(k, delim=delim)

    return delim.join((table_name, key))


def decode_meta_key(key, delim=MetaTableKeys.ENCODE_DELIMITER):
    """Decode a key which has been encoded using func:`encode_meta_key`.

    E.g.
    >>> from clease.db_util import decode_meta_key
    >>> decode_meta_key('poly_cf__time')
    ('poly_cf', 'time')

    :param key: String, key to decode.
    :param delim: Optional, what delimiter to use. Should usually not be changed.
        Defaults to '__'.
    """
    if delim not in key:
        raise InvalidMetaKey(f'Key "{key}" does not contain delimiter {delim}')
    table_name, table_key = key.split(delim)
    return table_name, table_key


def decode_meta(meta: dict) -> dict:
    """Decode an entire meta-data dictionary encoded using :func:`encode_meta`.

    The dictionary is returned in a nested format.
    """
    decoded = defaultdict(dict)
    for key, value in meta.items():
        table_name, table_key = decode_meta_key(key)
        decoded[table_name].update({table_key: value})
    return dict(decoded)


def encode_meta(meta: dict) -> dict:
    """Encodes a nested dictionary, such that it becomes a flat dictionary."""
    encoded = {}
    for table_name, table in meta.items():
        for key, value in table.items():
            encoded_key = encode_meta_key(table_name, key)
            encoded[encoded_key] = value
    return encoded


def make_meta_table(table_name: str, **kwargs) -> _TABLE:
    """Create a table with CLEASE meta data, such as the version the clease version
    the table was created with.

    Preserves any other metadata in the table, besides :func:`_make_meta_for_table`
    will update.
    """

    return {table_name: _make_meta_for_table(**kwargs)}


def new_row_with_many_tables(ase_connection: _CONNECTION, atoms, table_names: Sequence[str],
                             tables: Sequence[_TABLE], **kwargs) -> int:
    """Write a new row to a database with multiple external tables. Adds metadata for each table.

    Returns the ID of the new row in the database.

    :param ase_connection: An open ASE database connection
    :param atoms: The atoms object to write the row for
    :param table_names: Names of the tables to be added
    :param tables: Sequence of the tables. Order must be the same as ``table_names``
    :param kwargs: Any other key-value pair to be added to the row.
        See documentation for the `ASE database <https://wiki.fysik.dtu.dk/ase/ase/db/db.html>`_.
    """
    if not len(table_names) == len(tables):
        raise ValueError(
            (f'Number of table names should match number of tables. Got {len(table_names)} '
             f'table names, but {len(tables)} tables.'))

    metatable = {}
    for table_name in table_names:
        metatable.update(make_meta_table(table_name))

    tables = dict(zip(table_names, tables))
    tables.update({MetaTableKeys.CLEASE_META_TABLE: encode_meta(metatable)})
    uid = ase_connection.write(atoms, external_tables=tables, **kwargs)
    return uid


def new_row_with_single_table(ase_connection: _CONNECTION, atoms: ase.Atoms, table_name: str,
                              table: _TABLE, **kwargs) -> int:
    """Write a new row to a database with a single external table. Adds metadata to the table.

    See :func:`new_row_with_many_tables` for more details.
    """
    return new_row_with_many_tables(ase_connection, atoms, [table_name], [table], **kwargs)


def update_table(ase_connection: _CONNECTION, row_id: int, table_name: str, table: _TABLE) -> None:
    """Configure a row in an ASE database with an external table,
    and add a corresponding clease metadata table."""
    # Get the current row from the database connection,
    # as we need to know if it already contains metadata
    metatable = make_meta_table(table_name)
    meta = {MetaTableKeys.CLEASE_META_TABLE: encode_meta(metatable)}
    tables = dict(**{table_name: table}, **meta)
    logger.debug('Updating table "%s" for row id %d with keys: %s', table_name, row_id,
                 tables.keys())
    ase_connection.update(row_id, external_tables=tables)


def get_all_cf_names(db_name: str, tab_name: str) -> Set[str]:
    """
    Return a list with all correlation function names

    Parameters:

    db_name: Name of the database

    tab_name: Name of the table in the database where correlation functions
        are stores
    """
    with connect(db_name) as db:
        query = f"SELECT key FROM {tab_name}"
        cur = db.connection.cursor()
        db_names = set()
        cur.execute(query)
        for row in cur.fetchall():
            db_names.add(row[0])
    return db_names


def get_all_cf(db_name: str, tab_name: str, db_id: int) -> Dict[str, float]:
    """
    Return all correlation functions associated with an entry in the database

    Parameters:

    db_name: Name of the database

    tab_name: Name of the table where the correlation functions are stored

    db_id: ID of the entry
    """
    with connect(db_name) as db:
        query = f"SELECT key, value FROM {tab_name} WHERE id=?"
        cur = db.connection.cursor()
        cur.execute(query, (db_id,))
        cf = {}
        for row in cur.fetchall():
            cf_name, cf_value = row
            cf[cf_name] = cf_value
    return cf


def get_cf_tables(db_name: str) -> List[str]:
    """
    Return a list with table names that contain correlation functions

    Parameter:

    db_name: Name of the database
    """
    db = connect(db_name)
    ext_tab = db._get_external_table_names()  # pylint: disable=protected-access
    cf_tables = [n for n in ext_tab if n.endswith('_cf')]
    return cf_tables
