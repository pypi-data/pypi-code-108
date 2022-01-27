from syngenta_digital_dta.dynamodb.adapter import DynamodbAdapter
from syngenta_digital_dta.postgres.adapter import PostgresAdapter
from syngenta_digital_dta.elasticsearch.adapter import ElasticsearchAdapter
from syngenta_digital_dta.s3.adapter import S3Adapter


def adapter(**kwargs):
    if kwargs.get('engine') == 'dynamodb':
        return DynamodbAdapter(**kwargs)
    if kwargs.get('engine') == 'redshift':
        return PostgresAdapter(**kwargs)
    if kwargs.get('engine') == 'postgres':
        return PostgresAdapter(**kwargs)
    if kwargs.get('engine') == 'elasticsearch':
        return ElasticsearchAdapter(**kwargs)
    if kwargs.get('engine') == 's3':
        return S3Adapter(**kwargs)
    raise Exception(
        f'engine {kwargs.get("engine", "was not supplied, an empty engine kwarg is")} not supported; contribute to get it supported :)')
