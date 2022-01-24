import tests.config as config

service = config.service
environment = config.environment

# input for preprocessing
# https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateProcessingJob.html
pretraining_input = {}
preinference_input = {}

# input for modeling
# https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateHyperParameterTuningJob.html
tuning_input = {}
# https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateTrainingJob.html
training_input = {}

# input for inference
# https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateModel.html
model_input = {
    'ExecutionRoleArn.$': '$.role_arn',
    'ModelName.$': '$.model_input_id',
    'PrimaryContainer': {
        'Environment': {},
        'Image.$': '$.container_image_uri',
        'ModelDataUrl.$': "$['S3ModelArtifacts']"
    }
}
# https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateTransformJob.html
testing_transformer_input = {}
prediction_transformer_input = {}

# input for reporting
# https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateProcessingJob.html
testing_input = {}
reporting_input = {}
