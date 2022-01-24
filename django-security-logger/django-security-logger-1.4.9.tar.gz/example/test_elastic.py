from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3

host = 'vpc-mallpay-be-accept-fyaqep5vxdjqrkmrqbbem2nimq.eu-central-1.es.amazonaws.com'
region = 'eu-central-1'

service = 'es'
print('init boto 3')

credentials = boto3.Session().get_credentials()
print('boto')
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
search = Elasticsearch(
    hosts = [{'host': host, 'port': 443}],
    http_auth = awsauth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection
)
print(search)

document = {
    "title": "Moneyball",
    "director": "Bennett Miller",
    "year": "2011"
}

search.index(index="movies", doc_type="_doc", id="5", body=document)

print(search.get(index="movies", doc_type="_doc", id="5"))
