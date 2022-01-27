from psycopg2.extensions import AsIs

from syngenta_digital_dta.postgres import json_formatting
from syngenta_digital_dta.common import dict_merger
from syngenta_digital_dta.common import logger
from syngenta_digital_dta.common import publisher
from syngenta_digital_dta.common import schema_mapper
from syngenta_digital_dta.common.base_adapter import BaseAdapter
from syngenta_digital_dta.postgres.sql_connection import sql_connection
from syngenta_digital_dta.postgres.sql_connector import SQLConnector


class PostgresAdapter(BaseAdapter):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.endpoint = kwargs['endpoint']
        self.database = kwargs['database']
        self.table = kwargs['table']
        self.user = kwargs['user']
        self.password = kwargs['password']
        self.port = kwargs.get('port', 5432)
        self.relationships = kwargs.get('relationships', {})
        self.model_schema_file = kwargs['model_schema_file']
        self.model_schema = kwargs['model_schema']
        self.model_identifier = kwargs['model_identifier']
        self.autocommit = kwargs.get('autocommit', False)
        self.sns_arn = kwargs.get('sns_arn')
        self.author_identifier = kwargs.get('author_identifier')
        self.event_publisher = publisher
        self.connection = None
        self.cursor = None

    @sql_connection
    def connect(self, connector: SQLConnector):
        self.connection = connector.connect()
        self.cursor = connector.cursor()

    def commit(self, commit=True):
        if commit:
            self.connection.commit()

    def create(self, **kwargs):
        return self.insert(**kwargs)

    def insert(self, **kwargs):
        query = 'INSERT INTO %(table)s (%(columns)s) VALUES %(values)s'
        params = self.__get_data_params(**kwargs)
        exists = self.__get_existing(**kwargs)
        if exists:
            self.__raise_error('NOT_UNIQUE', **kwargs)
        self.__execute(query, params, **kwargs)
        super().publish('create', params['data'])
        return params['data']

    def update(self, **kwargs):
        exists = self.__get_existing(**kwargs)
        if not exists:
            self.__raise_error('NOT_EXISTS', **kwargs)
        kwargs['data'] = dict_merger.merge(exists, kwargs['data'], **kwargs)
        update = self.__create_update_query(kwargs['data'])
        self.__execute(update['query'], update['params'], **kwargs)
        super().publish('update', kwargs['data'])
        return kwargs['data']

    def upsert(self, **kwargs):
        exists = self.__get_existing(**kwargs)
        if exists:
            return self.update(**kwargs)
        return self.insert(**kwargs)

    def delete(self, identifier_value, **kwargs):
        query = 'DELETE FROM %(table)s WHERE %(identifier)s = %(identifier_value)s'
        params = self.__compose_params(data={f'{self.model_identifier}': identifier_value})
        self.__execute(query, params, **kwargs)
        super().publish('delete', params['data'])

    def read(self, identifier_value, **kwargs):
        return self.get(identifier_value, **kwargs)

    def get(self, identifier_value, **kwargs):
        query = 'SELECT * FROM %(table)s WHERE %(identifier)s = %(identifier_value)s'
        params = self.__compose_params(data={f'{self.model_identifier}': identifier_value})
        self.__execute(query, params, **kwargs)
        return self.__get_data()

    def read_all(self, **kwargs):
        return self.get_all(**kwargs)

    def get_all(self, **kwargs):
        get_query = self.__create_get_all_query(**kwargs)
        self.__execute(get_query['query'], get_query['params'], **kwargs)
        return self.__get_data(all=True)

    def get_relationship(self, relationship, **kwargs):
        join = self.__create_join_query(relationship, **kwargs)
        self.__execute(join['query'], join['params'], **kwargs)
        return self.__get_data(all=True)

    def create_table(self, **kwargs):
        if not kwargs['query'].lower().startswith('create table'):
            self.__raise_error('TABLE_WRITE_ONLY', **kwargs)
        query = kwargs.pop('query')
        self.__execute(query, params={}, commit=True, rollback=True)

    def query(self, **kwargs):
        if 'params' not in kwargs:
            self.__raise_error('PARAMS_REQUIRED', **kwargs)
        if any(word in kwargs['query'].lower() for word in ['insert', 'update', 'delete']):
            self.__raise_error('READ_ONLY', **kwargs)
        query = kwargs.pop('query')
        params = kwargs.pop('params')
        self.__execute(query, params, **kwargs)
        return self.__get_data(all=True)

    def bulk_insert_json(self, **kwargs):

        statement = json_formatting.insert_json_into_table(
            json=kwargs['json'],
            table_name=kwargs['table_name'],
            column_map=kwargs['column_map'],
            json_column_map=kwargs['json_column_map'],
            function_map=kwargs.get('function_map', {}),
            conflict_cols=kwargs.get('conflict_cols'),
            update_cols=kwargs.get('update_cols')
        )

        self.__execute(query=statement, params={}, commit=True, rollback=True)

    def create_index(self, table_name, index_columns):
        index_name = f"index_{'_'.join(index_columns)}"
        index_cols = f"({', '.join(index_columns)})"

        statement = f"CREATE INDEX {index_name} ON {table_name} {index_cols}"

        self.__execute(query=statement, params={})

    def __create_join_query(self, relationship, **kwargs):
        params = {
            'table': AsIs(self.table),
            'identifier': AsIs(self.model_identifier),
            'relationship': AsIs(relationship),
            'related': AsIs(self.relationships.get(relationship))
        }
        query = 'SELECT %(table)s.*, %(relationship)s.* FROM %(table)s JOIN %(relationship)s ON %(relationship)s.%(related)s = %(table)s.%(identifier)s'
        query += self.__build_addon_statements(params, **kwargs)
        return {'query': query, 'params': params}

    def __create_get_all_query(self, **kwargs):
        params = {
            'table': AsIs(self.table),
        }
        where_query = self.__build_addon_statements(params, **kwargs)
        return {
            'query': f'SELECT * FROM %(table)s {where_query}',
            'params': params
        }

    def __build_addon_statements(self, params, **kwargs):
        query = self.__build_where_statment(kwargs.get('where'), params)
        query += self.__build_order_by_statement(
            kwargs.get('orderby_column', self.model_identifier),
            kwargs.get('orderby_order', 'ASC'),
            params
        )
        query += self.__build_limit_statment(kwargs.get('limit', 1000), params)
        query += self.__build_offset_statment(kwargs.get('offset', 0), params)
        return query

    def __build_where_statment(self, where, params):
        if where is None:
            return ''
        where_list = []
        for where_key in where.keys():
            where_value = f'{where_key}-value'
            where_list.append(f'%(table)s.%({where_key})s = %({where_value})s')
            params[where_value] = where[where_key]
            params[where_key] = AsIs(where_key)
        where_query = ' AND '.join(where_list)
        return ' WHERE ' + where_query

    def __build_limit_statment(self, limit, params):
        if limit is None:
            return ''
        params['limit'] = limit
        return ' LIMIT %(limit)s'

    def __build_offset_statment(self, offset, params):
        if offset is None:
            return ''
        params['offset'] = offset
        return ' OFFSET %(offset)s'

    def __build_order_by_statement(self, orderby_column, orderby_order, params):
        params['orderby_column'] = AsIs(orderby_column)
        params['orderby_order'] = AsIs(orderby_order)
        return ' ORDER BY %(table)s.%(orderby_column)s %(orderby_order)s'

    def __create_update_query(self, data):
        params = {
            'table': AsIs(self.table),
            'identifier': AsIs(self.model_identifier),
            'identifier_value': data[self.model_identifier]
        }
        update_list = []
        for key in data.keys():
            value = f'{key}-value'
            update_list.append(f'%({key})s = %({value})s')
            params[value] = data[key]
            params[key] = AsIs(key)
        query = ', '.join(update_list)
        return {
            'query': f'UPDATE %(table)s SET {query} WHERE %(identifier)s = %(identifier_value)s',
            'params': params
        }

    def __get_existing(self, **kwargs):
        query = 'SELECT * FROM %(table)s WHERE %(identifier)s = %(identifier_value)s LIMIT 1'
        params = self.__compose_params(kwargs['data'])
        self.__execute(query, params, **kwargs)
        result = self.__get_data()
        if result:
            return result
        return False

    def __get_data_params(self, **kwargs):
        data = schema_mapper.map_to_schema(kwargs['data'], self.model_schema_file, self.model_schema)
        columns = data.keys()
        values = [data[column] for column in columns]
        return self.__compose_params(data, columns, values)

    def __get_data(self, **kwargs):
        if kwargs.get('all', False):
            get = self.cursor.fetchall
        else:
            get = self.cursor.fetchone
        try:
            return get()
        except:
            return [] if kwargs.get('all', False) else None

    def __execute(self, query, params, **kwargs):
        try:
            self.__debug(query, params, kwargs.get('debug', False))
            self.cursor.execute(query, params)
            self.commit(kwargs.get('commit', False))
        except Exception as error:
            self.__debug(query, params, True)
            logger.log(level='ERROR', log={'error': error})
            if kwargs.get('rollback'):
                self.connection.rollback()
            raise Exception(f'error with execution, check logs - {error}') from error

    def __compose_params(self, data, columns="*", values=None):
        if not values:
            values = []
        return {
            'data': data,
            'table': AsIs(self.table),
            'columns': AsIs(', '.join(columns)),
            'values': tuple(values),
            'identifier': AsIs(self.model_identifier),
            'identifier_value': data[self.model_identifier]
        }

    def __debug(self, query, params, debug=False):
        if debug and self.cursor:
            logger.log(level='INFO', log=self.cursor.mogrify(query, params))

    def __raise_error(self, error_type, **kwargs):
        if error_type == 'PARAMS_REQUIRED':
            raise Exception('params kwargs are required to prevent sql inject; send empty dict if not needed')
        if error_type == 'READ_ONLY':
            raise Exception(
                'query method is for read-only operations; please use another function for destructive operatins'
            )
        if error_type == 'TABLE_WRITE_ONLY':
            raise CreateTableException(
                'create table query-string must start with "create table"'
            )
        if error_type == 'NOT_UNIQUE':
            raise Exception(
                f'row already exist with {self.model_identifier} = {kwargs.get("data", {}).get(self.model_identifier)}'
            )
        if error_type == 'NOT_EXISTS':
            raise Exception(
                f'row does not exist with {self.model_identifier} = {kwargs.get("data", {}).get(self.model_identifier)}'
            )
        raise Exception(f'Something went wrong and I am not sure how I got here: {error_type}')


class CreateTableException(Exception):
    pass
