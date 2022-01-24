import os
import json
import boto3
from trell.utils import logger
from trell.exceptions import AwsConnectionError

# from trell.utils import LogFormatter
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
        print("----------- Connected to Trell AWS S via IAM role or AWS CLI configured credentials -----------------------")
    except Exception as err:
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name,
            aws_access_key_id=os.environ['ACCESS_KEY'],
            aws_secret_access_key=os.environ['SECRET_KEY']
        )
        response = client.get_secret_value(SecretId=secret_name)
        cred = json.loads(response['SecretString'])
        print("----------- Connected to Trell AWS via environment credentials -----------------------")

    
except Exception as err:
    print("** --- you are not authorized to use Trell pip package --- **")
    print("Follow one of the folling steps to use Trell pip package \n 1. Attach ds-general-ec2 IAM role to the machine  \n 2. Setup AWS CLI \n 3. manually set up the credentials via \n    from trell_ai_util.utils import Credential \n    Credential.set(ACCESS_KEY='*****', SECRET_KEY='*****') ")
    print(err)