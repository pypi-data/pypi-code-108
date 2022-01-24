import unittest
import json
from aws_mlops.get_best_job import GetBestJob

class SmClient():
    dtj = None
    def __init__(self):
        with open('tests/sm-describe-trainig-job.json') as json_file:
            self.dtj = json.load(json_file)
    def describe_training_job(self, TrainingJobName = 'test'):
        if isinstance(TrainingJobName, str):
            return self.dtj

class TestGetBestJob(unittest.TestCase, GetBestJob):
    gbj = None
    si = None
    sm = None

    def __init__(self, *args, **kwargs):
        self.gbj = GetBestJob()
        self.gbj.sm = SmClient()
        with open('tests/sm-step-input.json') as json_file:
            self.si = json.load(json_file)
        unittest.TestCase.__init__(self, *args, **kwargs)
    
    def test_run(self):
        result = self.gbj.run(self.si)
        self.assertEqual(result['HyperParameter']['eval_metric'], 'rmse')
        self.assertEqual(result['test_input']['key'], 'value')
        self.assertEqual(result['TrainingJobName'], 'test')

if __name__ == '__main__':
    unittest.main()