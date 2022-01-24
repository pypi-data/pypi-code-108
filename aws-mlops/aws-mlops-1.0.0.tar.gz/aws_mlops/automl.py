"""The class for managing your Auto ML jobs

The class accepts one property:
    'config' (module): configuration module

These properties are mandatory. Here's an example:

    >>> import config as config
    >>> from aws_mlops.automl import AutoML
    >>> am = AutoML(config)
    >>> am.run()
    >>> am.status()
    >>> am.best_candidate()

# license MIT
# author Alessandra Bilardi <alessandra.bilardi@gmail.com>
# see https://github.com/bilardi/aws-mlops for details
"""
import boto3
import sagemaker
from .mlops import MLOps
# https://docs.aws.amazon.com/sagemaker/latest/dg/autopilot-automate-model-development-container-output.html#autopilot-classification-container-inference-response
# https://sagemaker-examples.readthedocs.io/en/latest/autopilot/autopilot_customer_churn.html
class AutoML():
    config = None
    mo = None
    role = None
    session = None
    bucket = None
    region = None
    def __init__(self, config):
        self.config = config
        self.mo = MLOps(config)
        self.role = self.mo.get_role_arn('auto_input')
        self.session = sagemaker.Session()
        self.bucket = self.session.default_bucket()
        self.region = boto3.Session().region_name

    def create_job(self, config):
        """
        """
        # https://sagemaker.readthedocs.io/en/stable/api/training/automl.html
        return AutoML(
            role = self.role,
            sagemaker_session = self.session,
            target_attribute_name = config.target,
            problem_type='Regression', 
            job_objective={'MetricName': 'MSE'},
            output_path = f's3://{self.bucket}/{config.key}/auto',
            max_runtime_per_training_job_in_seconds = 300,
            max_candidates = 10,
            total_job_runtime_in_seconds = 5000
        )

    def get_notebooks_links(self, job_name):
        """
        """
        job = self.create_job()
        details = job.describe_auto_ml_job(job_name=job_name)
        return {
            'candidate': details['AutoMLJobArtifacts']['CandidateDefinitionNotebookLocation'],
            'data': details['AutoMLJobArtifacts']['DataExplorationNotebookLocation']
        }

    def best_candidate(self, job_name):
        """
        """
        job = self.create_job()
        job.best_candidate(job_name=job_name)

    def status(self, job_name):
        """
        """
        job = self.create_job()
        details = job.describe_auto_ml_job(job_name=job_name)
        return details['AutoMLJobStatus']

    def run(self, config):
        """
        """
        job = self.create_job
        job.fit(inputs=config.train_s3_url, logs=False, wait=False)
        return job.describe_auto_ml_job()
