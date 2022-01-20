#   See the NOTICE file distributed with this work for additional information
#   regarding copyright ownership.
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#       http://www.apache.org/licenses/LICENSE-2.0
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from functools import lru_cache
import sqlalchemy as sa
import re


@lru_cache(maxsize=None)
def get_engine(hostname, port='3306', user='ensro', password=''):
    uri = 'mysql://{}:{}@{}:{}'.format(user,
                                       password,
                                       hostname,
                                       port)
    return sa.create_engine(uri, pool_recycle=3600)


def get_schema_names(engine):
    return sa.inspect(engine).get_schema_names()


def get_table_names(engine, database):
    try:
        return sa.inspect(engine).get_table_names(schema=database)
    except sa.exc.OperationalError as e:
        raise ValueError('Invalid database: {}'.format(database)) from e


def _filter_names(names_list, filters):
    filter_names = set()
    filter_regexes = []
    if filters:
        try:
            for filter_name in filters:
                filter_regex = '^{}$'.format(filter_name)
                re.compile(filter_regex)
                filter_regexes.append(filter_regex)
        except re.error as e:
            raise ValueError('Invalid name_filter: {}'.format(filter_name)) from e
        filter_names_re = re.compile('|'.join(filter_regexes))
        filter_names = set(filter(filter_names_re.match, names_list))
    return filter_names


def _apply_filters(names_list, incl_filters, skip_filters):
    names = set(names_list)
    if incl_filters:
        names = _filter_names(names_list, incl_filters)
    skip_names = _filter_names(names_list, skip_filters)
    return names.difference(skip_names)


def get_database_set(
        hostname, port, user='ensro', password='', incl_filters=None, skip_filters=None
):
    try:
        db_engine = get_engine(hostname, port, user, password)
    except RuntimeError as e:
        raise ValueError('Invalid hostname: {} or port: {}'.format(hostname, port)) from e
    database_list = get_schema_names(db_engine)
    return _apply_filters(database_list, incl_filters, skip_filters)


def get_table_set(
        hostname, port, database, user='ensro', password='', incl_filters=None, skip_filters=None
):
    try:
        db_engine = get_engine(hostname, port, user, password)
    except RuntimeError as e:
        raise ValueError('Invalid hostname: {} or port: {}'.format(hostname, port)) from e
    table_list = get_table_names(db_engine, database)
    return _apply_filters(table_list, incl_filters, skip_filters)

