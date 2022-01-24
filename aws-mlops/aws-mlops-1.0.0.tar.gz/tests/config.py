import os.path
import git
from datetime import datetime

import boto3
import sagemaker
if os.path.isdir('/Users') or os.path.isdir('/home/jovyan/'):
    boto3.setup_default_session(profile_name='your-account', region_name='eu-west-1')
else:
    boto3.setup_default_session()

def get_git_details():
    repo = git.Repo(search_parent_directories=True)
    return [ repo.active_branch.name, repo.head.object.hexsha ]
def create_ts():
    now = datetime.now()
    return now.strftime('%Y-%m-%d-%H-%M-%S')
def slash_to_dash(string):
    return string.replace('/','-')
def dictionary_from_module(module):
    context = {}
    black_list = ['os', 'git', 'datetime', 'boto3', 'sagemaker', 'get_git_details', 'create_ts', 'slash_to_dash', 'dictionary_from_module']
    for setting in dir(module):
        # you can write your filter here
        if not setting.startswith('_') and not setting in (black_list):
            context[setting] = getattr(module, setting)
    return context

# common input
service='mlops' # name of your service
environment='studio' # stanging / production
ecr_repository_name = f'{service}-{environment}-processing'
[ branch, commit ] = get_git_details()
ts = create_ts()

#source_bucket='your-bucket'
source_bucket = sagemaker.Session().default_bucket()
model_bucket=source_bucket # it is different, if you want to define an expiration date for old models
destination_bucket=source_bucket # it is different, if you want to define a trigger for your predictions / reports
key=f'{service}/{branch}/{commit}/{ts}' # for testing
#key=f'{service}/{branch}/{environment}/{commit}/{ts}' for CD
if os.environ.get('KEY'):
    key = os.environ.get('KEY')
dash_key=slash_to_dash(key)
test_key=key # it is different, if you want to try modeling without to run again pretraining
execution_ssm=f'/{key}/execution-details'

#model_input_id='sample'

# path of your data
raw_data_filename='winequality-red.csv'
raw_data_key=f'{service}/{branch}/raw_data' # for testing
#raw_data_key=f'{key}/raw_data' # for production
raw_data_s3_url=f's3://{source_bucket}/{raw_data_key}/{raw_data_filename}'

new_data_filename='winequality-white.csv'
new_data_key=f'{service}/{branch}/new_data' # for testing
#new_data_key=f'{key}/new_data' # for production
new_data_path=f's3://{source_bucket}/{new_data_key}'
new_data_s3_url=f'{new_data_path}/{new_data_filename}'

target='quality'
identifier='id'
score='score'
test_size=0.3
validation_size=0.2

test_filename='test.csv'
test_data_key=f'{test_key}/test_data'
testing_data_key=f'{test_key}/testing_data'
test_path=f's3://{source_bucket}/{test_data_key}'
test_s3_url=f'{test_path}/{test_filename}'

train_filename='train.csv'
train_path=f's3://{source_bucket}/{test_key}/train_data'
train_s3_url=f'{train_path}/{train_filename}'

validation_filename='validation.csv'
validation_data_key=f'{test_key}/validation_data'
validation_path=f's3://{source_bucket}/{validation_data_key}'
validation_s3_url=f'{validation_path}/{validation_filename}'

models_path=f's3://{model_bucket}/{key}/models'
models_ssm=f'/{service}/{branch}/model-input-id'

#score_filename='.csv.out'
score_path=f's3://{source_bucket}/{key}/prediction'
#score_s3_url=f'{score_path}/{score_filename}'

prediction_filename='prediction.csv'
# prediction_path=score_path
prediction_path=f's3://{destination_bucket}/{key}/prediction'
report_filename='report.csv'
report_path=prediction_path

# input for images and containers
container_input = {
    'framework':'xgboost',
    'version':'latest',
    'InstanceCount': 1,
    'InstanceType': 'ml.t3.large',
    'VolumeSizeInGB': 10
}

processing_input = {
    'InstanceCount': 1,
    'InstanceType': 'ml.t3.large',
    'VolumeSizeInGB': 10
}

# input for preprocessing
auto_input = {}
pretraining_input = {}
preinference_input = {}

# input for modeling
tuning_input = {}
training_input = {}

# input for inference
testing_transformer_input = {}
prediction_transformer_input = {}

# input for reporting
testing_input = {}
reporting_input = {}
