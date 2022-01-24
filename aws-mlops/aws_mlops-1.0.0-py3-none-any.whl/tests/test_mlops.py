import unittest
import os
import json
import tests.config as config
import tests.definitions as definitions
from aws_mlops.mlops import MLOps

class EcrClient():
    di = None
    def __init__(self):
        with open('tests/ecr-describe-images.json') as json_file:
            self.di = json.load(json_file)
    def describe_images(self, repositoryName):
        if isinstance(repositoryName, str):
            return self.di

class SfnClient():
    dsm = None
    se_details = None
    dsm_details = None
    def __init__(self):
        with open('tests/sfn-describe-state-machine.json') as json_file:
            self.dsm = json.load(json_file)
    def start_execution(self, stateMachineArn: str, name: str, input: str):
        self.se_details = [stateMachineArn, name, input]
        return {}
    def describe_state_machine(self, stateMachineArn: str):
        self.dsm_details = stateMachineArn
        return self.dsm

class StsClient():
    def get_caller_identity(self):
        return {'Account': '1234567890'}

class TestMLOps(unittest.TestCase, MLOps):
    mo = None

    def __init__(self, *args, **kwargs):
        self.mo = MLOps(config)
        self.mo.ecr = EcrClient()
        self.mo.sfn = SfnClient()
        self.mo.sts = StsClient()
        self.mo.role = 'arn'
        self.tmp = os.path.dirname(os.path.realpath(__file__))
        unittest.TestCase.__init__(self, *args, **kwargs)
    
    def test_get_image_uri(self):
        self.assertEqual(self.mo.get_image_uri(config), 'your-account-id.dkr.ecr.eu-west-1.amazonaws.com/mlops-studio-processing:b8da9086')

    def test_get_role_arn(self):
        self.assertEqual(self.mo.get_role_arn('pretraining_input', config), 'arn:role:string')
        state_machine_arn = self.mo.sfn.dsm_details
        self.assertIn('arn:aws:states:', state_machine_arn)
        self.assertIn(':stateMachine:mlops-studio-processing', state_machine_arn)

    def test_create_step_functions_definition_files(self):
        self.mo.create_step_functions_definition_files(definitions)
#        result = filecmp.cmp('studio.pretraining.definition.json', 'tests/studio.pretraining.definition.json')
#        self.assertTrue(result)
#        result = filecmp.cmp('studio.modeling.definition.json', 'tests/studio.modeling.definition.json')
#        self.assertTrue(result)
#        result = filecmp.cmp('studio.prediction.definition.json', 'tests/studio.prediction.definition.json')
#        self.assertTrue(result)
#        result = filecmp.cmp('studio.mlops.definition.json', 'tests/studio.mlops.definition.json')
#        self.assertTrue(result)

    def test_run_state_machine(self):
        [response, response_name, response_input] = self.mo.run_state_machine('pretraining')
        [stateMachineArn, name, input] = self.mo.sfn.se_details
        self.assertEqual(response, {})
        self.assertIn(response_name, 'pretraining')
        self.assertRegex(name, r'^[0-9A-Za-z-]+$')
        self.assertEqual(response_input, input)
        obj = json.loads(input)
        self.assertEqual(len(list(obj.keys())), 66)
        self.assertIn('arn:aws:states:', stateMachineArn)
        self.assertIn(':stateMachine:mlops-studio-processing', stateMachineArn)

        [response, response_name, response_input] = self.mo.run_state_machine('modeling')
        [stateMachineArn, name, input] = self.mo.sfn.se_details
        self.assertEqual(response, {})
        self.assertIn(response_name, 'modeling')
        self.assertRegex(name, r'^[0-9A-Za-z-]+$')
        self.assertEqual(response_input, input)
        obj = json.loads(input)
        self.assertEqual(len(list(obj.keys())), 66)
        self.assertIn('arn:aws:states:', stateMachineArn)
        self.assertIn(':stateMachine:mlops-studio-modeling', stateMachineArn)

if __name__ == '__main__':
    unittest.main()