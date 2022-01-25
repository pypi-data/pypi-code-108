# -*- coding: future_fstrings -*-
import json
import os

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from sumoappclient.common.errors import InValidConfigException
from sumoappclient.configmanager.base import BaseConfigHandler


class AWSConfigHandler(BaseConfigHandler):
    DECRYPTION_TYPES = ["AwsSecretManager"]

    def setup(self, region_name, *args, **kwargs):
        my_config = Config(
            region_name=region_name,
            retries={
                'max_attempts': 10,
                'mode': 'standard'
            }
        )
        self.client = boto3.client('secretsmanager', config=my_config)

    def fetch_user_config(self):
        return self._override_section_config(os.environ)

    def decrypt(self, decrypt_type, key, value):
        if decrypt_type == "AwsSecretManager":
            decrypted_value = self.secret_manager(key, value)
        else:
            raise InValidConfigException(f"Invalid Decrypt type {decrypt_type} for AWS Environment. "
                                         f"Make sure it is one of value {self.DECRYPTION_TYPES}")
        return decrypted_value

    def secret_manager(self, key, value):
        try:
            get_secret_value_response = self.client.get_secret_value(
                SecretId=value
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'DecryptionFailureException':
                # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response['Error']['Code'] == 'InternalServiceErrorException':
                # An error occurred on the server side.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response['Error']['Code'] == 'InvalidParameterException':
                # You provided an invalid value for a parameter.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response['Error']['Code'] == 'InvalidRequestException':
                # You provided a parameter value that is not valid for the current state of the resource.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response['Error']['Code'] == 'ResourceNotFoundException':
                # We can't find the resource that you asked for.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
        else:
            # Decrypts secret using the associated KMS CMK.
            # Depending on whether the secret is a string or binary, one of these fields will be populated.
            if 'SecretString' in get_secret_value_response:
                secret = get_secret_value_response['SecretString']
                secret = json.loads(secret)
                if key in secret:
                    return secret[key]
                else:
                    raise InValidConfigException(f"{key} not present in the provided Secret manager ARN {value}.")
        return value
