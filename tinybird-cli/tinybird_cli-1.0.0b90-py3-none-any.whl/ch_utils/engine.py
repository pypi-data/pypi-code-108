import re
from collections import defaultdict

from ..sql import col_name, engine_replicated_to_local, parse_table_structure


class TableDetails:
    '''
    >>> ed = TableDetails({})
    >>> ed.engine_full == None
    True
    >>> ed.engine == None
    True
    >>> ed.to_json()
    {'engine_full': None, 'engine': None}
    >>> ed.to_datafile()
    ''

    >>> ed = TableDetails({ "engine_full": "MergeTree() PARTITION BY toYear(timestamp) ORDER BY (timestamp, cityHash64(location)) SAMPLE BY cityHash64(location) SETTINGS index_granularity = 32, index_granularity_bytes = 2048 TTL toDate(timestamp) + INTERVAL 1 DAY", "engine": "MergeTree", "partition_key": "toYear(timestamp)", "sorting_key": "timestamp, cityHash64(location)", "primary_key": "timestamp, cityHash64(location)", "sampling_key": "cityHash64(location)", "settings": "index_granularity = 32, index_granularity_bytes = 2048", "ttl": "toDate(timestamp) + INTERVAL 1 DAY" })
    >>> ed.engine_full
    'MergeTree() PARTITION BY toYear(timestamp) ORDER BY (timestamp, cityHash64(location)) SAMPLE BY cityHash64(location) SETTINGS index_granularity = 32, index_granularity_bytes = 2048 TTL toDate(timestamp) + INTERVAL 1 DAY'
    >>> ed.engine
    'MergeTree'
    >>> ed.to_json()
    {'engine_full': 'MergeTree() PARTITION BY toYear(timestamp) ORDER BY (timestamp, cityHash64(location)) SAMPLE BY cityHash64(location) SETTINGS index_granularity = 32, index_granularity_bytes = 2048 TTL toDate(timestamp) + INTERVAL 1 DAY', 'engine': 'MergeTree', 'partition_key': 'toYear(timestamp)', 'sorting_key': 'timestamp, cityHash64(location)', 'sampling_key': 'cityHash64(location)', 'settings': 'index_granularity = 32, index_granularity_bytes = 2048', 'ttl': 'toDate(timestamp) + INTERVAL 1 DAY'}
    >>> ed.to_datafile()
    'ENGINE "MergeTree"\\nENGINE_PARTITION_KEY "toYear(timestamp)"\\nENGINE_SORTING_KEY "timestamp, cityHash64(location)"\\nENGINE_SAMPLING_KEY "cityHash64(location)"\\nENGINE_SETTINGS "index_granularity = 32, index_granularity_bytes = 2048"\\nENGINE_TTL "toDate(timestamp) + INTERVAL 1 DAY"'

    >>> ed = TableDetails({"engine_full": "Join(ANY, LEFT, id)", "engine": "Join", "partition_key": "", "sorting_key": "", "primary_key": "", "sampling_key": ""})
    >>> ed.engine_full
    'Join(ANY, LEFT, id)'
    >>> ed.engine
    'Join'
    >>> ed.to_json()
    {'engine_full': 'Join(ANY, LEFT, id)', 'engine': 'Join', 'join_strictness': 'ANY', 'join_type': 'LEFT', 'key_columns': 'id'}
    >>> ed.to_datafile()
    'ENGINE "Join"\\nENGINE_JOIN_STRICTNESS "ANY"\\nENGINE_JOIN_TYPE "LEFT"\\nENGINE_KEY_COLUMNS "id"'

    >>> ed = TableDetails({"engine": "Join", "join_strictness": "ANY", "join_type": "LEFT", "key_columns": "id"})
    >>> ed.engine_full == None
    True
    >>> ed.engine
    'Join'
    >>> ed.to_json()
    {'engine_full': None, 'engine': 'Join', 'join_strictness': 'ANY', 'join_type': 'LEFT', 'key_columns': 'id'}
    >>> ed.to_datafile()
    'ENGINE "Join"\\nENGINE_JOIN_STRICTNESS "ANY"\\nENGINE_JOIN_TYPE "LEFT"\\nENGINE_KEY_COLUMNS "id"'
    '''
    def __init__(self, details):
        self.details = details or {}

    @property
    def engine_full(self):
        _engine_full = self.details.get('engine_full', None)
        if not _engine_full:
            return None
        _engine_full = _engine_full.replace(' SETTINGS index_granularity = 8192', '')
        return engine_replicated_to_local(_engine_full)

    @property
    def engine(self):
        _engine = self.details.get('engine', None)
        return _engine and _engine.replace('Replicated', '')

    @property
    def version(self):
        _version = self.details.get('version', None)
        return _version

    def is_mergetree_family(self):
        return self.engine and 'mergetree' in self.engine.lower()

    def supports_alter_add_column(self):
        return self.is_mergetree_family() or self.engine.lower() == "null"

    def is_replacing_engine(self):
        if self.engine:
            engine_lower = self.engine.lower()
            is_aggregating = 'aggregatingmergetree' in engine_lower
            is_replacing = 'replacingmergetree' in engine_lower
            is_collapsing = 'collapsingmergetree' in engine_lower
            return is_aggregating or is_replacing or is_collapsing
        return False

    @property
    def partition_key(self):
        return self.details.get('partition_key', None)

    @property
    def sorting_key(self):
        _sorting_key = self.details.get('sorting_key', None)
        if self.is_replacing_engine() and not _sorting_key:
            raise ValueError(f'SORTING_KEY must be defined for the {self.engine} engine')
        if self.is_mergetree_family():
            return _sorting_key or 'tuple()'
        return _sorting_key

    @property
    def primary_key(self):
        _primary_key = self.details.get('primary_key', None)
        if self.sorting_key == _primary_key:
            return None
        return _primary_key

    @property
    def sampling_key(self):
        return self.details.get('sampling_key', None)

    @property
    def settings(self):
        settings = self.details.get('settings', None)
        if settings and settings.strip().lower() != 'index_granularity = 8192':
            return settings

    @property
    def ttl(self):
        return self.details.get('ttl', None)

    @property
    def ver(self):
        _ver = self.details.get('ver', None)
        return _ver

    @property
    def columns(self):
        _columns = self.details.get('columns', None)
        return _columns

    @property
    def sign(self):
        _sign = self.details.get('sign', None)
        return _sign

    @property
    def join_strictness(self):
        _join_strictness = self.details.get('join_strictness', None)
        return _join_strictness

    @property
    def join_type(self):
        _join_type = self.details.get('join_type', None)
        return _join_type

    @property
    def key_columns(self):
        _key_columns = self.details.get('key_columns', None)
        return _key_columns

    @property
    def statistics(self):
        return {
            'bytes': self.details.get('total_bytes', None),
            'row_count': self.details.get('total_rows', None),
        }

    def to_json(self, exclude=None):
        d = {
            'engine_full': self.engine_full,
            'engine': self.engine,
        }
        if self.partition_key:
            d['partition_key'] = self.partition_key
        if self.sorting_key:
            d['sorting_key'] = self.sorting_key
        if self.primary_key:
            d['primary_key'] = self.primary_key
        if self.sampling_key:
            d['sampling_key'] = self.sampling_key
        if self.settings:
            d['settings'] = self.settings
        if self.ttl:
            d['ttl'] = self.ttl.strip()
        if self.join_strictness:
            d['join_strictness'] = self.join_strictness
        if self.join_type:
            d['join_type'] = self.join_type
        if self.key_columns:
            d['key_columns'] = self.key_columns
        if self.engine_full:
            engine_params = engine_params_from_engine_full(self.engine_full)
            d = {**d, **engine_params}

        if exclude:
            for attr in exclude:
                if attr in d:
                    del d[attr]

        return d

    def to_datafile(self):
        d = self.to_json()
        del d['engine_full']
        engine = d['engine']
        del d['engine']
        if engine:
            return '\n'.join([f'ENGINE "{engine}"'] + [f'ENGINE_{k.upper()} "{v}"' for k, v in d.items() if v])
        return ''


def engine_config(name, params=None, options=None):
    params = params or []
    options = options or []
    return (name, (params, options))


class EngineOption:
    def __init__(self, name=None, sql=None, required=None, default_value=None, is_valid=None):
        self.name = name
        self.sql = sql
        self.required = required
        self.default_value = default_value
        self.is_valid = is_valid


class EngineParam:
    def __init__(self, name=None, required=None, default_value=None, is_valid=None):
        self.name = name
        self.required = required
        self.default_value = default_value
        self.is_valid = is_valid


def column_is_valid(columns, column_name):
    schema_columns = [col_name(c['name'], backquotes=False) for c in columns]
    if column_name not in schema_columns:
        raise ValueError(f"'{column_name}' column is not present in schema")
    return col_name(column_name, backquotes=False)


def columns_are_valid(columns, column_names):
    schema_columns = [col_name(c['name'], backquotes=False) for c in columns]
    new_column_names = []
    for column_name in [x.strip() for x in column_names.split(',')]:
        if column_name not in schema_columns:
            raise ValueError(
                f"'{column_name}' column is not present in schema")
        new_column_names.append(col_name(column_name, backquotes=False))
    return ', '.join(new_column_names)


def sorting_key_is_valid(columns, value):
    INVALID_SORTING_KEYS = ['tuple()']

    if not value:
        raise ValueError("Sorting key can not be empty")
    if value in INVALID_SORTING_KEYS:
        raise ValueError(f"'{value}' is not a valid as a sorting key")
    return value


# [PARTITION BY expr]
# [ORDER BY expr]
# [PRIMARY KEY expr]
# [SAMPLE BY expr]
# [TTL expr [DELETE|TO DISK 'xxx'|TO VOLUME 'xxx'], ...]
# [SETTINGS name=value, ...]
MERGETREE_OPTIONS = [
    EngineOption(name='partition_key', sql='PARTITION BY'),
    EngineOption(name='sorting_key', sql='ORDER BY', default_value='tuple()'),
    EngineOption(name='primary_key', sql='PRIMARY KEY'),
    EngineOption(name='sampling_key', sql='SAMPLE BY'),
    EngineOption(name='ttl', sql='TTL'),
    EngineOption(name='settings', sql='SETTINGS'),
]
REPLACINGMERGETREE_OPTIONS = [
    EngineOption(name='partition_key', sql='PARTITION BY'),
    EngineOption(name='sorting_key', sql='ORDER BY', required=True, is_valid=sorting_key_is_valid),
    EngineOption(name='primary_key', sql='PRIMARY KEY'),
    EngineOption(name='sampling_key', sql='SAMPLE BY'),
    EngineOption(name='ttl', sql='TTL'),
    EngineOption(name='settings', sql='SETTINGS'),
]
ENABLED_ENGINES = [
    # MergeTree()
    engine_config('MergeTree', options=MERGETREE_OPTIONS),
    # ReplacingMergeTree([ver])
    engine_config('ReplacingMergeTree', [
        EngineParam(name='ver', is_valid=column_is_valid)
    ], REPLACINGMERGETREE_OPTIONS),
    # SummingMergeTree([columns])
    engine_config('SummingMergeTree', [
        # This should check the columns are numeric ones
        EngineParam(name='columns', is_valid=columns_are_valid),
    ], MERGETREE_OPTIONS),
    # AggregatingMergeTree()
    engine_config('AggregatingMergeTree', options=REPLACINGMERGETREE_OPTIONS),
    # CollapsingMergeTree(sign)
    engine_config('CollapsingMergeTree', [
        EngineParam(name='sign', required=True, is_valid=column_is_valid)
    ], REPLACINGMERGETREE_OPTIONS),
    # VersionedCollapsingMergeTree(sign, version)
    engine_config('VersionedCollapsingMergeTree', [
        EngineParam(name='sign', required=True, is_valid=column_is_valid),
        EngineParam(name='version', required=True, is_valid=column_is_valid),
    ], MERGETREE_OPTIONS),
    # Join(join_strictness, join_type, k1[, k2, ...])
    engine_config('Join', [
        # https://github.com/ClickHouse/ClickHouse/blob/fa8e4e4735b932f08b6beffcb2d069b72de34401/src/Storages/StorageJoin.cpp
        EngineParam(name='join_strictness', required=True,
                    is_valid=['ANY', 'ALL', 'SEMI', 'ANTI']),
        EngineParam(name='join_type', required=True, is_valid=[
                    'LEFT', 'INNER', 'RIGHT', 'FULL']),
        EngineParam(name='key_columns', required=True,
                    is_valid=columns_are_valid),
    ]),
    # Null()
    engine_config('Null'),
]


def get_engine_config(engine):
    for (name, config) in ENABLED_ENGINES:
        if engine.lower() == name.lower():
            return (name, config)
    return None


def engine_params(columns, params, args):
    params_values = []
    for p in params:
        if p.required and p.name not in args:
            raise ValueError(f"Missing required parameter '{p.name}'")
        param_value = args.get(p.name, None) or p.default_value
        if not param_value:
            continue
        if p.is_valid:
            check_is_valid(
                valid_check=p.is_valid,
                check_type='parameter',
                columns=columns,
                name=p.name,
                value=param_value)
        params_values.append(param_value)
    return params_values


def engine_options(columns, options, args):
    options_values = []
    for o in options:
        if o.required and o.name not in args:
            raise ValueError(f"Missing required option '{o.name}'")
        option_value = args.get(o.name) or o.default_value
        if o.is_valid:
            check_is_valid(
                valid_check=o.is_valid,
                check_type='option',
                columns=columns,
                name=o.name,
                value=option_value)
        if option_value:
            if o.sql.lower() == 'settings':
                options_values.append(f"{o.sql} {option_value}")
            else:
                options_values.append(f"{o.sql} ({option_value})")
    return options_values


def check_is_valid(valid_check, check_type, columns, name, value):
    if callable(valid_check):
        try:
            new_value = valid_check(columns, value)
            if new_value:
                value = new_value
        except Exception as e:
            raise ValueError(f"Invalid value '{value}' for {check_type} '{name}', reason: {e}")
    else:
        if value not in valid_check:
            raise ValueError(f"Invalid value '{value}' for {check_type} '{name}', valid values are: {', '.join(valid_check)}")


def build_engine(engine, columns, params, options, args):
    return f"{engine}({', '.join(engine_params(columns, params, args))}) {' '.join(engine_options(columns, options, args))}".strip()


def engine_full_from_dict(engine: str, args: dict, schema: str = None, columns: list = None):
    """
    >>> schema = ''
    >>> engine_full_from_dict('wadus', {}, schema=schema)
    Traceback (most recent call last):
    ...
    ValueError: Engine wadus is not supported, supported engines include: MergeTree, ReplacingMergeTree, SummingMergeTree, AggregatingMergeTree, CollapsingMergeTree, VersionedCollapsingMergeTree, Join, Null

    >>> schema = ''
    >>> engine_full_from_dict('null', {}, schema=schema)
    'Null()'
    >>> schema = ''
    >>> engine_full_from_dict('null', {}, columns=[])
    'Null()'

    >>> schema = 'cid Int32'
    >>> engine_full_from_dict('Join', {'join_strictness': 'ANY', 'join_type': 'LEFT', 'key_columns': 'cid'}, schema=schema)
    'Join(ANY, LEFT, cid)'
    >>> engine_full_from_dict('Join', {'join_strictness': 'ANY', 'join_type': 'LEFT', 'key_columns': 'cid'}, columns=[{'name': 'cid', 'type': 'Int32', 'codec': None, 'default_value': None, 'nullable': False, 'normalized_name': 'cid'}])
    'Join(ANY, LEFT, cid)'
    >>> schema = 'cid1 Int32, cid2 Int8'
    >>> engine_full_from_dict('Join', {'join_strictness': 'ANY', 'join_type': 'LEFT', 'key_columns': 'cid1, cid2'}, schema=schema)
    'Join(ANY, LEFT, cid1, cid2)'
    >>> engine_full_from_dict('Join', {'join_strictness': 'ANY', 'join_type': 'OUTER', 'key_columns': 'cid'}, schema=schema)
    Traceback (most recent call last):
    ...
    ValueError: Invalid value 'OUTER' for parameter 'join_type', valid values are: LEFT, INNER, RIGHT, FULL

    >>> schema = ''
    >>> engine_full_from_dict('MergeTree', {}, schema=schema)
    'MergeTree() ORDER BY (tuple())'
    >>> engine_full_from_dict('MergeTree', {'sorting_key': 'local_date, cod_store'}, schema=schema)
    'MergeTree() ORDER BY (local_date, cod_store)'
    >>> engine_full_from_dict('MergeTree', {'partition_key': 'toDate(timestamp)', 'sorting_key': 'local_date, cod_store', 'settings': 'index_granularity = 32, index_granularity_bytes = 2048', 'ttl': 'toDate(local_date) + INTERVAL 1 DAY'}, schema=schema)
    'MergeTree() PARTITION BY (toDate(timestamp)) ORDER BY (local_date, cod_store) TTL (toDate(local_date) + INTERVAL 1 DAY) SETTINGS index_granularity = 32, index_granularity_bytes = 2048'

    >>> schema = ''
    >>> engine_full_from_dict('CollapsingMergeTree', {'sign': 'sign_column'}, schema=schema)
    Traceback (most recent call last):
    ...
    ValueError: Invalid value 'sign_column' for parameter 'sign', reason: 'sign_column' column is not present in schema

    >>> schema = 'sign_column Int8'
    >>> engine_full_from_dict('CollapsingMergeTree', {'sign': 'sign_column'}, schema=schema)
    Traceback (most recent call last):
    ...
    ValueError: Missing required option 'sorting_key'

    >>> schema = 'sign_column Int8, key_column Int8'
    >>> engine_full_from_dict('CollapsingMergeTree', {'sign': 'sign_column', 'sorting_key': 'key_column'}, schema=schema)
    'CollapsingMergeTree(sign_column) ORDER BY (key_column)'

    >>> columns=[]
    >>> columns.append({'name': 'sign_column', 'type': 'Int8', 'codec': None, 'default_value': None, 'nullable': False, 'normalized_name': 'sign_column'})
    >>> columns.append({'name': 'key_column', 'type': 'Int8', 'codec': None, 'default_value': None, 'nullable': False, 'normalized_name': 'key_column'})
    >>> engine_full_from_dict('CollapsingMergeTree', {'sign': 'sign_column', 'sorting_key': 'key_column' }, columns=columns)
    'CollapsingMergeTree(sign_column) ORDER BY (key_column)'

    >>> schema = 'sign_column Int8'
    >>> engine_full_from_dict('AggregatingMergeTree', {}, schema=schema)
    Traceback (most recent call last):
    ...
    ValueError: Missing required option 'sorting_key'

    >>> columns=[]
    >>> columns.append({'name': 'key_column', 'type': 'Int8', 'codec': None, 'default_value': None, 'nullable': False, 'normalized_name': 'key_column'})
    >>> engine_full_from_dict('AggregatingMergeTree', { 'sorting_key': 'key_column' }, columns=columns)
    'AggregatingMergeTree() ORDER BY (key_column)'

    >>> schema = 'ver_column Int8, key_column Int8'
    >>> engine_full_from_dict('ReplacingMergeTree', {}, schema=schema)
    Traceback (most recent call last):
    ...
    ValueError: Missing required option 'sorting_key'

    >>> engine_full_from_dict('ReplacingMergeTree', {'sorting_key': 'key_column'}, schema=schema)
    'ReplacingMergeTree() ORDER BY (key_column)'

    >>> engine_full_from_dict('ReplacingMergeTree', {'ver': 'ver_column', 'sorting_key': 'key_column'}, schema=schema)
    'ReplacingMergeTree(ver_column) ORDER BY (key_column)'

    >>> engine_full_from_dict('ReplacingMergeTree', {'ver': 'other_column'}, schema=schema)
    Traceback (most recent call last):
    ...
    ValueError: Invalid value 'other_column' for parameter 'ver', reason: 'other_column' column is not present in schema

    >>> schema = 'col0 Int8, col1 Int8, col2 Int8'
    >>> engine_full_from_dict('SummingMergeTree', {}, schema=schema)
    'SummingMergeTree() ORDER BY (tuple())'
    >>> engine_full_from_dict('SummingMergeTree', {'columns': 'col0'}, schema=schema)
    'SummingMergeTree(col0) ORDER BY (tuple())'
    >>> engine_full_from_dict('SummingMergeTree', {'columns': 'col0, col2'}, schema=schema)
    'SummingMergeTree(col0, col2) ORDER BY (tuple())'
    >>> engine_full_from_dict('SummingMergeTree', {'columns': 'col1, other_column'}, schema=schema)
    Traceback (most recent call last):
    ...
    ValueError: Invalid value 'col1, other_column' for parameter 'columns', reason: 'other_column' column is not present in schema
    >>> engine_full_from_dict('SummingMergeTree', {'columns': 'col1, other_column'}, schema=schema, columns=[])
    Traceback (most recent call last):
    ...
    ValueError: You can not use 'schema' and 'columns' at the same time
    """
    if schema is not None and columns is not None:
        raise ValueError("You can not use 'schema' and 'columns' at the same time")
    engine_config = get_engine_config(engine)

    if not engine_config:
        raise ValueError(
            f"Engine {engine} is not supported, supported engines include: {', '.join([e[0] for e in ENABLED_ENGINES])}")
    name, (params, options) = engine_config
    if columns is None:
        columns = parse_table_structure(schema)

    for arg in args:
        if not hasattr(TableDetails, arg):
            raise ValueError(f"engine_{arg} is not a valid option")

    return build_engine(name, columns, params, options, args)


def engine_params_from_engine_full(engine_full: str):
    """
    >>> engine_params_from_engine_full("Null()")
    {}
    >>> engine_params_from_engine_full("Join(ANY, LEFT, id)")
    {'join_strictness': 'ANY', 'join_type': 'LEFT', 'key_columns': 'id'}
    >>> engine_params_from_engine_full("Join(ANY, LEFT, k1, k2)")
    {'join_strictness': 'ANY', 'join_type': 'LEFT', 'key_columns': 'k1, k2'}
    >>> engine_params_from_engine_full("AggregatingMergeTree('/clickhouse/tables/{layer}-{shard}/d_f837aa.sales_by_country_rt__v0_staging_t_00c3091e7530472caebda05e97288a1d', '{replica}') PARTITION BY toYYYYMM(date) ORDER BY (purchase_location, cod_device, date) SETTINGS index_granularity = 8192")
    {}
    >>> engine_params_from_engine_full("ReplicatedSummingMergeTree('/clickhouse/tables/{layer}-{shard}/d_abcf3e.t_69f9da31f4524995b8911e1b24c80ab4', '{replica}') PARTITION BY toYYYYMM(date) ORDER BY (date, purchase_location, sku_rank_lc) SETTINGS index_granularity = 8192")
    {}
    >>> engine_params_from_engine_full("ReplicatedSummingMergeTree('/clickhouse/tables/{layer}-{shard}/d_abcf3e.t_69f9da31f4524995b8911e1b24c80ab4', '{replica}', c1, c2) PARTITION BY toYYYYMM(date) ORDER BY (date, purchase_location, sku_rank_lc) SETTINGS index_granularity = 8192")
    {'columns': 'c1, c2'}
    >>> engine_params_from_engine_full("ReplacingMergeTree(insert_date) ORDER BY date")
    {'ver': 'insert_date'}
    >>> engine_params_from_engine_full("ReplicatedReplacingMergeTree('/clickhouse/tables/{layer}-{shard}/d_f837aa.t_d3aaad001dee4d9e9e3067ccb789fb59_n1', '{replica}', insert_date) ORDER BY pk TTL toDate(local_timeplaced) + toIntervalDay(3) SETTINGS index_granularity = 8192")
    {'ver': 'insert_date'}
    >>> engine_params_from_engine_full("ReplicatedVersionedCollapsingMergeTree('/clickhouse/tables/{layer}-{shard}/test.foo', '{replica}', sign_c,version_c) ORDER BY pk TTL toDate(local_timeplaced) + toIntervalDay(3) SETTINGS index_granularity = 8192")
    {'sign': 'sign_c', 'version': 'version_c'}
    """
    engine_full = engine_replicated_to_local(engine_full)
    for engine, (params, _options) in ENABLED_ENGINES:
        if engine_full.startswith(engine):
            m = re.search(rf'{engine}\(([^\)]*)\).*', engine_full)
            params_used = []
            if m:
                params_used = [x.strip() for x in m.group(1).split(',')]
            params_dict = defaultdict(list)
            param = None
            for i, v in enumerate(params_used):
                if i < len(params):
                    param = params[i]
                if param and v:
                    params_dict[param.name].append(v)

            return {k: ', '.join(v) for k, v in params_dict.items()}
    return {}
