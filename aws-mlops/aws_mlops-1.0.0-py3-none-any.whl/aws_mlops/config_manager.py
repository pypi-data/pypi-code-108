"""The class for managing the states inputs and configuration and model.tar.gz files

The class needs the properties:
    'event' (dict): with ExecutionId and ExecutionName parameters [and last_output with other all parameters]

You can load it on a lambda and the handler is:
    aws_mlops/config_manager.main

# license MIT
# author Alessandra Bilardi <alessandra.bilardi@gmail.com>
# see https://github.com/bilardi/aws-mlops for details
"""
import boto3
import json
import os.path
from botocore.exceptions import ClientError

class ConfigManager():
    s3 = None
    ssm = None
    sfn = None
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.ssm = boto3.client('ssm')
        self.sfn = boto3.client('stepfunctions')

    def get_config_by_ssm(self, parameter_name):
        """
        gets the configuration saved on ssm
            Arguments:
                parameter_name (str): name of execution of state machine
            Returns:
                dictionary of config
        """
        try:
            details = self.ssm.get_parameter(Name=parameter_name)
        except ClientError:
            return {}
        return json.loads(details['Parameter']['Value'])

    def save_config_by_ssm(self, parameter_name, value):
        """
        saves the configuration merged with the last OutputPath
            Arguments:
                parameter_name (str): name of execution of state machine
                value (dict): dictionary of the configuration
        """
        return self.ssm.put_parameter(Name=parameter_name, Value=json.dumps(value), Type='String', Overwrite=True)

    def remove_config_by_ssm(self, parameter_name):
        """
        removes the configuration on ssm
            Arguments:
                parameter_name (str): name of execution of state machine
        """
        return self.ssm.delete_parameter(Name=parameter_name)

    def get_config_by_s3(self, bucket, key):
        """
        gets the configuration saved on s3
            Arguments:
                bucket (str): name of bucket
                key (str): path and filename
            Returns:
                dictionary of config
        """
        try:
            details = self.s3.get_object(Bucket=bucket, Key=key)
        except ClientError:
            return {}
        return json.loads(details['Body'].read())

    def save_config_by_s3(self, bucket, key, value):
        """
        saves the configuration merged with the last OutputPath
            Arguments:
                bucket (str): name of bucket
                key (str): path and filename
                value (dict): dictionary of the configuration
        """
        return self.s3.put_object(
            ACL='bucket-owner-full-control',
            Body=json.dumps(value).encode('ascii'), #b''
            Bucket=bucket,
            Key=key
        )

    def remove_config_by_s3(self, bucket, key):
        """
        removes the configuration on s3
            Arguments:
                bucket (str): name of bucket
                key (str): path and filename
        """
        return self.s3.delete_object(Bucket=bucket, Key=key)

    def get_config_by_sfn(self, execution_arn):
        """
        gets the configuration passed at the start the state machine
            Arguments:
                execution_arn (str): ARN of execution of state machine 
            Returns:
                dictionary of config
        """
        execution_details = self.sfn.describe_execution(executionArn=execution_arn)
        return json.loads(execution_details['input'])

    def get_details(self, event):
            """
            gets configuration
                Arguments:
                    event (dict): with ExecutionName parameter [and last_output with other all parameters]
                Returns:
                    list of parameter_name, bucket, key and dict of configuration
            """
            datetime = event['ExecutionName'].replace('-','/',3)
            parameter_name = '/' + datetime
            bucket = key = None
            if 'last_output' in event and 'source_bucket' in event['last_output']:
                bucket = event['last_output']['source_bucket']
            if 'last_output' in event and 'key' in event['last_output']:
                key = event['last_output']['key']
            if bucket is None or key is None:
                value = self.get_config_by_ssm(parameter_name)
                bucket = value['bucket']
                key = value['key']
            config = self.get_config_by_s3(bucket, f'{key}/config.json')
            if not config:
                print('get config by sfn')
                config = self.get_config_by_sfn(event['ExecutionId'])
            if not bucket:
                print('get bucket by sfn')
                bucket = config['source_bucket']
            if not key:
                print('get key by sfn')
                key = config['key']
            return [ parameter_name, bucket, key, config ]

    def save_details(self, parameter_name, bucket, key, config, event):
        """
        saves position and configuration
            Arguments:
                parameter_name (str): path of parameter stored on ssm
                bucket (str): bucket name
                key (str): path and filename where to save the dict of configuration
                config (dict): dict of configuration
                event (dict): dict of event
        """
        self.save_config_by_ssm(parameter_name, {"bucket":bucket, "key":key})
        self.save_config_by_ssm(config['execution_ssm'], json.dumps({"ExecutionId": event['ExecutionId'], "ExecutionName": event['ExecutionName']}))
        self.save_config_by_s3(bucket, f'{key}/config.json', config)

    def clean(self, parameter_name, bucket, key, config):
        """
        cleans parameter stored and moves files to save
            Arguments:
                parameter_name (str): path of parameter stored on ssm
                bucket (str): bucket name
                key (str): path and filename where to save the dict of configuration
                config (dict): dict of configuration
        """
        self.remove_config_by_ssm(parameter_name)
        # move configuration in config.key
        #if key contains the word mlops or modeling
        # move config.S3ModelArtifacts in config.key
        # and remove files in config.key/models
        #self.remove_config_by_s3(bucket, key)

    def update_model_input_id(self, config):
        """
        updates model input id from ssm
            Arguments:
                config (dict): dict of configuration
            Returns:
                dict of configuration
        """
        # the step function is named prediction, so the model_input_id can't be the same of turner_input_id
        if config['model_input_id'] == config['tuner_input_id'] and 'models_ssm' in config:
            model_input_id = self.get_config_by_ssm(config['models_ssm'])
            config['model_input_id'] = model_input_id
        return config

    def run(self, event):
        """
        manages the states inputs
            Arguments:
                event (dict): with ExecutionId and ExecutionName parameters [and last_output with other all parameters]
            Returns:
                dictionary with statusCode and body
        """
        [ parameter_name, bucket, key, config ] = self.get_details(event)
        if 'last_output' in event:
            config.update(event['last_output'])
            self.save_details(parameter_name, bucket, key, config, event)
        if 'StateName' in event:
            if event['StateName'] == 'GoToPreInference':
                config = self.update_model_input_id(config)
                self.save_details(parameter_name, bucket, key, config, event)
            if event['StateName'] == 'GoToEnd':
                self.clean(parameter_name, bucket, key, config)
        return config

def main(event, context = None):
    cm = ConfigManager()
    config = cm.run(event)
    return {
        'statusCode': 200,
        'body': config
    }
