import sys
from botocore.config import Config

from awsservicespkg.utils import constants, utilities


class CloudFormationService:

    # Instantiate cloud formation service
    def __init__(self, logger, session, region, customer_id, environment_type):
        try:
            cfn = session.resource('cloudformation', region_name=region, config=Config(retries=dict(max_attempts=3)))
            self.logger = logger
            self.cfnresource = cfn
            self.customer_id = customer_id
            self.environment_type = environment_type
            self.region = region
            self.logger.info("Cloudformation service initialized")
        except Exception as e:
            logger.exception(e)
            print(
                "Error while initializing cloudformation resource. Please refer to the log file at- " + constants.logger_path)
            sys.exit(1)

    def get_cloud_formation_stack(self, stack_name):
        try:
            stack = self.cfnresource.Stack(stack_name)
            return stack
        except Exception as err:
            self.logger.exception(err)
            print("Error while getting cloudformation stack. Please refer to the log file at- " + constants.logger_path)
            sys.exit(1)

    def get_a_stack_output_value(self, stack_name, output_key):
        stack = self.get_cloud_formation_stack(stack_name)
        stack_output = stack.outputs
        output_value = ''
        for item in stack_output:
            if item['OutputKey'] == output_key:
                output_value = item['OutputValue']
                break
        return output_value

    def get_phz_id(self):
        stack_name = utilities.get_stack_name(self.customer_id, self.environment_type, 'PrivateHostedZone')
        a_value = self.get_a_stack_output_value(stack_name, 'PrivateHostedZoneId')
        self.logger.info('PrivateHostedZoneId for {} stack is {}'.format(stack_name, a_value))
        return a_value

    def get_efs_id(self):
        stack_name = utilities.get_stack_name(self.customer_id, self.environment_type, 'EFS')
        a_value = self.get_a_stack_output_value(stack_name, 'FileSystemDNS')
        self.logger.info('FileSystemDNS for {} stack is {}'.format(stack_name, a_value))
        return a_value

    def get_efs_filesystem_id(self):
        stack_name = utilities.get_stack_name(self.customer_id, self.environment_type, 'EFS')
        a_value = self.get_a_stack_output_value(stack_name, 'FileSystemForVolume')
        self.logger.info('FileSystemForVolume for {} stack is {}'.format(stack_name, a_value))
        return a_value

    def get_rds_id(self):
        stack_name = utilities.get_stack_name(self.customer_id, self.environment_type, 'RDSAurora')
        a_value = self.get_a_stack_output_value(stack_name, 'RDSEndpointAddressId')
        self.logger.info('RDSEndpointAddressId for {} stack is {}'.format(stack_name, a_value))
        return a_value

    def get_sns_topic_arn(self):
        stack_name = utilities.get_stack_name(self.customer_id, self.environment_type, 'SNS')
        a_value = self.get_a_stack_output_value(stack_name, 'SNSTopicARN')
        self.logger.info('SNSTopicARN for {} stack is {}'.format(stack_name, a_value))
        return a_value

    def get_efs_arn(self, account_id):
        arn = utilities.create_arn(service='elasticfilesystem', region=self.region, account_id=account_id,
                                   resource_type='file-system', resource_id=self.get_efs_filesystem_id())
        return arn

    def get_alb_target_group_arn(self, target_group_stack_identifier):
        stack_name = utilities.get_stack_name(self.customer_id, self.environment_type,
                                              target_group_stack_identifier + 'TargetGroup')
        a_value = self.get_a_stack_output_value(stack_name, 'TargetGroup')
        self.logger.info('TargetGroup for {} stack is {}'.format(stack_name, a_value))
        return a_value
