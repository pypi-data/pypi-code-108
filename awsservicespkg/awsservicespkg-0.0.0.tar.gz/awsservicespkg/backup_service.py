import sys
import time

from botocore.config import Config

from awsservicespkg.utils import constants


class BackupService:
    # Instantiate Backup service
    def __init__(self, _logger, session, aws_region):
        try:
            self.backup_client = session.client('backup', region_name=aws_region,
                                                config=Config(retries=dict(max_attempts=3)))
            self.logger = _logger
            self.logger.info('AWS Backup client initialized')
        except Exception as e:
            _logger.exception(e)
            print("Error while creating AWS Backup client. Please refer to the log file at- " + constants.logger_path)
            sys.exit(1)

    def start_on_demand_backup(self, backup_vault_name, resource_arns, iam_role_arn):
        try:
            backup_job_ids = []
            for resource_arn in resource_arns:
                response = self.backup_client.start_backup_job(BackupVaultName=backup_vault_name,
                                                               ResourceArn=resource_arn,
                                                               IamRoleArn=iam_role_arn
                                                               )
                backup_job_ids.append(response['BackupJobId'])
                self.logger.info('Backup job id for ARN- {} is {}'.format(resource_arn, response['BackupJobId']))
            return backup_job_ids
        except Exception as e:
            self.logger.exception(e)
            print("Error while starting on demand backup. Please refer to the log file at- " + constants.logger_path)
            sys.exit(1)

    def get_list_of_latest_recovery_point_from_backup_vault(self, backup_vault_name, resource_type):
        try:
            response = self.backup_client.list_recovery_points_by_backup_vault(BackupVaultName=backup_vault_name,
                                                                               ByResourceType=resource_type)
            all_recovery_points = response['RecoveryPoints']
            latest_recovery_points = [
                max(
                    filter(lambda recovery_point: recovery_point['ResourceArn'] == arn, all_recovery_points),
                    key=lambda recovery_point: recovery_point["CreationDate"]
                ) for arn in {recovery_point['ResourceArn'] for recovery_point in all_recovery_points}
            ]
            return latest_recovery_points
        except Exception as e:
            self.logger.exception(e)
            print("Error while getting list of latest recovery points for {} from {}. Please refer to the log file at- ".format(
                resource_type, backup_vault_name) + constants.logger_path)
            sys.exit(1)

    def get_recovery_point_metadata(self, backup_vault_name, recovery_point_arn):
        try:
            response = self.backup_client.get_recovery_point_restore_metadata(BackupVaultName=backup_vault_name,
                                                                              RecoveryPointArn=recovery_point_arn)
            return response['RestoreMetadata']
        except Exception as e:
            self.logger.exception(e)
            print("Error while getting metadata for recovery point arn from {}. Please refer to the log file at- ".format(backup_vault_name)
                  + constants.logger_path)
            sys.exit(1)

    def restore(self, restore_data):
        try:
            response = self.backup_client.start_restore_job(RecoveryPointArn=restore_data['RecoveryPointArn'],
                                                            IamRoleArn=restore_data['IamRoleArn'],
                                                            Metadata=restore_data['Metadata'])
            self.logger.info('Restore job started for {}'.format(restore_data['RecoveryPointArn']))
            return response['RestoreJobId']
        except Exception as e:
            self.logger.exception(e)
            print("Error while restoring {}. Please refer to the log file at- ".format(restore_data['RecoveryPointArn'])
                  + constants.logger_path)
            sys.exit(1)

    def check_backup_job_state(self, job_ids, service_type, timeout=constants.backup_default_timeout):
        try:
            start_time = time.time()
            total_ids = len(job_ids)
            count = 0
            result = {}
            curr_state = ''
            while job_ids:
                count += 1
                job_id = job_ids.pop(0)
                if service_type == 'backup':
                    output = self.backup_client.describe_backup_job(
                        BackupJobId=job_id
                    )
                    curr_state = output['State']
                    result[job_id] = {'Status': curr_state}
                elif service_type == 'restore':
                    output = self.backup_client.describe_restore_job(
                        RestoreJobId=job_id
                    )
                    curr_state = output['Status']
                    result[job_id] = {'ResourceType': output.get('ResourceType'),
                                      'Status': curr_state,
                                      'CreatedResourceArn': output.get('CreatedResourceArn')}
                # Check if state of back up job is in terminated state
                if curr_state in ['ABORTED', 'COMPLETED', 'FAILED', 'EXPIRED']:
                    self.logger.info(
                        'Backup/Restore for job id- {} finished with state as {}'.format(job_id, curr_state))
                # If command is still running
                else:
                    job_ids.append(job_id)
                # If provided time limit gets exceeded
                if time.time() - start_time >= float(timeout) and job_ids:
                    self.logger.error('Timeout exceeded')
                    break
                # If loop completes 1 iteration over list, it will sleep for 60 seconds
                if count == total_ids and job_ids:
                    total_ids = len(job_ids)
                    count = 0
                    time.sleep(60)

            if not job_ids:
                self.logger.info('Backup/Restore finished with result- {}'.format(result))
            else:
                self.logger.error('Time-out occurred, state of backup/restore job ids - ' + ', '.join(job_ids) +
                                  ' are unknown.')
            return result
        except Exception as err:
            self.logger.exception(err)
            print(
                "Error while checking state of backup/restore job ids. Please refer to the log at- " + constants.logger_path)
            sys.exit(1)
