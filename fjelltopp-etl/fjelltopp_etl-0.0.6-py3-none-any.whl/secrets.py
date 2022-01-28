import base64

import boto3
import os
import json
from botocore.exceptions import ClientError


class SecretsError(Exception):
    pass


def get_secret(name: str, source: str="envrionment") -> dict:
    if source == "environment":
        secret = os.environ.get(name, None)
        if secret is None:
            raise ValueError("No such secret in the envrionment")
    elif source == "ssm":
        client = boto3.client("secretsmanager")
        try:
            get_secret_value_response = client.get_secret_value(
                SecretId=name
            )
        except ClientError as e:
            raise SecretsError(f"Failed to get secret form SecretManager with error code {e.response.get('Error',{}).get('Code')}")
        if 'SecretString' in get_secret_value_response:
            secret = json.loads(get_secret_value_response['SecretString'])
        else:
            secret = json.loads(base64.b64decode(get_secret_value_response['SecretBinary']))
            
    else:
        raise NotImplementedError(f"{source} is not a supported source")
    return secret

    
