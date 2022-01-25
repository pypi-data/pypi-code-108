from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
import enum
import os

import boto3
from botocore.exceptions import NoRegionError

from api_machine import exc


class EnvEnum(int, enum.Enum):
    """ Where do we run this? """
    LOCAL = 1
    DOCKER = 2
    CLOUD = 3


ENV = getattr(
    EnvEnum, os.environ.get('DEPLOYMENT_ENV', 'CLOUD'), EnvEnum.CLOUD
)


@dataclass
class DynamoTable:
    """ Port to a dynamodb table """
    name: str
    pk: str
    sk: str
    dk: str
    schema: dict
    components: dict

    class Result:
        table: "DynamoTable"
        items: list
        objects: dict

        def __init__(self, table, objects):
            self.table = table
            self.objects = defaultdict(dict)
            self.items = []
            if len(self.table.components) == 0:
                for obj in objects:
                    self.items.append(
                        self._deserialize(
                            self.table.schema, obj
                        )
                    )
                return

            for obj in objects:
                pk = obj.get(self.table.pk)
                sk = obj.get(self.table.sk)
                self.objects[pk][sk] = obj
                if "#" in sk:
                    cm_ref, cm_key = sk.split("#")
                    if cm_ref not in self.objects[pk]:
                        self.objects[pk][cm_ref] = []
                    self.objects[pk][cm_ref].append(sk)
            for pk, objs in self.objects.items():
                self.items.append(
                    self._deserialize(self.table.schema, objs)
                )

        def _deserialize(self, value, context):
            if isinstance(value, dict):
                return {
                    field: self._deserialize(spec, context)
                    for field, spec
                    in value.items()
                }
            if isinstance(value, str):
                if value.endswith("[]"):
                    component = "".join(value[:-2])
                    return [
                        self._deserialize(
                            self.table.components[component], context.get(sk)
                        ) for sk in context.get(
                            component, []
                        )
                    ]
                field = value
                if "." in field:
                    sk, field = value.split(".")
                    context = context[sk]
                return context.get(field)

        def get_by_ref(self, ref):
            return self.objects[ref]

        def serialize(self, model=dict):
            return {
                "items": [
                    model(i) for i in self.items
                ],
            }

    def deserialize(self, items: list):
        """ Deserialize a repsonse from DynamoDB to structured data """
        items = [
            {k: deserializer.deserialize(v) for k, v in data.items()}
            for data in items
        ]
        return self.Result(
            table=self, objects=items
        )


try:
    boto3.resource('dynamodb')
    deserializer = boto3.dynamodb.types.TypeDeserializer()
    _serializer = boto3.dynamodb.types.TypeSerializer()

except NoRegionError:
    # Ignore, this happens because of imports
    # that don't acutally require this service
    pass


class Serializer:
    backend = _serializer.serialize

    def _parse(self, v):
        if isinstance(v, dict):
            return dict(
                (k, self._parse(v)) for k, v in v.items()
            )

        if isinstance(v, float):
            return Decimal(str(v))
        return v

    def serialize(self, v):
        v = self._parse(v)
        return self.backend(v)


serializer = Serializer()


def inject_assumed_role(cfg_key: str, params: dict):
    assume_role = os.environ.get(cfg_key)
    if not assume_role:
        return
    sts_client = boto3.client('sts')
    assumed_role_object = sts_client.assume_role(
        RoleArn=assume_role,
        RoleSessionName=f"AssumeRoleDynamoDB"
    )
    credentials = assumed_role_object['Credentials']
    injection = dict(
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'],
    )
    params.update(injection)


@dataclass
class DynamoRepository:
    """ Repository to a dynamodbTable """

    @dataclass
    class Config:
        source: DynamoTable
        mode: EnvEnum = ENV

    config: Config

    @property
    def client(self):
        params = {}
        inject_assumed_role("API_MACHINE_AWS_ASSUME_ROLE", params)
        if self.config.mode == EnvEnum.LOCAL:
            params['endpoint_url'] = 'http://localhost:8000/'
        if self.config.mode == EnvEnum.DOCKER:
            params['endpoint_url'] = 'http://dynamodb:8000/'
        return boto3.client('dynamodb', **params)

    def create_table(self):
        client = self.client
        client.create_table(
            TableName=self.config.source.name,
            AttributeDefinitions=[
                {
                    'AttributeName': key,
                    'AttributeType': 'S'
                } for key in [
                    self.config.source.pk,
                    self.config.source.sk,
                ]
            ],
            KeySchema=[
                {
                    'AttributeName': key[1],
                    'KeyType': key[0]
                } for key in [
                    ('HASH', self.config.source.pk),
                    ('RANGE', self.config.source.sk),
                ]
            ],
        )

    def all(self) -> DynamoTable.Result:
        client = self.client
        response = client.scan(
            TableName=self.config.source.name
        )
        return self.config.source.deserialize(response['Items'])

    def list(self, expr, **params) -> DynamoTable.Result:
        client = self.client
        params = {
            f':{k}': serializer.serialize(v) for k, v in params.items()
        }
        query_params = dict(
            TableName=self.config.source.name,
        )

        if expr:
            query_params.update(dict(
                KeyConditionExpression=expr,
                ExpressionAttributeValues=params,
            ))

        response = client.query(**query_params)
        items = response['Items']
        while 'LastEvaluatedKey' in response:
            response = client.query(
                ExclusiveStartKey=response['LastEvaluatedKey'],
                **query_params
            )
            items.extend(response['Items'])
        return self.config.source.deserialize(items)

    def insert(self, data):
        client = self.client
        _ = client.put_item(
            TableName=self.config.source.name,
            Item={
                v: serializer.serialize(data.get(k)) for k, v in
                self.config.source.schema.items()
            }
        )
        return data

    def get(self, key: dict):
        client = self.client
        response = client.get_item(
            TableName=self.config.source.name,
            Key={
                self.config.source.schema[k]: serializer.serialize(v) for
                k, v in key.items()
            }
        )
        try:
            item = response['Item']
        except KeyError:
            raise exc.ObjectNotFound(
                self.config.source.name, key
            )
        return self.config.source.deserialize([item]).items[0]

    def update(self, key, values):
        return self.insert(values)

    def batch_insert(self, data: list):
        """ Upserts a batch of item in a DynamoDB table """
        client = self.client
        chunk_size = 25
        for index in range(1, int(len(data)/chunk_size) + 2):
            start = (index * chunk_size) - chunk_size
            stop = min(len(data), start+chunk_size)
            batch = data[start:stop]

            # Base case for getting out of the for in case
            # batch length is equal to zero
            if len(batch) == 0:
                continue

            print(f"storing {len(batch)}")
            client.batch_write_item(
                RequestItems={
                    self.config.source.name: [{
                        'PutRequest': {
                            'Item': {
                                k: serializer.serialize(v) for k, v in item.items()
                            }
                        }
                    } for item in batch]
                }
            )
