"""
Datafile is like a Dockerfile but to describe ETL processes
"""

import asyncio
import shlex
import sys
import re
import click
import glob
import pprint
import requests
import unittest
from string import Template
from toposort import toposort
from pathlib import Path
import urllib.parse
from urllib.parse import urlencode, urlparse, parse_qs
from collections import namedtuple
from io import StringIO
import os.path
from copy import deepcopy
import traceback

from .sql import parse_table_structure, schema_to_sql_columns
from .client import TinyB, DoesNotExistException
from .sql_template import render_sql_template, get_used_tables_in_template
from .feedback_manager import FeedbackManager
from .ch_utils.engine import ENABLED_ENGINES
from tinybird.syncasync import sync_to_async

INTERNAL_TABLES = ('datasources_ops_log', 'snapshot_views', 'pipe_stats', 'pipe_stats_rt', 'block_log',
                   'data_connectors_log', 'kafka_ops_log')

requests_get = sync_to_async(requests.get, thread_sensitive=False)
requests_post = sync_to_async(requests.post, thread_sensitive=False)
requests_put = sync_to_async(requests.put, thread_sensitive=False)
requests_delete = sync_to_async(requests.delete, thread_sensitive=False)

pp = pprint.PrettyPrinter()


class ParseException(Exception):
    def __init__(self, err, lineno=-1):
        self.lineno = lineno
        super().__init__(err)


class ValidationException(Exception):
    def __init__(self, err, lineno=-1):
        self.lineno = lineno
        super().__init__(err)


def sizeof_fmt(num, suffix='b'):
    """Readable file size
    :param num: Bytes value
    :type num: int
    :param suffix: Unit suffix (optionnal) default = o
    :type suffix: str
    :rtype: str
    """
    for unit in ['', 'k', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def is_shared_datasource(ds_name):
    """just looking for a dot in the name is fine, dot are not allowed in regular datasources"""
    return '.' in ds_name


class Datafile:

    def __init__(self):
        self.maintainer = None
        self.sources = []
        self.nodes = []
        self.tokens = []
        self.keys = []
        self.version = None
        self.description = None

    def validate(self):
        for x in self.nodes:
            if not x['name'].strip():
                raise ValidationException("invalid node name, can't be empty")
            if 'sql' not in x:
                raise ValidationException(
                    "node %s must have a SQL query" % x['name'])
        if self.version is not None and (not isinstance(self.version, int) or self.version < 0):
            raise ValidationException("version must be a positive integer")

    def is_equal(self, other):
        if len(self.nodes) != len(other.nodes):
            return False

        for i, _ in enumerate(self.nodes):
            if self.nodes[i] != other.nodes[i]:
                return False

        return True


def parse_datasource(filename):
    with open(filename) as file:
        s = file.read()
    basepath = os.path.dirname(filename)

    try:
        doc = parse(s, 'default', basepath)
    except ParseException as e:
        raise click.ClickException(FeedbackManager.error_parsing_file(filename=filename, lineno=e.lineno, error=e)) from None

    if len(doc.nodes) > 1:
        raise ValueError(f"{filename}: datasources can't have more than one node")

    return doc


def parse_pipe(filename):
    with open(filename) as file:
        s = file.read()
    basepath = os.path.dirname(filename)

    try:
        doc = parse(s, basepath=basepath)
    except ParseException as e:
        raise click.ClickException(FeedbackManager.error_parsing_file(filename=filename, lineno=e.lineno, error=e))

    return doc


def parse(s, default_node=None, basepath='.'):  # noqa: C901
    """
    Parses `s` string into a document
    >>> d = parse("FROM SCRATCH\\nSOURCE 'https://test.com'\\n#this is a comment\\nMAINTAINER 'rambo' #this is me\\nNODE \\"test_01\\"\\n    DESCRIPTION this is a node that does whatever\\nSQL >\\n\\n        SELECT * from test_00\\n\\n\\nNODE \\"test_02\\"\\n    DESCRIPTION this is a node that does whatever\\nSQL >\\n\\n    SELECT * from test_01\\n    WHERE a > 1\\n   GROUP by a\\n")
    >>> d.maintainer
    'rambo'
    >>> d.sources
    ['https://test.com']
    >>> len(d.nodes)
    2
    >>> d.nodes[0]
    {'name': 'test_01', 'description': 'this is a node that does whatever', 'sql': 'SELECT * from test_00'}
    >>> d.nodes[1]
    {'name': 'test_02', 'description': 'this is a node that does whatever', 'sql': 'SELECT * from test_01\\n    WHERE a > 1\\n   GROUP by a'}
    """
    lines = list(StringIO(s, newline=None))

    doc = Datafile()

    parser_state = namedtuple(
        'ParserState',
        ['multiline', 'current_node', 'command', 'multiline_string'])

    parser_state.multiline = False
    parser_state.current_node = False

    def _unquote(x):
        QUOTES = ('"', "'")
        if x[0] in QUOTES and x[-1] in QUOTES:
            x = x[1:-1]
        return x

    def assign(attr):
        def _fn(x, **kwargs):
            setattr(doc, attr, _unquote(x))
        return _fn

    def schema(*args, **kwargs):
        s = _unquote(''.join(args))
        try:
            sh = parse_table_structure(s)
        except Exception as e:
            raise ParseException(FeedbackManager.error_parsing_schema(line=kwargs['lineno'], error=e))
        parser_state.current_node['schema'] = ','.join(
            schema_to_sql_columns(sh))
        parser_state.current_node['columns'] = sh

    def eval_var(s):
        # replace ENV variables
        # it's probably a bad idea to allow to get any env var
        return Template(s).safe_substitute(os.environ)

    def assign_var(v):
        def _f(*args, **kwargs):
            s = _unquote((' '.join(args)).strip())
            parser_state.current_node[v.lower()] = eval_var(s)
        return _f

    def sources(x, **kwargs):
        doc.sources.append(_unquote(x))

    def node(*args, **kwargs):
        node = {
            'name': eval_var(_unquote(args[0]))
        }
        doc.nodes.append(node)
        parser_state.current_node = node

    def description(*args, **kwargs):
        description = (' '.join(args)).strip()

        if parser_state.current_node:
            parser_state.current_node['description'] = description
        else:
            doc.description = description

    def sql(sql, **kwargs):
        if not parser_state.current_node:
            raise ParseException("SQL must be called after a NODE command")
        parser_state.current_node['sql'] = sql.strip()

    def assign_node_var(v):
        def _f(*args, **kwargs):
            if not parser_state.current_node:
                raise ParseException("%s must be called after a NODE command" % v)
            return assign_var(v)(*args, **kwargs)
        return _f

    def add_token(*args, **kwargs):  # token_name, permissions):
        if len(args) < 2:
            raise ParseException('TOKEN gets two params, token name and permissions e.g TOKEN "read api token" READ')
        doc.tokens.append({
            'token_name': _unquote(args[0]),
            'permissions': args[1]
        })

    def add_key(*args, **kwargs):  # token_name, permissions):
        if len(args) < 1:
            raise ParseException('KEY gets one params')
        doc.keys.append({
            'column': _unquote(args[0])
        })

    def test(*args, **kwargs):
        print("test", args, kwargs)

    def include(*args, **kwargs):
        f = _unquote(args[0])
        f = eval_var(f)
        attrs = dict(_unquote(x).split('=', 1) for x in args[1:])
        nonlocal lines
        lineno = kwargs['lineno']
        # be sure to replace the include line
        p = Path(basepath)
        with open(p / f) as file:
            lines[lineno:lineno + 1] = [''] + list(StringIO(Template(file.read()).safe_substitute(attrs), newline=None))

    def version(*args, **kwargs):
        if len(args) < 1:
            raise ParseException('VERSION gets one positive integer param')
        try:
            version = int(args[0])
            if version < 0:
                raise ValidationException('version must be a positive integer e.g VERSION 2')
            doc.version = version
        except ValueError:
            raise ValidationException('version must be a positive integer e.g VERSION 2')

    def __init_engine(v):
        if not parser_state.current_node:
            raise Exception(f"{v} must be called after a NODE command")
        if 'engine' not in parser_state.current_node:
            parser_state.current_node['engine'] = {'type': None, 'args': []}

    def set_engine(*args, **kwargs):
        __init_engine('ENGINE')
        engine_type = _unquote((' '.join(args)).strip())
        parser_state.current_node['engine']['type'] = engine_type

    def add_engine_var(v):
        def _f(*args, **kwargs):
            __init_engine(f"ENGINE_{v}".upper())
            engine_arg = _unquote((' '.join(args)).strip())
            parser_state.current_node['engine']['args'].append((v, engine_arg))
        return _f

    cmds = {
        'from': assign('from'),
        'source': sources,
        'maintainer': assign('maintainer'),
        'schema': schema,
        'engine_full': assign_var('engine_full'),
        'engine': set_engine,
        'partition_key': assign_var('partition_key'),
        'sorting_key': assign_var('sorting_key'),
        'primary_key': assign_var('primary_key'),
        'sampling_key': assign_var('sampling_key'),
        'ttl': assign_var('ttl'),
        'settings': assign_var('settings'),
        'node': node,
        'description': description,
        'type': assign_node_var('type'),
        'datasource': assign_node_var('datasource'),
        'tags': assign_node_var('tags'),
        'token': add_token,
        'key': add_key,
        'test': test,
        'include': include,
        'sql': sql,
        'version': version,
        'kafka_connection_name': assign_var('kafka_connection_name'),
        'kafka_topic': assign_var('kafka_topic'),
        'kafka_group_id': assign_var('kafka_group_id'),
        'kafka_bootstrap_servers': assign_var('kafka_bootstrap_servers'),
        'kafka_key': assign_var('kafka_key'),
        'kafka_secret': assign_var('kafka_secret'),
        'kafka_schema_registry_url': assign_var('kafka_schema_registry_url'),
        'kafka_target_partitions': assign_var('kafka_target_partitions'),
        'kafka_auto_offset_reset': assign_var('kafka_auto_offset_reset'),
        'kafka_store_raw_value': assign_var('kafka_store_raw_value')
    }

    engine_vars = set()

    for _engine, (params, options) in ENABLED_ENGINES:
        for p in params:
            engine_vars.add(p.name)
        for o in options:
            engine_vars.add(o.name)
    for v in engine_vars:
        cmds[f"engine_{v}"] = add_engine_var(v)

    if default_node:
        node(default_node)

    lineno = 0
    try:
        while lineno < len(lines):
            line = lines[lineno]
            try:
                sa = shlex.shlex(line)
                sa.whitespace_split = True
                lexer = list(sa)
            except ValueError:
                sa = shlex.shlex(shlex.quote(line))
                sa.whitespace_split = True
                lexer = list(sa)
            if lexer:
                cmd, args = lexer[0], lexer[1:]

                if parser_state.multiline and cmd.lower() in cmds and not (line.startswith(' ') or line.startswith('\t') or line.lower().startswith('from')):
                    parser_state.multiline = False
                    cmds[parser_state.command](parser_state.multiline_string, lineno=lineno)

                if not parser_state.multiline:
                    if len(args) >= 1 and args[0] == ">":
                        parser_state.multiline = True
                        parser_state.command = cmd.lower()
                        parser_state.multiline_string = ''
                    else:
                        if cmd.lower() in cmds:
                            cmds[cmd.lower()](*args, lineno=lineno)
                        else:
                            raise click.ClickException(FeedbackManager.error_option(option=cmd.upper()))
                else:
                    parser_state.multiline_string += line
            lineno += 1
        # close final state
        if parser_state.multiline:
            cmds[parser_state.command](parser_state.multiline_string, lineno=lineno)
    except ParseException as e:
        raise ParseException(str(e), lineno=lineno)
    except ValidationException as e:
        raise ValidationException(str(e), lineno=lineno)
    except IndexError as e:
        raise ValidationException(f'Validation error, found {line} in line {str(lineno)}: {str(e)}', lineno=lineno)
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        raise ParseException(f"Unexpected error: {e}", lineno=lineno)

    return doc


def generate_resource_for_key(key, name, schema, version, res_name):
    resources = []
    # datasource
    ds_name = f"{name}_join_by_{key}{version}"
    params = {
        "name": ds_name,
        "schema": schema,
        "__engine_full": f"Join(ANY, LEFT, {key})"
    }
    resources.append({
        'resource_name': f'{name}_join_by_{key}',
        'resource': 'datasources',
        'params': params,
        'filename': f"{params['name']}.datasource"
    })
    resources.append({
        'resource_name': f'{name}_join_by_{key}_pipe',
        'resource': 'pipes',
        'filename': f"{params['name']}.pipe",
        "name": f"{name}_join_by_{key}_pipe{version}",
        "schema": schema,
        'nodes': [{
            'sql': f"select * from {name}{version}",
            'params': {
                "name": f"{name}_join_by_{key}_view",
                'type': 'materialized',
                'datasource': ds_name
            }
        }],
        'deps': [res_name],  # [ds_name],
        'tokens': []
    })
    return resources


async def process_file(filename, tb_client, dir_path, tag='', resource_versions=None, verbose=False, skip_connectors=False, workspace_map={}, workspace_lib_paths=None):  # noqa: C901 B006

    if resource_versions is None:
        resource_versions = {}
    resource_versions_string = {k: f'__v{v}' for k, v in resource_versions.items() if v >= 0}

    def get_engine_params(node):
        params = {}
        if 'engine_full' in node and 'engine' in node:
            raise ValueError('You can not use ENGINE and ENGINE_FULL in the same node')

        if 'engine_full' in node:
            if verbose:
                click.echo(FeedbackManager.warning_deprecated(warning=f"The 'ENGINE_FULL' keyword is deprecated, found at node '{node.get('name', 'unknown')}', you must use 'ENGINE' instead. 'ENGINE_FULL' will stop working after 2021-03-31."))
            params["__engine_full"] = node['engine_full']

        if 'engine' in node:
            deprecated_vars = ('partition_key', 'sorting_key', 'primary_key', 'sampling_key', 'ttl', 'settings')
            for v in deprecated_vars:
                dep_value = node.get(v, None)
                if dep_value is not None:
                    node['engine']['args'].append((v, dep_value))
                    if verbose:
                        click.echo(FeedbackManager.warning_deprecated_command(keyword=v.upper(), node=node.get('name', 'unknown'), deadline='2021-03-31'))
            engine = node['engine']['type']
            params['engine'] = engine
            args = node['engine']['args']
            for (k, v) in args:
                params[f'engine_{k}'] = v
        return params

    async def get_kafka_params(node):
        params = {
            key: value
            for key, value in node.items() if key.startswith('kafka')
        }

        if not skip_connectors:
            try:
                connector_params = {
                    'kafka_bootstrap_servers': params.get('kafka_bootstrap_servers', None),
                    'kafka_key': params.get('kafka_key', None),
                    'kafka_secret': params.get('kafka_secret', None),
                    'kafka_connection_name': params.get('kafka_connection_name', None),
                    'kafka_auto_offset_reset': params.get('kafka_auto_offset_reset', None),
                    'kafka_schema_registry_url': params.get('kafka_schema_registry_url', None)
                }
                connector = await tb_client.get_connection(**connector_params)

                if not connector:
                    click.echo(FeedbackManager.success_connection_creating(connection_name=params['kafka_connection_name']))
                    connector = await tb_client.connection_create_kafka(**connector_params)
            except Exception as e:
                raise click.ClickException(
                    FeedbackManager.error_connection_create(connection_name=params['kafka_connection_name'], error=str(e)))

            click.echo(FeedbackManager.success_connection_using(connection_name=connector['name']))

            params.update({
                'connector': connector['id'],
                'service': 'kafka',
            })

        return params

    if '.datasource' in filename:
        doc = parse_datasource(filename)
        node = doc.nodes[0]
        deps = []
        # reemplace tables on materialized columns
        columns = parse_table_structure(node['schema'])

        _format = 'csv'
        for x in columns:
            if x['default_value'] and x['default_value'].lower().startswith('materialized'):
                # turn expression to a select query to sql_get_used_tables can get the used tables
                q = 'select ' + x['default_value'][len('materialized'):]
                tables = await tb_client.sql_get_used_tables(q)
                # materualized columns expressions could have joins so we need to add them as a dep
                deps += tables
                # generate replacements and replace the query
                replacements = {t: t + resource_versions_string.get(t, '') for t in tables}

                replaced_results = await tb_client.replace_tables(q, replacements)
                x['default_value'] = replaced_results.replace('SELECT', 'materialized')
            if x.get('jsonpath', None):
                _format = 'ndjson'

        schema = ','.join(schema_to_sql_columns(columns))

        name = os.path.basename(filename).rsplit('.', 1)[0]

        if workspace_lib_paths:
            for wk_name, wk_path in workspace_lib_paths:
                try:
                    Path(filename).relative_to(wk_path)
                    name = f'{workspace_map.get(wk_name, wk_name)}.{name}'
                except ValueError:
                    # the path was not relative, not inside workspace
                    pass
        #
        res_name = name
        if tag and not is_shared_datasource(name):
            name = f'{tag}__{name}'

        version = (f'__v{doc.version}' if doc.version is not None else '')

        def append_version_to_name(name, version):
            if version != '':
                name = name.replace(".", "_")
                return name + version
            return name

        params = {
            "name": append_version_to_name(name, version),
            "schema": schema,
            "format": _format
        }

        params.update(get_engine_params(node))

        if 'kafka_connection_name' in node:
            kafka_params = await get_kafka_params(node)
            params.update(kafka_params)
            # drop the schema, it's fixed by the kafka connector
            del params["schema"]
            del params["engine"]
            del params["format"]

        if 'tags' in node:
            tags = {k: v[0]
                    for k, v in urllib.parse.parse_qs(node['tags']).items()}
            params.update(tags)

        resources = []

        resources.append({
            'resource': 'datasources',
            'resource_name': name,
            "version": doc.version,
            'params': params,
            'filename': filename,
            'keys': doc.keys,
            'deps': deps
        })

        # generate extra resources in case of the key
        if doc.keys:
            for k in doc.keys:
                resources += generate_resource_for_key(
                    k['column'],
                    name,
                    params['schema'],
                    version,
                    res_name
                )
                # set derived resources version the same the parent
                for x in resources:
                    x['version'] = doc.version

        return resources

    elif '.pipe' in filename:
        doc = parse_pipe(filename)
        version = (f'__v{doc.version}' if doc.version is not None else '')
        name = os.path.basename(filename).split('.')[0]
        description = doc.description if doc.description is not None else ''

        if tag and not is_shared_datasource(name):
            name = f'{tag}__{name}'

        deps = []
        nodes = []

        for node in doc.nodes:
            sql = node['sql']
            params = {
                'name': node['name'],
                'type': node.get('type', 'standard'),
                'description': node.get('description', ''),
            }
            if node.get('type', '').lower() == 'materialized':
                params.update({
                    'type': 'materialized',
                })

            sql = sql.strip()
            is_template = False
            if sql[0] == '%':
                sql_rendered = render_sql_template(sql[1:], test_mode=True)
                is_template = True
            else:
                sql_rendered = sql

            try:
                dependencies = await tb_client.sql_get_used_tables(sql_rendered, raising=True)
                deps += [t for t in dependencies if t not in [n['name'] for n in doc.nodes]]

            except Exception as e:
                raise click.ClickException(FeedbackManager.error_parsing_node(
                    node=node['name'], pipe=name, error=str(e)))

            if is_template:
                deps += get_used_tables_in_template(sql[1:])

            tag_ = ''
            if tag:
                tag_ = f'{tag}__'

            if ('engine_full' in node or 'engine' in node) and 'datasource' not in node:
                raise ValueError('Defining ENGINE options in a node requires a DATASOURCE')

            if 'datasource' in node:
                params['datasource'] = tag_ + node['datasource'] + \
                    resource_versions_string.get(tag_ + node['datasource'], '')
                deps += [node['datasource']]

            params.update(get_engine_params(node))

            def create_replacement_for_resource(tag, name):
                for old_ws, new_ws in workspace_map.items():
                    name = name.replace(f'{old_ws}.', f'{new_ws}.')
                if tag != '' and not is_shared_datasource(name):
                    name = tag + name
                return name + resource_versions_string.get(name, '')

            replacements = {x: create_replacement_for_resource(tag_, x) for x in deps if x not in [
                n['name'] for n in doc.nodes]}

            # when using templates replace_tables from clickhouse can't be used. Not ideal but ok
            if is_template:
                for old, new in replacements.items():
                    sql = re.sub(
                        '([\t \\n\']+|^)' + old + '([\t \\n\'\\)]+|$)', "\\1" + new + "\\2", sql)
            else:
                sql = await tb_client.replace_tables(sql, replacements)

            if 'tags' in node:
                tags = {k: v[0]
                        for k, v in urllib.parse.parse_qs(node['tags']).items()}
                params.update(tags)

            nodes.append({
                'sql': sql,
                'params': params
            })

        return [{
            'resource': 'pipes',
            'resource_name': name,
            "version": doc.version,
            'filename': filename,
            'name': name + version,
            'nodes': nodes,
            'deps': [x for x in set(deps)],
            'tokens': doc.tokens,
            'description': description
        }]
    else:
        raise Exception(FeedbackManager.error_file_extension(filename=filename))


def full_path_by_name(folder, name, workspace_lib_paths=None):
    f = Path(folder)
    ds = name + ".datasource"
    if os.path.isfile(os.path.join(folder, ds)):
        return f / ds
    if os.path.isfile(f / 'datasources' / ds):
        return f / 'datasources' / ds

    pipe = name + ".pipe"
    if os.path.isfile(os.path.join(folder, pipe)):
        return f / pipe

    if os.path.isfile(f / 'endpoints' / pipe):
        return f / 'endpoints' / pipe

    if os.path.isfile(f / 'pipes' / pipe):
        return f / 'pipes' / pipe

    if workspace_lib_paths:
        for wk_name, wk_path in workspace_lib_paths:
            if name.startswith(f'{wk_name}.'):
                r = full_path_by_name(wk_path, name.replace(f'{wk_name}.', ''))
                if r:
                    return r


def find_file_by_name(folder, name, verbose=False, is_raw=False, workspace_lib_paths=None):
    f = Path(folder)
    ds = name + ".datasource"
    if os.path.isfile(os.path.join(folder, ds)):
        return ds
    if os.path.isfile(f / 'datasources' / ds):
        return ds

    pipe = name + ".pipe"
    if os.path.isfile(os.path.join(folder, pipe)):
        return pipe

    if os.path.isfile(f / 'endpoints' / pipe):
        return pipe

    if os.path.isfile(f / 'pipes' / pipe):
        return pipe

    # look for the file in subdirectories if it's not found in datasources folder
    if workspace_lib_paths:
        r = None
        for wk_name, wk_path in workspace_lib_paths:
            if name.startswith(f'{wk_name}.'):
                r = find_file_by_name(wk_path, name.replace(f'{wk_name}.', ''), verbose, is_raw)
            if r:
                return r

    if not is_raw:
        return find_file_by_name(folder, get_dep_from_raw_tables(name), verbose=verbose, is_raw=True, workspace_lib_paths=workspace_lib_paths)

    if verbose:
        click.echo(FeedbackManager.warning_file_not_found_inside(name=name, folder=folder))


def drop_token(url):
    """
    drops token param from the url query string
    >>> drop_token('https://api.tinybird.co/v0/pipes/aaa.json?token=abcd&a=1')
    'https://api.tinybird.co/v0/pipes/aaa.json?a=1'
    >>> drop_token('https://api.tinybird.co/v0/pipes/aaa.json?a=1')
    'https://api.tinybird.co/v0/pipes/aaa.json?a=1'
    """
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    qs = {k: v[0] for k, v in qs.items()}  # change several arguments to single one
    if 'token' in qs:
        del qs['token']
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(qs)}"


class PipeChecker(unittest.TestCase):
    def __init__(self, current_pipe_url, checker_pipe_name, token, only_response_times, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_pipe_url = drop_token(current_pipe_url)
        self.checker_pipe_name = checker_pipe_name
        self.token = token
        self.only_response_times = only_response_times
        parsed = urlparse(self.current_pipe_url)
        self.qs = parse_qs(parsed.query)
        self.checker_pipe_url = f"{parsed.scheme}://{parsed.netloc}/v0/pipes/{self.checker_pipe_name}.json?{parsed.query}"

    def __str__(self):
        return f"current {self.current_pipe_url}\n    new {self.checker_pipe_url}"

    def runTest(self):
        if 'debug' in self.qs:
            self.skipTest('found debug param')
        headers = {'Authorization': f'Bearer {self.token}'}

        current_r = requests.get(self.current_pipe_url, headers=headers)
        checker_r = requests.get(self.checker_pipe_url, headers=headers)
        current_data = current_r.json().get('data', [])
        check_data = checker_r.json().get('data', [])
        error_check_data = checker_r.json().get('error', None)
        self.assertIsNone(error_check_data, 'You are trying to push a pipe with errors, please check the output or run with --no-check')
        if not self.only_response_times:
            self.assertEqual(len(current_data), len(check_data), "Number of elements does not match")
        for i, (current_data_e, check_data_e) in enumerate(zip(current_data, check_data)):
            if self.only_response_times:
                self.assertAlmostEqual(
                    current_r.elapsed.total_seconds(),
                    checker_r.elapsed.total_seconds(),
                    delta=.25,
                    msg="response time has changed by more than 25%"
                )
                continue
            self.assertEqual(list(current_data_e.keys()),
                             list(check_data_e.keys()))
            for x in current_data_e.keys():
                if type(current_data_e[x]) == float:
                    d = abs(current_data_e[x] - check_data_e[x])
                    self.assertLessEqual(d / current_data_e[x], 0.001)
                else:
                    self.assertEqual(
                        current_data_e[x], check_data_e[x], f"Failed on index {i}, key {x}")


async def check_pipe(pipe, host, token, populate, cl, limit=10, only_response_times=False):
    checker_pipe = deepcopy(pipe)
    checker_pipe['name'] = f"{checker_pipe['name']}__checker"

    # In case of doing --force for a materialized view, checker is being created as standard pipe
    for node in checker_pipe['nodes']:
        node['params']['type'] = 'standard'

    if populate:
        raise Exception(FeedbackManager.error_check_pipes_populate())

    headers = {'Authorization': f'Bearer {token}'}
    r = await requests_get(f"{host}/v0/pipes/{pipe['name']}/requests", headers=headers)

    if r.status_code != 200:
        raise Exception(FeedbackManager.error_check_pipes_api(pipe=pipe['name']))

    pipe_top_requests = r.json().get('requests', {}).get('top', [])
    suite = unittest.TestSuite()

    await new_pipe(checker_pipe, cl, replace=True, check=False, populate=populate, skip_tokens=True, skip_table_checks=True, ignore_sql_errors=True)

    for i, r in enumerate(pipe_top_requests):
        if i == limit:
            break
        suite.addTest(PipeChecker(r['endpoint_url'],
                                  checker_pipe['name'], token, only_response_times))
    result = unittest.TextTestResult(unittest.runner._WritelnDecorator(sys.stdout), descriptions=True, verbosity=2)
    suite.run(result)

    if not result.wasSuccessful():
        for _test, err in result.failures:
            try:
                i = err.index('AssertionError') + len('AssertionError :')
                click.echo('==== Test FAILED ====\n')
                click.echo(_test)
                click.echo(FeedbackManager.error_check_pipe(error=err[i:]))
                click.echo('=====================\n\n\n')
            except Exception:
                pass
        raise RuntimeError('Invalid results, you can bypass checks by running push with the --no-check flag')

    # Only delete if no errors, so we can check results after failure
    r = await requests_delete(f"{host}/v0/pipes/{checker_pipe['name']}", headers=headers)
    if r.status_code != 204:
        click.echo(FeedbackManager.warning_check_pipe(content=r.content))


async def new_pipe(p, tb_client: TinyB, replace=False, check=True, populate=False, wait_populate=False, skip_tokens=False, tag='', skip_table_checks=False, ignore_sql_errors=False, only_response_times=False, timeout=None):  # noqa: C901
    exists = False
    materialized = False

    # TODO use tb_client instead of calling the urls directly.
    host = tb_client.host
    token = tb_client.token

    headers = {'Authorization': f'Bearer {token}'}

    if tag:
        tag = tag + "__"

    cli_params = {}
    cli_params['cli_version'] = tb_client.version
    cli_params['description'] = p.get('description', '')
    cli_params['skip_table_checks'] = 'true' if skip_table_checks else 'false'
    cli_params['ignore_sql_errors'] = 'true' if ignore_sql_errors else 'false'

    r = await requests_get(f"{host}/v0/pipes/{p['name']}?{urlencode(cli_params)}", headers=headers)

    if r.status_code == 200:
        exists = True
        if replace:
            # TODO: this should create a different node and rename it to the final one on success
            if check and not populate:
                await check_pipe(p, host, token, populate, tb_client, only_response_times=only_response_times)

            pipe = r.json()

            delete_endpoint = await requests_put(f"{host}/v0/pipes/{p['name']}/endpoint?{urlencode(cli_params)}", headers=headers, data='')
            if delete_endpoint.status_code != 200:
                raise Exception(FeedbackManager.error_remove_endpoint(error=r.content))

            update_pipe = await requests_put(f"{host}/v0/pipes/{p['name']}?{urlencode(cli_params)}", headers=headers, data='')
            if update_pipe.status_code != 200:
                raise Exception(FeedbackManager.error_updating_pipe(error=r.content))

            for n in pipe.get('nodes', []):
                r = await requests_delete(f"{host}/v0/pipes/{p['name']}/nodes/{n['id']}?{urlencode(cli_params)}", headers=headers)
                if r.status_code != 204:
                    raise Exception(FeedbackManager.error_removing_node(pipe=p['name'], error=r.json()['error']))
        else:
            raise click.ClickException(FeedbackManager.error_pipe_already_exists(pipe=p['name']))
    else:
        r = await requests_post(f"{host}/v0/pipes?name={p['name']}&sql=select+1&{urlencode(cli_params)}", headers=headers, data='')
        if r.status_code != 200:
            try:
                raise Exception(FeedbackManager.error_creating_pipe(error=r.json()['error']))
            except ValueError:
                raise Exception(FeedbackManager.error_creating_pipe(error=r.content))

        dummy_node = r.json()['nodes'][0]['id']

        r = await requests_delete(f"{host}/v0/pipes/{p['name']}/nodes/{dummy_node}?{urlencode(cli_params)}", headers=headers)
        if r.status_code != 204:
            raise Exception(FeedbackManager.error_removing_dummy_node(error=r.content))

    for node in p['nodes']:
        params = node['params']
        if populate:
            params['populate'] = 'true'
        if params.get('type', '') == 'materialized':
            materialized = True
        params['cli_version'] = tb_client.version
        params['skip_table_checks'] = 'true' if skip_table_checks else 'false'
        params['ignore_sql_errors'] = 'true' if ignore_sql_errors else 'false'

        r = await requests_post(f"{host}/v0/pipes/{p['name']}/nodes?{urlencode(params)}", headers=headers, data=node['sql'])

        if r.status_code != 200:
            if not exists:
                # remove the pipe when it does not exist
                await requests_delete(f"{host}/v0/pipes/{p['name']}?{urlencode(cli_params)}", headers=headers)
            raise Exception(FeedbackManager.error_creating_node(pipe=p['name'], error=r.json()['error']))

        new_node = r.json()
        pipe_type = params.get('type', None)

        if pipe_type == 'materialized':
            created_datasource = new_node.get('created_datasource', False)
            datasource = new_node.get('datasource')

            if created_datasource:
                click.echo(FeedbackManager.info_materialized_datasource_created(node=new_node.get('name', 'unknown'), datasource=datasource['name']))
            else:
                click.echo(FeedbackManager.info_materialized_datasource_used(node=new_node.get('name', 'unknown'), datasource=datasource['name']))

            if populate:
                job_url = new_node.get('job', {}).get('job_url', None)
                job_id = new_node.get('job', {}).get('job_id', None)
                click.echo(FeedbackManager.info_populate_job_url(url=job_url))

                if wait_populate:
                    with click.progressbar(label="Populating ", length=100, show_eta=False, show_percent=True, fill_char=click.style("█", fg="green")) as progress_bar:
                        def progressbar_cb(res):
                            if 'progress_percentage' in res:
                                progress_bar.update(int(round(res['progress_percentage'])) - progress_bar.pos)
                            elif res['status'] != 'working':
                                progress_bar.update(progress_bar.length)
                        try:
                            result = await asyncio.wait_for(tb_client.wait_for_job(job_id, status_callback=progressbar_cb), timeout)
                            if result['status'] != 'done':
                                click.echo(FeedbackManager.error_while_populating(error=result['error']))
                        except asyncio.TimeoutError:
                            await tb_client.job_cancel(job_id)
                            raise click.ClickException(FeedbackManager.error_while_populating(error="Reach timeout, job cancelled"))
                        except Exception as e:
                            raise click.ClickException(FeedbackManager.error_while_populating(error=str(e)))

        endpoint_node = r.json()['id']
        r = await requests_put(f"{host}/v0/pipes/{p['name']}/endpoint?{urlencode(cli_params)}", headers=headers, data=endpoint_node)
        if r.status_code != 200:
            raise Exception(FeedbackManager.error_creating_endpoint(node=endpoint_node, pipe=p['name'], error=r.json()['error']))

    if p['tokens'] and not skip_tokens:

        # search for token with specified name and adds it if not found or adds permissions to it
        t = None
        for tk in p['tokens']:
            token_name = tag + tk['token_name']
            t = await tb_client.get_token_by_name(token_name)
            if t:
                break
        if not t:
            token_name = tag + tk['token_name']
            click.echo(FeedbackManager.info_create_not_found_token(token=token_name))
            url = f"{host}/v0/tokens?name={token_name}&scope=PIPES:{tk['permissions']}:{p['name']}&{urlencode(cli_params)}"
            r = await requests_post(url, headers=headers, data='')
            if r.status_code != 200:
                raise Exception(FeedbackManager.error_creating_pipe(error=r.json()['error']))
            token = r.json()['token']
        else:
            click.echo(FeedbackManager.info_create_found_token(token=token_name))
            scopes = [f"PIPES:{tk['permissions']}:{p['name']}"]
            for x in t['scopes']:
                sc = x['type'] if 'resource' not in x else f"{x['type']}:{x['resource']}"
                scopes.append(sc)
            s = '&'.join([f'scope={x}' for x in scopes])
            url = f"{host}/v0/tokens/{t['token']}?{s}&{urlencode(cli_params)}"
            r = await requests_put(url, headers=headers, data='')
            if r.status_code != 200:
                raise Exception(FeedbackManager.error_creating_pipe(error=r.json()['error']))
            token = t['token']
        click.echo(FeedbackManager.success_test_endpoint(host=host, pipe=p['name'], token=token))
    else:
        if not materialized and not skip_tokens:
            click.echo(FeedbackManager.success_test_endpoint_no_token(host=host, pipe=p['name']))


async def new_ds(ds, client, replace=False, skip_table_checks=False, skip_confirmation=False):
    ds_name = ds['params']['name']

    try:
        await client.get_datasource(ds_name)
        datasource_exists = True
    except DoesNotExistException:
        datasource_exists = False

    if not datasource_exists:
        params = ds['params']
        params['skip_table_checks'] = 'true' if skip_table_checks else 'false'

        try:
            await client.datasource_create_from_definition(params)
        except Exception as e:
            raise Exception(FeedbackManager.error_creating_datasource(error=str(e)))
        return

    if not replace:
        raise click.ClickException(FeedbackManager.error_datasource_already_exists(datasource=ds_name))

    alter_response = None
    alter_error_message = None

    try:
        # Schema fixed by the kafka connector
        if 'kafka_connection_name' not in ds['params']:
            alter_response = await client.alter_datasource(ds_name, ds['params']['schema'], True)
    except Exception as e:
        if "There were no operations to perform" in str(e):
            pass
        else:
            alter_error_message = str(e)

    if alter_response:
        click.echo(FeedbackManager.info_datasource_doesnt_match_current_schema(datasource=ds_name))
        for operation in alter_response["operations"]:
            click.echo(f"**   -  {operation}")

        if skip_confirmation:
            make_changes = True
        else:
            make_changes = click.prompt(FeedbackManager.info_ask_for_alter_confirmation()).lower() == "y"

        if make_changes:
            await client.alter_datasource(ds_name, ds['params']['schema'], False)
            click.echo(FeedbackManager.success_datasource_alter())
            return
        else:
            alter_error_message = "Alter datasource cancelled"

    # removed replacing by default. When a datasource is removed data is
    # removed and all the references needs to be updated
    if os.getenv('TB_I_KNOW_WHAT_I_AM_DOING') and click.prompt(FeedbackManager.info_ask_for_datasource_confirmation()) == ds_name:  # TODO move to CLI
        try:
            await client.datasource_delete(ds_name)
            click.echo(FeedbackManager.success_delete_datasource(datasource=ds_name))
        except Exception:
            raise Exception(FeedbackManager.error_removing_datasource(datasource=ds_name))
        return
    else:
        if alter_error_message:
            raise click.ClickException(FeedbackManager.error_datasource_already_exists_and_alter_failed(
                datasource=ds_name, alter_error_message=alter_error_message))
        else:
            click.echo(FeedbackManager.warning_datasource_already_exists(datasource=ds_name))


async def exec_file(r, tb_client, override, check, debug, populate, wait_populate, tag, skip_table_checks=False, ignore_sql_errors=False, skip_confirmation=False, only_response_times=False, timeout=None):

    if debug:
        click.echo(FeedbackManager.debug_running_file(file=pp.pformat(r)))
    if r['resource'] == 'pipes':
        await new_pipe(
            r,
            tb_client,
            override,
            check,
            populate,
            wait_populate,
            tag=tag,
            skip_table_checks=skip_table_checks,
            ignore_sql_errors=ignore_sql_errors,
            only_response_times=only_response_times,
            timeout=timeout)

    elif r['resource'] == 'datasources':
        await new_ds(
            r,
            tb_client,
            override,
            skip_table_checks=skip_table_checks,
            skip_confirmation=skip_confirmation
        )
    else:
        raise Exception(FeedbackManager.error_unknown_resource(resource=r['resource']))


def get_name_tag_version(ds):
    """
    Given a name like "name__dev__v0" returns ['name', 'dev', 'v0']
    >>> get_name_tag_version('dev__name__v0')
    {'name': 'name', 'tag': 'dev', 'version': 0}
    >>> get_name_tag_version('name__v0')
    {'name': 'name', 'tag': None, 'version': 0}
    >>> get_name_tag_version('dev__name')
    {'name': 'name', 'tag': 'dev', 'version': None}
    >>> get_name_tag_version('name')
    {'name': 'name', 'tag': None, 'version': None}
    >>> get_name_tag_version('horario__3__pipe')
    {'name': '3__pipe', 'tag': 'horario', 'version': None}
    >>> get_name_tag_version('horario__checker')
    {'name': 'horario__checker', 'tag': None, 'version': None}
    >>> get_name_tag_version('dev__horario__checker')
    {'name': 'horario__checker', 'tag': 'dev', 'version': None}
    >>> get_name_tag_version('tg__dActividades__v0_pipe_3907')
    {'name': 'dActividades', 'tag': 'tg', 'version': 0}
    >>> get_name_tag_version('tg__dActividades__va_pipe_3907')
    {'name': 'dActividades__va_pipe_3907', 'tag': 'tg', 'version': None}
    >>> get_name_tag_version('tg__origin_workspace.shared_ds__v3907')
    {'name': 'origin_workspace.shared_ds', 'tag': 'tg', 'version': 3907}
    """
    tk = ds.rsplit('__', 2)
    if len(tk) == 1:
        return {'name': tk[0], 'tag': None, 'version': None}
    elif len(tk) == 2:
        if tk[1][0] == 'v' and re.match('[0-9]+$', tk[1][1:]):
            return {'name': tk[0], 'tag': None, 'version': int(tk[1][1:])}
        else:
            if tk[1] == 'checker':
                return {'name': tk[0] + "__" + tk[1], 'tag': None, 'version': None}
            return {'name': tk[1], 'tag': tk[0], 'version': None}
    elif len(tk) == 3:
        if tk[2] == 'checker':
            return {'name': tk[1] + "__" + tk[2], 'tag': tk[0], 'version': None}
        if tk[2][0] == 'v':
            parts = tk[2].split('_')
            try:
                return {'name': tk[1], 'tag': tk[0], 'version': int(parts[0][1:])}
            except ValueError:
                return {'name': f'{tk[1]}__{tk[2]}', 'tag': tk[0], 'version': None}
        else:
            return {'name': '__'.join(tk[1:]), 'tag': tk[0], 'version': None}

    return ds


def get_resource_versions(datasources):
    """
    return the latest version for all the datasources
    """
    versions = {}
    for x in datasources:
        t = get_name_tag_version(x)
        name = t['name']
        if t['tag']:
            name = f"{t['tag']}__{name}"
        if t.get('version', None) is not None:
            versions[name] = t['version']
    return versions


def get_remote_resource_name_without_version(remote_resource_name: str) -> str:
    """
    >>> get_remote_resource_name_without_version("r__datasource")
    'r__datasource'
    >>> get_remote_resource_name_without_version("r__datasource__v0")
    'r__datasource'
    >>> get_remote_resource_name_without_version("datasource")
    'datasource'
    """
    parts = get_name_tag_version(remote_resource_name)
    if parts['tag']:
        return parts['tag'] + '__' + parts['name']
    else:
        return parts['name']


def get_dep_from_raw_tables(x):
    """
    datasources KEY command generates tables, this transform the used table with the source file
    >>> get_dep_from_raw_tables('test')
    'test'
    >>> get_dep_from_raw_tables('test_join_by_column')
    'test'
    """

    try:
        return x[:x.index('_join_by_')]
    except ValueError:
        return x


async def build_graph(filenames, tb_client, tag='', resource_versions=None, workspace_map=None, process_dependencies=False, verbose=False, skip_connectors=False, workspace_lib_paths=None):  # noqa: C901 B006
    """process files"""
    to_run = {}
    deps = []
    dep_map = {}
    if not workspace_map:
        workspace_map = {}

    deps_tag = ''
    if tag:
        deps_tag = f'{tag}__'

    dir_path = os.getcwd()

    async def process(filename, deps, dep_map, to_run, workspace_lib_paths):
        name, kind = filename.rsplit('.', 1)

        try:
            res = await process_file(
                filename,
                tb_client,
                dir_path,
                tag,
                resource_versions=resource_versions,
                verbose=verbose,
                skip_connectors=skip_connectors,
                workspace_map=workspace_map,
                workspace_lib_paths=workspace_lib_paths
            )
        except click.ClickException as e:
            raise e
        except Exception as e:
            raise click.ClickException(e)

        for r in res:
            fn = r['resource_name']
            to_run[fn] = r
            file_deps = r.get('deps', [])
            deps += file_deps
            # calculate and look for deps
            dep_list = []
            for x in file_deps:
                if x not in INTERNAL_TABLES:
                    f = find_file_by_name(dir_path, x, verbose, workspace_lib_paths=workspace_lib_paths)
                    if f:
                        dep_list.append(deps_tag + f.rsplit('.', 1)[0])
            dep_map[fn] = set(dep_list)
        return os.path.basename(name)

    processed = set()
    for filename in filenames:
        if verbose:
            click.echo(FeedbackManager.info_processing_file(filename=filename))
        name = await process(filename, deps, dep_map, to_run, workspace_lib_paths)
        processed.add(name)

    if process_dependencies:
        while len(deps) > 0:
            dep = deps.pop()
            if dep not in processed:
                processed.add(dep)
                f = full_path_by_name(dir_path, dep, workspace_lib_paths)
                if f:
                    if verbose:
                        try:
                            processed_filename = f.relative_to(os.getcwd())
                        except ValueError:
                            processed_filename = f
                        click.echo(FeedbackManager.info_processing_file(filename=processed_filename))
                    await process(str(f), deps, dep_map, to_run, workspace_lib_paths)

    return to_run, dep_map


def get_project_filenames(folder):
    folders = [
        f'{folder}/*.datasource',
        f'{folder}/datasources/*.datasource',
        f'{folder}/*.pipe',
        f'{folder}/pipes/*.pipe',
        f'{folder}/endpoints/*.pipe',
    ]
    filenames = []
    for x in folders:
        filenames += glob.glob(x)
    return filenames


async def folder_push(tb_client: TinyB, tag='', filenames=None, dry_run=False, check=False, push_deps=False,  # noqa: C901
                      debug=False, force=False, folder='.', populate=False, upload_fixtures=False, wait=False,
                      skip_table_checks=False, ignore_sql_errors=False, skip_confirmation=None, only_response_times=False,
                      workspace_map=None, workspace_lib_paths=None, no_versions=False, timeout=None):

    if not workspace_map:
        workspace_map = {}
    if not workspace_lib_paths:
        workspace_lib_paths = []

    workspace_lib_paths = list(workspace_lib_paths)
    # include vendor libs without overriding user ones without overriding user ones
    existing_workspaces = set(x[1] for x in workspace_lib_paths)
    vendor_path = Path('vendor')
    if vendor_path.exists():
        for x in vendor_path.iterdir():
            if x.is_dir() and x.name not in existing_workspaces:
                workspace_lib_paths.append((x.name, x))

    datasources = await tb_client.datasources()
    pipes = await tb_client.pipes()

    existing_resources = [x['name'] for x in datasources] + [x['name'] for x in pipes]
    # replace workspace mapping names
    for old_ws, new_ws in workspace_map.items():
        existing_resources = [x.replace(f'{old_ws}.', f'{new_ws}.') for x in existing_resources]

    if not no_versions:
        resource_versions = get_resource_versions(existing_resources)
    else:
        resource_versions = {}

    remote_resource_names = [get_remote_resource_name_without_version(x) for x in existing_resources]

    # replace workspace mapping names
    for old_ws, new_ws in workspace_map.items():
        remote_resource_names = [x.replace(f'{old_ws}.', f'{new_ws}.') for x in remote_resource_names]

    if not filenames:
        filenames = get_project_filenames(folder)

    # build graph to get new versions for all the files involved in the query
    # dependencies need to be processed always to get the versions
    resources, dep_map = await build_graph(
        filenames,
        tb_client,
        tag=tag,
        process_dependencies=True,
        workspace_map=workspace_map,
        skip_connectors=True,
        workspace_lib_paths=workspace_lib_paths
    )

    # update existing versions
    if not no_versions:
        latest_datasource_versions = resource_versions.copy()

        for dep in resources.values():
            ds = dep['resource_name']
            if dep['version'] is not None:
                latest_datasource_versions[ds] = dep['version']
    else:
        latest_datasource_versions = {}

    # build the graph again with the rigth version
    to_run, dep_map = await build_graph(
        filenames,
        tb_client,
        tag=tag,
        resource_versions=latest_datasource_versions,
        workspace_map=workspace_map,
        process_dependencies=push_deps,
        verbose=True,
        workspace_lib_paths=workspace_lib_paths
    )

    if debug:
        pp.pprint(to_run)

    click.echo(FeedbackManager.info_building_dependencies())

    for group in toposort(dep_map):
        for name in group:
            if name in to_run:
                if not dry_run:
                    if name not in remote_resource_names or resource_versions.get(name.replace(".", "_"), '') != latest_datasource_versions.get(name, '') or force:
                        if name not in resource_versions:
                            version = ''
                            if name in latest_datasource_versions:
                                version = f'(v{latest_datasource_versions[name]})'
                            click.echo(FeedbackManager.info_processing_new_resource(name=name, version=version))
                        else:
                            click.echo(FeedbackManager.info_processing_resource(
                                name=name,
                                version=latest_datasource_versions[name],
                                latest_version=resource_versions.get(name)
                            ))
                        try:
                            await exec_file(to_run[name], tb_client, force, check, debug, populate, wait, tag,
                                            skip_table_checks, ignore_sql_errors, skip_confirmation, only_response_times, timeout)
                            click.echo(FeedbackManager.success_create(
                                name=name if to_run[name]['version'] is None else f'{name}__v{to_run[name]["version"]}'))

                        except Exception as e:
                            exception = FeedbackManager.error_push_file_exception(filename=to_run[name]['filename'], error=e)
                            if '[CLI] skip_table_checks_error' in exception:
                                skip_table_checks_error = FeedbackManager.error_skip_table_checks_path()
                                exception = exception.replace('[CLI] skip_table_checks_error', f', {skip_table_checks_error}')
                            raise click.ClickException(exception)
                    else:
                        click.echo(FeedbackManager.warning_name_already_exists(
                            name=name if to_run[name]['version'] is None else f'{name}__v{to_run[name]["version"]}'))
                else:
                    if name not in remote_resource_names or resource_versions.get(name.replace(".", "_"), '') != latest_datasource_versions.get(name, '') or force:
                        if name not in resource_versions:
                            version = ''
                            if name in latest_datasource_versions:
                                version = f'(v{latest_datasource_versions[name]})'
                            click.echo(FeedbackManager.info_dry_processing_new_resource(name=name, version=version))
                        else:
                            click.echo(FeedbackManager.info_dry_processing_resource(
                                name=name,
                                version=latest_datasource_versions[name],
                                latest_version=resource_versions.get(name)
                            ))
                    else:
                        click.echo(FeedbackManager.warning_dry_name_already_exists(name=name))

    if not dry_run:
        if upload_fixtures:
            click.echo(FeedbackManager.info_pushing_fixtures())
            processed = set()
            for group in toposort(dep_map):
                for f in group:
                    name = os.path.basename(f)
                    if name not in processed:
                        if name in to_run:
                            await check_data(tb_client, to_run[name], debug, folder)
                            processed.add(name)
            for f in to_run:
                if f not in processed:
                    await check_data(tb_client, to_run[f], debug, folder)
        else:
            click.echo(FeedbackManager.info_not_pushing_fixtures())


async def check_data(cl, r, debug, folder=''):
    if debug:
        click.echo(FeedbackManager.info_checking_file(file=pp.pformat(r)))
    if r['resource'] == 'pipes':
        pass
    elif r['resource'] == 'datasources':
        name = os.path.basename(r['filename']).rsplit('.', 1)[0]
        csv_test_file = Path(folder) / 'fixtures' / f'{name}.csv'
        if not csv_test_file.exists():
            csv_test_file = Path(folder) / 'datasources' / 'fixtures' / f'{name}.csv'
        if csv_test_file.exists():
            click.echo(FeedbackManager.info_checking_file_size(filename=r['filename'], size=sizeof_fmt(os.stat(csv_test_file).st_size)))
            sys.stdout.flush()
            try:
                with open(csv_test_file, 'rb') as file:
                    res = await cl.datasource_append_data(r['params']['name'], file)
                click.echo(FeedbackManager.success_processing_blocks(num_blocks=len(res['blocks'])))
            except Exception as e:
                raise click.ClickException(FeedbackManager.error_processing_blocks(error=e))

        else:
            click.echo(FeedbackManager.warning_file_not_found(name=csv_test_file))

    else:
        raise Exception(FeedbackManager.error_unknown_resource(resource=r['resource']))
