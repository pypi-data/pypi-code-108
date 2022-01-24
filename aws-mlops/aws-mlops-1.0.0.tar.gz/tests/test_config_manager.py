import unittest
import json
from botocore.exceptions import ClientError
from aws_mlops.config_manager import ConfigManager

class S3Client():
    go = None
    po = None
    do = False
    goe = False
    poe = False
    doe = False
    def __init__(self):
        with open('tests/s3-get-object.json') as json_file:
            go = json.load(json_file)
            go['Body'] = StreamingBody(go['Body'])
            self.go = go
        with open('tests/s3-put-object.json') as json_file:
            self.po = json.load(json_file)
        with open('tests/s3-delete-object.json') as json_file:
            self.do = json.load(json_file)
    def get_object(self, Bucket, Key):
        if isinstance(Bucket, str) and isinstance(Key, str) and not self.goe:
            return self.go
        else:
            raise ClientError({'Error':{'Code':'NoSuchKey'}}, 'NoSuchKey')
    def put_object(self, ACL, Bucket, Key, Body):
        if isinstance(ACL, str) and isinstance(Bucket, str) and isinstance(Key, str) and isinstance(Body, bytes) and not self.poe:
            return self.po
        else:
            return {}
    def delete_object(self, Bucket, Key):
        if isinstance(Bucket, str) and isinstance(Key, str) and not self.doe:
            return self.do
        else:
            return {}        

class StreamingBody():
    body = None
    def __init__(self, body):
        self.body = body
    def read(self):
        return self.body

class SsmClient():
    gp = None
    pp = None
    dp = None
    gpe = False
    def __init__(self):
        with open('tests/ssm-get-parameter.json') as json_file:
            self.gp = json.load(json_file)
        with open('tests/ssm-put-parameter.json') as json_file:
            self.pp = json.load(json_file)
        with open('tests/ssm-delete-parameter.json') as json_file:
            self.dp = json.load(json_file)
    def get_parameter(self, Name = 'test'):
        if isinstance(Name, str) and not self.gpe:
            return self.gp
        else:
            raise ClientError({'Error':{'Code':'ParameterNotFound'}}, 'NotFound')
    def put_parameter(self, Name='test', Value='string', Type='String', Overwrite=True):
        if isinstance(Name, str) and isinstance(Value, str) and isinstance(Type, str) and isinstance(Overwrite, bool):
            return self.pp
    def delete_parameter(self, Name='test'):
        if isinstance(Name, str):
            return self.dp

class SfnClient():
    de = None
    def __init__(self):
        with open('tests/sfn-describe-execution.json') as json_file:
            self.de = json.load(json_file)
    def describe_execution(self, executionArn = 'test'):
        if isinstance(executionArn, str):
            return self.de

class TestManageConfig(unittest.TestCase, ConfigManager):
    cm = None
    event = None

    def __init__(self, *args, **kwargs):
        self.cm = ConfigManager()
        self.cm.s3 = S3Client()
        self.cm.ssm = SsmClient()
        self.cm.sfn = SfnClient()
        with open('tests/config.json') as json_file:
            self.event = json.load(json_file)
        unittest.TestCase.__init__(self, *args, **kwargs)

    def test_run(self):
        self.assertTrue('service' in self.event)
        self.assertFalse('ModelName' in self.event)

        self.cm.s3.goe = True
        result = self.cm.run(self.event)
        self.assertEqual(result['Parameter'], 'from-event') # get-event
        self.assertTrue('Model', result) # get-execution
        self.assertFalse('VersionId' in result) # get-s3

        self.cm.s3.goe = False
        result = self.cm.run(self.event)
        self.assertEqual(result['Parameter'], 'from-event') # get-event
        self.assertTrue('Model', result) # get-execution
        self.assertFalse('VersionId' in result) # get-s3

        del(self.event['last_output']['Parameter'])

        self.cm.s3.goe = True
        result = self.cm.run(self.event)
        self.assertEqual(result['Parameter'], 'Initial') # get-execution
        self.assertTrue('Model', result) # get-execution
        self.assertFalse('VersionId' in result) # get-s3

        self.cm.s3.goe = False
        result = self.cm.run(self.event)
        self.assertEqual(result['Parameter'], 'from-s3') # get-s3
        self.assertTrue('Model', result) # get-execution
        self.assertFalse('VersionId' in result) # get-s3

        self.event['StateName'] = 'GoToPreInference'
        self.cm.sfn.de['input'] = "{\"model_input_id\": \"samplekey\", \"tuner_input_id\": \"samplekey\", \"models_ssm\": \"/ssm/path/name\"}"

        self.cm.s3.goe = True
        result = self.cm.run(self.event)
        self.assertEqual(result['model_input_id'], {'bucket': 'your-bucket', 'key': 'your/key'}) # get-ssm

        result = self.cm.run({'ExecutionId': 'test-from-processing-id', 'ExecutionName': 'test-from-processing-name'})
        self.assertEqual(result['model_input_id'], 'samplekey') # get-description

        self.cm.sfn.de['input'] = "{\"model_input_id\": \"sample\", \"tuner_input_id\": \"samplekey\"}"

        result = self.cm.run(self.event)
        self.assertEqual(result['model_input_id'], 'sample') # get-event

        result = self.cm.run({'ExecutionId': 'test-from-processing-id', 'ExecutionName': 'test-from-processing-name'})
        self.assertEqual(result['model_input_id'], 'sample') # get-event

if __name__ == '__main__':
    unittest.main()