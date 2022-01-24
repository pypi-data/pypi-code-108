import os
import json
import boto3
import logging

# from trell_ai_util.utils import LogFormatter
# LogFormatter.apply()

try:
    secret_name = "data-secret"
    region_name = "ap-south-1"
    session = boto3.session.Session()
    try:
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )
        response = client.get_secret_value(SecretId=secret_name)
        cred = json.loads(response['SecretString'])
        print("----------- Connected to AWS via IAM role or AWS CLI configured credentials -----------------------")
    except Exception as err:
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name,
            aws_access_key_id=os.environ['ACCESS_KEY'],
            aws_secret_access_key=os.environ['SECRET_KEY']
        )
        response = client.get_secret_value(SecretId=secret_name)
        cred = json.loads(response['SecretString'])
        print("----------- Connected to AWS via environment credentials -----------------------")

    
except Exception as err:
    print("* you are not authorized to use Trell pip package *")
    print("** Either setup AWS CLI or use EC2 machine with proper IAM roles attached **")
    print(err)
