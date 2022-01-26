import boto3


def check_dynamodb_table_connection(table_name: str) -> [bool, str]:
    dynamodb_client = boto3.client('dynamodb')
    error = ""

    try:
        dynamodb_client.describe_table(TableName=table_name)
        has_access = True
    except Exception as e:
        error = e
        has_access = False

    return has_access, error


def check_bucket_connection(bucket_name: str) -> [bool, str]:
    s3 = boto3.resource('s3')
    error = ""

    try:
        s3.meta.client.head_bucket(Bucket=bucket_name)
        has_access = True
    except Exception as e:
        error = e
        has_access = False

    return has_access, error


if __name__ == '__main__':
    check_dynamodb_table_connection("rastless")
    check_bucket_connection("rastless")