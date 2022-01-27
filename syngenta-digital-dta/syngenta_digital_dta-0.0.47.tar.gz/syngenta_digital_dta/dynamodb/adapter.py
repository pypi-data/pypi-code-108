from functools import lru_cache

import boto3
from boto3.dynamodb.conditions import Attr

from syngenta_digital_dta.common import schema_mapper
from syngenta_digital_dta.common import dict_merger
from syngenta_digital_dta.common.base_adapter import BaseAdapter


class BatchItemException(Exception):
    pass


class DynamodbAdapter(BaseAdapter):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.table = self._get_dynamo_table(kwargs['table'], kwargs.get('endpoint'))
        self.model_schema_file = kwargs['model_schema_file']
        self.model_schema = kwargs['model_schema']
        self.model_identifier = kwargs['model_identifier']
        self.model_version_key = kwargs['model_version_key']

    @lru_cache(maxsize=128)
    def _get_dynamo_table(self, table, endpoint=None):
        return boto3.resource('dynamodb', endpoint_url=endpoint).Table(table)

    def create(self, **kwargs):
        if kwargs.get('operation') == 'overwrite':
            return self.overwrite(**kwargs)
        return self.insert(**kwargs)

    def read(self, **kwargs):
        if kwargs.get('operation') == 'query':
            return self.query(**kwargs)
        if kwargs.get('operation') == 'scan':
            return self.scan(**kwargs)
        return self.get(**kwargs)

    def scan(self, **kwargs):
        if kwargs.get('raw_scan'):
            return self.table.scan(**kwargs.get('query', {}))
        return self.table.scan(**kwargs.get('query', {})).get('Items', [])

    def get(self, **kwargs):
        return self.table.get_item(**kwargs.get('query', {})).get('Item', {})

    def query(self, **kwargs):
        if kwargs.get('raw_query'):
            return self.table.query(**kwargs.get('query', {}))

        return self.table.query(**kwargs.get('query', {})).get('Items', [])

    def overwrite(self, **kwargs):
        overwrite_item = schema_mapper.map_to_schema(kwargs['data'], self.model_schema_file, self.model_schema)
        self.table.put_item(Item=overwrite_item)
        super().publish('create', overwrite_item)
        return overwrite_item

    def insert(self, **kwargs):
        new_item = schema_mapper.map_to_schema(kwargs['data'], self.model_schema_file, self.model_schema)
        self.table.put_item(Item=new_item, ConditionExpression=Attr(self.model_identifier).not_exists())
        super().publish('create', new_item)
        return new_item

    def batch_insert(self, **kwargs):
        data = kwargs['data']
        batch_size = kwargs.get('batch_size', 25)

        if not isinstance(data, list):
            raise BatchItemException('Batched data must be contained within a list')

        batched_data = (data[pos:pos + batch_size] for pos in range(0, len(data), batch_size))
        with self.table.batch_writer() as writer:
            for batch in batched_data:
                for item in batch:
                    writer.put_item(Item=item)

    def delete(self, **kwargs):
        kwargs['query']['ReturnValues'] = 'ALL_OLD'
        result = self.table.delete_item(**kwargs['query']).get('Attributes', {})
        super().publish('delete', result)
        return result

    def batch_delete(self, **kwargs):
        batch_size = kwargs.get('batch_size', 25)
        if not isinstance(kwargs['data'], list):
            raise BatchItemException('Batched data must be contained within a list')
        batched_data = (kwargs['data'][pos:pos + batch_size] for pos in range(0, len(kwargs['data']), batch_size))
        with self.table.batch_writer() as writer:
            for batch in batched_data:
                for item in batch:
                    writer.delete_item(Key=item)

    def update(self, **kwargs):
        original_data = self._get_original_data(**kwargs)
        merged_data = dict_merger.merge(original_data, kwargs['data'], **kwargs)
        updated_data = schema_mapper.map_to_schema(merged_data, self.model_schema_file, self.model_schema)
        self.table.put_item(Item=updated_data, ConditionExpression=Attr(
            self.model_version_key).eq(original_data[self.model_version_key]))
        super().publish('update', updated_data)
        return updated_data

    def _get_original_data(self, **kwargs):
        if kwargs['operation'] == 'get':
            original_data = self.get(**kwargs)
        else:
            original_data = self.query(**kwargs)[0]
        if not original_data:
            raise Exception('update: no data found to update')
        return original_data
