import sys

from botocore.config import Config

from awsservicespkg.utils import constants


class EFSService:
    def __init__(self, _logger, session, region):
        try:
            self.efs_client = session.client('efs', region_name=region, config=Config(retries=dict(max_attempts=3)))
            self.logger = _logger
            self.logger.info('EFS client initialized')
        except Exception as e:
            _logger.exception(e)
            print("Error while initializing EFS client. Please refer to the log file at- " + constants.logger_path)
            sys.exit(1)

    def create_tags_for_efs(self, filesystem_id, tags):
        try:
            res = self.efs_client.create_tags(FileSystemId=filesystem_id, Tags=tags)
            self.logger.info('Tags: {} created for FileSystemId {}'.format(tags, filesystem_id))
            return res
        except Exception as e:
            self.logger.exception(e)
            print("Error while creating tags for filesystem_id: {}. Please refer to the log file at- ".format(
                filesystem_id)
                  + constants.logger_path)
            sys.exit(1)

    def create_mount_targets(self, filesystem_id, subnet_id, security_groups):
        try:
            res = self.efs_client.create_mount_target(FileSystemId=filesystem_id,
                                                      SubnetId=subnet_id,
                                                      SecurityGroups=security_groups
                                                      )
            self.logger.info('Mount targets created for EFS filesystem_id: {} with subnet_id as {} and security_group '
                             'as {}'.format(filesystem_id, subnet_id, security_groups))
            return res
        except Exception as e:
            self.logger.exception(e)
            print("Error while mounting targets for filesystem_id: {}. Please refer to the log file at- ".format(
                filesystem_id)
                  + constants.logger_path)
            sys.exit(1)
