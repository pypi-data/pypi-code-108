import boto3
from botocore.exceptions import ClientError


class DynamoTable:
    def __init__(self, name, region, endpoint=None):

        # Get a DynamoDB client to use for this region.
        dynamo = boto3.resource(
            'dynamodb',
            region_name=region,
            endpoint_url=endpoint
        )

        # Attempt to access the table.
        self._table = dynamo.Table(name)

    def get_item(self, key: {}):
        return self._table.get_item(Key=key)

    def query(self, expression):
        return self._table.query(KeyConditionExpression=expression)

    def batch_get_item(self, keys: []):
        try:
            return self._table.batch_get_item(
                Keys=keys
            )['Responses']
        except ClientError as e:
            print(e.response['Error']['Message'])

    def try_get_item(self, key: {}) -> {}:

        try:
            # Lookup the object.
            response = self.get_item(key=key)

            # Check if there is a response to return.
            if not response or 'Item' not in response or \
                    not response['Item']:
                return None
            else:
                return response['Item']
        except ClientError:
            return None

    def put_item(self, item: {}) -> {}:
        return self._table.put_item(Item=item)

    def delete_item(self, key: {}) -> {}:
        return self._table.delete_item(Key=key)
