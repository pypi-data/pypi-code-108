import json
import sys

from botocore.config import Config

from awsservicespkg.utils import constants


class Route53Service:
    # Instantiate Route53 service
    def __init__(self, _logger, session, region, customer_id, environment_type, phz_id):
        try:
            route53 = session.client('route53', region_name=region, config=Config(retries=dict(max_attempts=3)))
            self.logger = _logger
            self.route53_client = route53
            self.customer_id = customer_id
            self.environment_type = environment_type
            self.hosted_zone_id = phz_id
            self.logger.info('Route53 client initialized')
        except Exception as err:
            _logger.exception(err)
            print("Error while initializing Route53 client. Please refer to the log file at- " + constants.logger_path)
            sys.exit(1)

    def create_change_rs_batch_input(self, record_sets_json):
        change_rs_batch_str = json.loads('{"Comment": "patch updates", "Changes": []}')
        changes_list = []
        for record in record_sets_json:
            change_record_json = json.loads('{"Action": "UPSERT", "ResourceRecordSet": {}}')
            change_record_json["ResourceRecordSet"] = json.loads(record)
            changes_list.append(change_record_json)

        change_rs_batch_str["Changes"] = changes_list
        return change_rs_batch_str

    def update_record_sets(self, records_list):
        # record_sets_str = utils.replace_values_in_string(json.dumps(constants.route53_record_sets),
        #                                                      values_to_replace)
        record_sets_json = json.dumps(records_list)
        self.logger.info(json.loads(record_sets_json))

        create_record_sets_input = self.create_change_rs_batch_input(json.loads(record_sets_json))
        try:
            self.route53_client.change_resource_record_sets(
                HostedZoneId=self.hosted_zone_id,
                ChangeBatch=create_record_sets_input
            )
        except Exception as err:
            self.logger.error('An error occurred updating hosted zone records: ', err)

    def update_prod_vpc(self, prod_vpc_id, prod_vpc_region):
        self.logger.info('update_prod_vpc')
        try:
            self.route53_client.associate_vpc_with_hosted_zone(
                HostedZoneId=self.hosted_zone_id,
                VPC={
                    'VPCRegion': prod_vpc_region,
                    'VPCId': prod_vpc_id
                }
            )
        except Exception as err:
            self.logger.error('An error occurred updating production vpc in hosted zone: ', err)
