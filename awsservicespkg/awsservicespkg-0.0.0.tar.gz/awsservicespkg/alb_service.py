import sys

from botocore.config import Config

from awsservicespkg.utils import constants


class ALBService:
    # Instantiate ALB service
    def __init__(self, _logger, session, aws_region):
        try:
            self.alb_client = session.client('elbv2', region_name=aws_region, config=Config(retries=dict(max_attempts=3)))
            self.logger = _logger
            self.logger.info('ALB client initialized')
        except Exception as e:
            _logger.exception(e)
            print("Error while creating ALB client. Please refer to the log file at- " + constants.logger_path)
            sys.exit(1)

    def deregister_targets(self, target_group_arn, instance_ids):
        targets_list = []
        try:
            for instance_id in instance_ids:
                target_element = {'Id': instance_id}
                targets_list.append(target_element)

            self.alb_client.deregister_targets(TargetGroupArn=target_group_arn, Targets=targets_list)
            self.logger.info('ALB targets deregisterd for - ' + target_group_arn)
        except Exception as e:
            self.logger.exception(e)
            print("Error while de-registering ALB target. Please refer to the log file at- " + constants.logger_path)
            sys.exit(1)

    def register_targets(self, target_group_arn, instances_with_ports):
        targets_list = []
        try:
            for instance in instances_with_ports:
                #get the first name-value pair
                instance_port_pair = next(iter(instance.items()))
                target_element = {'Id': instance_port_pair[0], 'Port': instance_port_pair[1]}
                targets_list.append(target_element)

            self.alb_client.register_targets(TargetGroupArn=target_group_arn, Targets=targets_list)
            self.logger.info('Targets registered successfully for - ' + target_group_arn)
        except Exception as e:
            self.logger.exception(e)
            print("Error while registering ALB target. Please refer to the log file at- " + constants.logger_path)
            sys.exit(1)

    def get_existing_targets(self, target_group_arn):
        existing_targets = []
        try:
            target_health_response = self.alb_client.describe_target_health(TargetGroupArn=target_group_arn)
            for target_desc in target_health_response['TargetHealthDescriptions']:
                target_id = target_desc['Target']['Id']
                existing_targets.append(target_id)
            return existing_targets
        except Exception as e:
            self.logger.exception(e)
            print("Error while retrieving target groups for target " + target_group_arn +
                  ". Please refer to the log file at - " + constants.logger_path)
            sys.exit(1)
