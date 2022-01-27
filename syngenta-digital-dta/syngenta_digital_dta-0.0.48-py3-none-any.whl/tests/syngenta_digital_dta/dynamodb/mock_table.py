import boto3

class MockTable():

    def __init__(self, **kwargs):
        self.table_name = kwargs['table_name']
        self.client = boto3.client('dynamodb', endpoint_url='http://localhost:4000')
        self.mock_data = {
            'test_id': 'abc123',
            'test_query_id': 'def345',
            'object_key': {
                'string_key': 'nothing'
            },
            'array_number': [1, 2, 3],
            'array_objects': [
                {
                    'array_string_key': 'a',
                    'array_number_key': 1
                }
            ],
            'created': '2020-10-05',
            'modified': '2020-10-05'
        }

    def setup_test_table(self):
        self.clear_table()
        self.create_table()
        self.seed_table()

    def clear_table(self):
        try:
            self.client.delete_table(TableName=self.table_name)
        except Exception as e:
            print('delete table error, table doesnt exists; error: {}'.format(e))

    def create_table(self, ):
        self.client.create_table(
            TableName=self.table_name,
            BillingMode= 'PAY_PER_REQUEST',
            AttributeDefinitions=[
                {
                    'AttributeName': 'test_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'test_query_id',
                    'AttributeType': 'S'
                }
            ],
            KeySchema=[
                {
                    'AttributeName': 'test_id',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'test_query_id',
                    'KeyType': 'RANGE'
                }
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'test_query_id',
                    'KeySchema': [
                        {
                            'AttributeName': 'test_query_id',
                            'KeyType': 'HASH'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                }
            ]
        )

    def seed_table(self):
        client = boto3.resource('dynamodb', endpoint_url='http://localhost:4000').Table(self.table_name)
        client.put_item(
            Item=self.mock_data
        )
