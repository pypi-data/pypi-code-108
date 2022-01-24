"""The class for managing your MLOps cycle by Sagemaker services with Step Functions

The class accepts one property:
    'config' (module): configuration module

These properties are mandatory. Here's an example:

    >>> import config as config
    >>> import definitions as definitions
    >>> from aws_mlops.mlops import MLOps
    >>> mo = MLOps(config)
    >>> mo.create_step_functions_definition_files(definitions)
    >>> mo.run_state_machine('pretraining')
    >>> mo.run_state_machine('modeling')
    >>> mo.run_state_machine('prediction')
    >>> mo.run_state_machine('mlops')

# license MIT
# author Alessandra Bilardi <alessandra.bilardi@gmail.com>
# see https://github.com/bilardi/aws-mlops for details
"""
import json
import boto3
import sagemaker
from datetime import datetime
from .data_storage import DataStorage
class MLOps():
    config = None
    ecr = None
    sfn = None
    sts = None
    ds = None
    region = None
    def __init__(self, config):
        self.config = config
        self.ecr = boto3.client('ecr')
        self.sfn = boto3.client('stepfunctions')
        self.sts = boto3.client('sts')
        self.ds = DataStorage()
        self.region = boto3.Session().region_name

    def get_state_machine_suffix(self, name):
        """
        gets the suffix of state machine
            Arguments:
                name (str): name of state
            Returns:
                name of state machine
        """
        return 'processing' if name in ['pretraining', 'preinference', 'testing', 'reporting'] else name
    def calc_state_machine_arn(self, name, config):
        """
        calculates state machine ARN
            Arguments:
                name (str): name of state machine
                config (module): configuration module
            Returns:
                string of state machine ARN
        """
        # https://github.com/boto/boto3/issues/454
        account_id = self.sts.get_caller_identity()['Account']
        suffix = self.get_state_machine_suffix(name)
        return f'arn:aws:states:{self.region}:{account_id}:stateMachine:{config.service}-{config.environment}-{suffix}'
    def create_unique_identificator(self, name, config):
        """
        creates an unique identificator with 0-9, A-Z, a-z, - and _
        name must be unique for your AWS account, region, and state machine for 90 days
            Arguments:
                name (str): name of state machine
                config (module): configuration module
            Returns:
                string
        """
        identificator = f'{config.service}-{config.environment}-{name}-{datetime.now().isoformat(timespec="microseconds").replace(":","-").replace(".","")}'
        return identificator
    def get_last_image(self, images, property):
        """
        gets the last item sorting by property
            Arguments:
                images (list): list of dictionaries
                property (str): name of property contained in each item
            Returns:
                dictionary
        """
        images_sorted = sorted(images['imageDetails'], key=lambda k: k[property])
        return images_sorted[-1]
    def get_image_uri(self, config):
        """
        gets last image URI deployed
            Returns:
                last image URI
        """
        images = self.ecr.describe_images(repositoryName = config.ecr_repository_name)
        details = self.get_last_image(images, 'imagePushedAt')
        return '{}.dkr.ecr.{}.amazonaws.com/{}:{}'.format(
            details['registryId'], 
            self.region, 
            config.ecr_repository_name, 
            details['imageTags'][0]
        )
    def get_container_uri(self, name, config):
        """
        creates link to a docker container with a specific framework and version
            Arguments:
                container_input (dict): dictionary of all properties to configure an object of type sagemaker.image_uris.retrieve
            Returns:
                container
        """
        input = getattr(config, name)
        # https://sagemaker.readthedocs.io/en/stable/api/utility/image_uris.html
        container = sagemaker.image_uris.retrieve(
            input['framework'],
            self.region,    
            input['version'])
        return container
    def get_role_arn(self, name, config):
        """
        gets role ARN of that state machine
            Arguments:
                name (str): name of parameter in config module
                config (module): configuration module
            Returns:
                string of role ARN
        """
        state_machine_arn = self.calc_state_machine_arn(name.replace("_input",""), config)
        state_machine_details = self.sfn.describe_state_machine(stateMachineArn=state_machine_arn)
        return state_machine_details['roleArn']
    def get_catch(self):
        """
        gets the catch for failure state
            Returns:
                list of dictionaries
        """
        return [{
            'ErrorEquals': [
                'States.TaskFailed'
            ],
            'Next': 'Failure'
        }]
    def create_failure_definition(self):
        """
        creates Failure definition
            Returns:
                Failure definition
        """
        return {
            'Cause': 'SageMakerProcessingJobFailed',
            'Type': 'Fail'
        }

    def create_processing_definition(self, name, config, next_step = 'Tuning'):
        """
        creates the ProcessingJob
            Arguments:
                name (str): name of parameter in config module
                config (module): configuration module
                next_step (str): name of the next step
            Returns:
                ProcessingJob definition
        """
        parameter = 'Next' if next_step != 'End' else 'End'
        value = next_step if next_step != 'End' else True

        # https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateProcessingJob.html
        return {'Type': 'Task', 'Resource': 'arn:aws:states:::sagemaker:createProcessingJob.sync',
            parameter: value,
            'Catch': self.get_catch(),
            'Parameters': getattr(config, name)
        }
    def create_manage_config_definition(self, next_step, config):
        """
        creates the lambda invoke definition
            Arguments:
                next_step (str): name of the next step
                config (module): configuration module
            Returns:
                lambda invoke definition
        """
        parameter = 'Next' if next_step != 'End' else 'End'
        value = next_step if next_step != 'End' else True

        return {
            'Type': 'Task',
            'Resource': "arn:aws:states:::lambda:invoke",
            parameter: value,
            'Catch': self.get_catch(),
            'Parameters': {
                'FunctionName': f'{config.service}-{config.environment}-config-manager',
                'Payload': {
                    'last_output.$': '$',
                    'ExecutionId.$': '$$.Execution.Id',
                    'ExecutionName.$': '$$.Execution.Name',
                    'StateName.$': '$$.State.Name'
                }
            },
            'OutputPath': '$.Payload.body'
        }
    def create_tuning_definition(self, config, next_step = 'GetBestTrainingJob'):
        """
        creates the TuningJob
            Arguments:
                config (module): configuration module
                next_step (str): name of the next step
            Returns:
                TuningJob definition
        """
        parameter = 'Next' if next_step != 'End' else 'End'
        value = next_step if next_step != 'End' else True

        # https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateHyperParameterTuningJob.html
        return {'Type': 'Task', 'Resource': 'arn:aws:states:::sagemaker:createHyperParameterTuningJob.sync',
            parameter: value,
            'Catch': self.get_catch(),
            'Parameters': getattr(config, 'tuning_input')
        }
    def create_get_best_training_job_definition(self, config):
        """
        creates the lambda invoke definition
            Arguments:
                config (module): configuration module
            Returns:
                lambda invoke definition
        """
        return {
            'Type': 'Task',
            'Resource': "arn:aws:states:::lambda:invoke",
            'Next': 'GoToModel',
            'Catch': self.get_catch(),
            'Parameters': {
                'FunctionName': f'{config.service}-{config.environment}-get-best-training-job-details',
                'Payload': {
                    'TrainingJobName.$': '$.BestTrainingJob.TrainingJobName'
                }
            },
            'OutputPath': '$.Payload.body'
        }
    def create_model_definition(self, config):
        """
        creates the CreateModel
            Arguments:
                config (module): configuration module
            Returns:
                CreateModel definition
        """
        # https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateModel.html
        return {'Type': 'Task', 'Resource': 'arn:aws:states:::sagemaker:createModel',
            'Next': 'GoToTransform', 
            'Catch': self.get_catch(),
            'Parameters': getattr(config, 'model_input')
        }
    def create_generic_definition(self, name, config, next_step, resource):
        """
        creates a generic definition
            Arguments:
                name (str): name of parameter in config module
                config (module): configuration module
                next_step (str): name of the next step
                resource (str): name of sagemaker resource
            Returns:
                Generic definition
        """
        return {'Type': 'Task', 'Resource': f'arn:aws:states:::sagemaker:{resource}',
            'Next': next_step, 
            'Catch': self.get_catch(),
            'Parameters': getattr(config, name)
        }
    def create_transform_definition(self, name, config, next_step = 'GoToTesting'):
        """
        creates the TransformJob
            Arguments:
                name (str): 
                config (module): configuration module
                next_step (str): name of the next step
            Returns:
                TransformJob definition
        """
        parameter = 'Next' if next_step != 'End' else 'End'
        value = next_step if next_step != 'End' else True

        # https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateTransformJob.html
        return {'Type': 'Task', 'Resource': 'arn:aws:states:::sagemaker:createTransformJob.sync',
            parameter: value,
            'Catch': self.get_catch(),
            'Parameters': getattr(config, name)
        }
    def create_endpoint_choice_definition(self, config):
        """
        creates a choice definition
            Arguments:
                config (module): configuration module
            Returns:
                Choice definition
        """
        return {'Type': 'Choice',
            'Choices': [
                    {
                        'Variable': '$.endpoint_exists',
                        'NumericEquals': 0,
                        'Next': 'GoToCreateEndpoint'
                    }
            ],
            'Default': 'GoToUpdateEndpoint'
        }

    def create_step_functions_processing_definition(self, name, config):
        """
        creates step functions definition
            Arguments:
                name (str): name of parameter in config module
                config (module): configuration module
            Returns:
                state machine definition
        """
        definition = {'Comment':'MLOps state machine processing', 'StartAt': 'Processing',
            'States': {
                'Processing': self.create_processing_definition(name, config, 'End'),
                'Failure': self.create_failure_definition()
            }
        }
        return definition
    def create_step_functions_modeling_definition(self, name, config):
        """
        creates step functions definition
            Arguments:
                config (module): configuration module
            Returns:
                state machine definition
        """
        # https://docs.aws.amazon.com/step-functions/latest/dg/connect-sagemaker.html
        definition = {'Comment':'MLOps state machine', 'StartAt': 'GoToTuning',
            'States': {
                'GoToTuning': self.create_manage_config_definition('Tuning', config),
                'Tuning': self.create_tuning_definition(config),
                'GetBestTrainingJob': self.create_get_best_training_job_definition(config),
                'GoToModel': self.create_manage_config_definition('CreateModel', config),
                'CreateModel': self.create_model_definition(config),
                'GoToTransform': self.create_manage_config_definition('Transform', config),
                'Transform': self.create_transform_definition('testing_transformer_input', config, 'GoToTesting'),
                'GoToTesting': self.create_manage_config_definition('Testing', config),
                'Testing': self.create_processing_definition('testing_input', config, 'GoToEnd'),
                'GoToEnd': self.create_manage_config_definition('End', config),
                'Failure': self.create_failure_definition()
            }
        }
        return definition
    def create_step_functions_prediction_definition(self, name, config):
        """
        creates step functions definition
            Arguments:
                name (str): name of parameter in config module
                config (module): configuration module
            Returns:
                state machine definition
        """
        # https://docs.aws.amazon.com/step-functions/latest/dg/connect-sagemaker.html
        definition = {'Comment':'MLOps state machine', 'StartAt': 'GoToPreInference',
            'States': {
                'GoToPreInference': self.create_manage_config_definition('PreInference', config),
                'PreInference': self.create_processing_definition('preinference_input', config, 'GoToTransform'),
                'GoToTransform': self.create_manage_config_definition('Transform', config),
                'Transform': self.create_transform_definition('prediction_transformer_input', config, 'GoToReporting'),
                'GoToReporting': self.create_manage_config_definition('Reporting', config),
                'Reporting': self.create_processing_definition(name, config, 'GoToEnd'),
                'GoToEnd': self.create_manage_config_definition('End', config),
                'Failure': self.create_failure_definition()
            }
        }
        return definition
    def create_step_functions_endpoint_definition(self, config):
        """
        creates step functions definition
            Arguments:
                config (module): configuration module
            Returns:
                state machine definition
        """
        # https://docs.aws.amazon.com/step-functions/latest/dg/connect-stepfunctions.html
        definition = {'Comment':'MLOps state machine', 'StartAt': 'GoToEndpointConfig',
            'States': {
                'GoToEndpointConfig': self.create_manage_config_definition('EndpointConfig', config),
                'EndpointConfig': self.create_generic_definition('endpoint_config_input', config, 'EndpointChoice', 'createEndpointConfig'),
                'EndpointChoice': self.create_endpoint_choice_definition(config),
                'GoToCreateEndpoint': self.create_manage_config_definition('CreateEndpoint', config),
                'CreateEndpoint': self.create_generic_definition('endpoint_input', config, 'GoToEnd', 'createEndpoint'),
                'GoToUpdateEndpoint': self.create_manage_config_definition('UpdateEndpoint', config),
                'UpdateEndpoint': self.create_generic_definition('endpoint_input', config, 'GoToEnd', 'updateEndpoint'),
                'GoToEnd': self.create_manage_config_definition('End', config),
                'Failure': self.create_failure_definition()
            }
        }
        return definition
    def create_step_functions_mlops_definition(self, config):
        """
        creates step functions definition
            Arguments:
                config (module): configuration module
            Returns:
                state machine definition
        """
        # https://docs.aws.amazon.com/step-functions/latest/dg/connect-stepfunctions.html
        definition = {'Comment':'MLOps state machine', 'StartAt': 'GoToPreTraining',
            'States': {
                'GoToPreTraining': self.create_manage_config_definition('PreTraining', config),
                'PreTraining': self.create_processing_definition('pretraining_input', config, 'GoToTuning'),
                'GoToTuning': self.create_manage_config_definition('Tuning', config),
                'Tuning': self.create_tuning_definition(config),
                'GetBestTrainingJob': self.create_get_best_training_job_definition(config),
                'GoToModel': self.create_manage_config_definition('CreateModel', config),
                'CreateModel': self.create_model_definition(config),
                'GoToTransform': self.create_manage_config_definition('Transform', config),
                'Transform': self.create_transform_definition('testing_transformer_input', config, 'GoToTesting'),
                'GoToTesting': self.create_manage_config_definition('Testing', config),
                'Testing': self.create_processing_definition('testing_input', config, 'GoToEnd'),
                'GoToEnd': self.create_manage_config_definition('End', config),
                'Failure': self.create_failure_definition()
            }
        }
        return definition
    def create_step_functions_definition_files(self, config = None):
        """
        creates Step Function definition files
            Arguments:
                config (module): configuration module
        """
        if config is None:
            config = self.config
        definitions = {}
        definitions['pretraining'] = self.create_step_functions_processing_definition('pretraining_input', config)
        definitions['preinference'] = self.create_step_functions_processing_definition('preinference_input', config)
        definitions['testing'] = self.create_step_functions_processing_definition('testing_input', config)
        definitions['reporting'] = self.create_step_functions_processing_definition('reporting_input', config)
        definitions['modeling'] = self.create_step_functions_modeling_definition('tuning_input', config)
        definitions['prediction'] = self.create_step_functions_prediction_definition('reporting_input', config)
        #definitions['endpoint'] = self.create_step_functions_endpoint_definition(config)
        definitions['mlops'] = self.create_step_functions_mlops_definition(config)
        for definition in definitions.keys():
            with open(f'{config.environment}.{definition}.definition.json', 'w') as fh:
                json.dump(definitions[definition], fh)

    def create_step_function_input(self, config):
        """
        creates Step Function input
            Arguments:
                config (module): configuration module
            Returns:
                json string
        """
        input = {}
        identificator = self.create_unique_identificator('xxxxx', config)
        short_identificator = identificator.replace('xxxxx', '').replace('-', '')[:31]
        if not hasattr(config, 'model_input_id'):
            input['model_input_id'] = short_identificator
        if not hasattr(config, 'role_arn'):
            input['role_arn'] = self.get_role_arn('processing', config)
        if not hasattr(config, 'processing_image_uri'):
            input['processing_image_uri'] = self.get_image_uri(config)
        if not hasattr(config, 'container_image_uri'):
            input['container_image_uri'] = self.get_container_uri('container_input', config)

        input['pretraining_input_id'] = identificator.replace('xxxxx', 'pretraining')
        input['preinference_input_id'] = identificator.replace('xxxxx', 'preinference')
        input['tuner_input_id'] = short_identificator
        input['testing_transformer_input_id'] = identificator.replace('xxxxx', 'testing')
        input['prediction_transformer_input_id'] = identificator.replace('xxxxx', 'prediction')
        input['testing_input_id'] = identificator.replace('xxxxx', 'testing')
        input['reporting_input_id'] = identificator.replace('xxxxx', 'reporting')

        config_dict = config.dictionary_from_module(config)
        input.update(config_dict)
        return json.dumps(input)
    def run_state_machine(self, name = 'pretraining', config = None):
        """
        run state machine
            Arguments:
                name (str): name of state
                config (module): configuration module
        """
        if config is None:
            config = self.config
        input = self.create_step_function_input(config)
        return [self.sfn.start_execution(
            stateMachineArn=self.calc_state_machine_arn(name, config),
            name=self.create_unique_identificator(name, config),
            input=input
        ), name, input]
