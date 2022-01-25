import sys
from botocore.config import Config
from awsservicespkg.utils import constants


class RDSService:

    def __init__(self, _logger, session, aws_region):
        try:
            self.rds_client = session.client('rds', region_name=aws_region, config=Config(retries=dict(max_attempts=3)))
            self.logger = _logger
            self.logger.info('AWS RDS client initialized')
        except Exception as e:
            _logger.exception(e)
            print("Error while creating AWS RDS client. Please refer to the log file at- " + constants.logger_path)
            sys.exit(1)

    def get_subnet_group_for_given_vpc_id(self, vpc_id):
        try:
            response = self.rds_client.describe_db_subnet_groups()
            all_subnet_groups = response['DBSubnetGroups']
            for subnet_group in all_subnet_groups:
                if subnet_group['VpcId'] == vpc_id:
                    return subnet_group
        except Exception as e:
            self.logger.exception(e)
            print(
                "Error while getting subnet group name for given VPC ID: {}. Please refer to the log file at- ".format(
                    vpc_id)
                + constants.logger_path)
            sys.exit(1)

    def update_db_cluster(self, db_cluster_identifier, security_group_ids, enable_deletion_protection):
        try:
            res = self.rds_client.modify_db_cluster(DBClusterIdentifier=db_cluster_identifier,
                                                    VpcSecurityGroupIds=security_group_ids,
                                                    DeletionProtection=enable_deletion_protection,
                                                    CopyTagsToSnapshot=True,
                                                    ApplyImmediately=True
                                                    )
            self.logger.info("DB Cluster: {} updated successfully".format(db_cluster_identifier))
            return res['DBCluster']
        except Exception as e:
            self.logger.exception(e)
            print("Error while updating DB Cluster: {}. Please refer to the log file at- ".format(db_cluster_identifier)
                  + constants.logger_path)
            sys.exit(1)

    def create_new_database_instance(self, db_cluster_identifier, db_instance_identifier, engine, db_instance_class):
        try:
            res = self.rds_client.create_db_instance(DBInstanceIdentifier=db_instance_identifier,
                                                     DBClusterIdentifier=db_cluster_identifier,
                                                     Engine=engine,
                                                     DBInstanceClass=db_instance_class
                                                     )
            self.logger.info("DB Instance: {} created successfully.".format(db_instance_identifier))
            return res['DBInstance']
        except Exception as e:
            self.logger.exception(e)
            print(
                "Error while creating DB Instance: {}. Please refer to the log file at- ".format(db_instance_identifier)
                + constants.logger_path)
            sys.exit(1)

    def check_db_instance_status(self, db_instance_identifier):
        try:
            res = self.rds_client.describe_db_instances(DBInstanceIdentifier=db_instance_identifier)['DBInstances'][0]
            db_instance_status = res['DBInstanceStatus']
            return db_instance_status
        except Exception as e:
            self.logger.exception(e)
            print(
                "Error while checking DB Instance Status for instance: {}. Please refer to the log file at- ".format(
                    db_instance_identifier)
                + constants.logger_path)
            sys.exit(1)
