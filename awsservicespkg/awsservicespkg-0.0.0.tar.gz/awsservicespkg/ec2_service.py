import sys

from botocore.config import Config

from awsservicespkg.utils import constants


class EC2Service:
    def __init__(self, _logger, session, region):
        try:
            self.ec2_client = session.client('ec2', region_name=region, config=Config(retries=dict(max_attempts=3)))
            self.logger = _logger
            self.logger.info('EC2 client initialized')
        except Exception as e:
            _logger.exception(e)
            print("Error while initializing EC2 client. Please refer to the log file at- " + constants.logger_path)
            sys.exit(1)

    def get_instance_platform(self, instance_id):
        try:
            ec2_platform = ''
            ec2_describe_instance_response = self.ec2_client.describe_instances(InstanceIds=[instance_id])
            instance_image_id = ec2_describe_instance_response['Reservations'][0]['Instances'][0]['ImageId']
            ec2_describe_image_response = self.ec2_client.describe_images(ImageIds=[instance_image_id])

            ec2_platform_name = ec2_describe_image_response['Images'][0]['Name']
            for platform in constants.ec2_instance_platform_mappings:
                for item in constants.ec2_instance_platform_mappings[platform]:
                    if item in ec2_platform_name:
                        ec2_platform = platform
                        return ec2_platform

            return ec2_platform
        except Exception as err:
            self.logger.exception(err)
            print("Error while getting instance platform. Please refer to the log file at- " + constants.logger_path)
            sys.exit(1)

    def get_vpc_id_for_vpc_cidr(self, vpc_cidr):
        try:
            response = self.ec2_client.describe_vpcs(Filters=[
                {
                    'Name': 'cidr-block-association.cidr-block',
                    'Values': [vpc_cidr]
                },
            ])
            return response['Vpcs'][0]['VpcId']
        except Exception as err:
            self.logger.exception(err)
            print("Error while getting VPC for CIDR: {}. Please refer to the log file at- ".format(vpc_cidr)
                  + constants.logger_path)
            sys.exit(1)

    def get_security_group_id(self, identifier, customer_id, environment_type):
        try:
            security_groups = self.ec2_client.describe_security_groups()['SecurityGroups']
            for security_group in security_groups:
                security_group_name = security_group['GroupName']
                if all(x in security_group_name for x in [identifier, customer_id, environment_type]):
                    return security_group['GroupId']
        except Exception as err:
            self.logger.exception(err)
            print("Error while getting security group id. Please refer to the log file at- " + constants.logger_path)
            sys.exit(1)

    def describe_ec2_instances(self, instance_ids=None, filters=None):
        try:
            if instance_ids is not None and filters is not None:
                res = self.ec2_client.describe_instances(InstanceIds=instance_ids, Filters=filters)
            elif instance_ids is not None:
                res = self.ec2_client.describe_instances(InstanceIds=instance_ids)
            elif filters is not None:
                res = self.ec2_client.describe_instances(Filters=filters)
            else:
                res = self.ec2_client.describe_instances()
            return res['Reservations']
        except Exception as err:
            self.logger.exception(err)
            print("Error while describing ec2 instances. Please refer to the log file at- " + constants.logger_path)
            sys.exit(1)

    def create_tags_for_ec2_instance(self, instance_ids, tags):
        try:
            self.ec2_client.create_tags(Resources=instance_ids, Tags=tags)
            self.logger.info('Tags created for instance ids- {}'.format(instance_ids))
        except Exception as e:
            self.logger.exception(e)
            print('Error while creating tags for instance ids- {}. Please refer to the log file at- {}'.format(
                instance_ids, constants.logger_path
            ))
            sys.exit(1)

    def assign_iam_instance_profile(self, instance_id, iam_instance_profile_arn):
        try:
            res = self.ec2_client.associate_iam_instance_profile(IamInstanceProfile={'Arn': iam_instance_profile_arn},
                                                                 InstanceId=instance_id)
            self.logger.info('IAM instance profile assigned to instance- {}'.format(instance_id))
            return res
        except Exception as e:
            self.logger.exception(e)
            print(
                'Error while assigning IAM instance profile for instance id- {}. Please refer to the log file at- {}'.format(
                    instance_id, constants.logger_path
                ))
            sys.exit(1)
