import re
import sys
import time
from botocore.config import Config

from awsservicespkg.utils import constants


def compose_command(platform, command, executing_user, password, win_command_type='wincmd'):
    if platform == 'Windows':
        # There is a difference between running a script and Powershell commands
        # If .bat of .cmd is to be executed, then it should be wrapped inside Invoke-Expression
        #   in such case, it is also required to separate commands using && for sequential execution
        if win_command_type == 'wincmd' and ('.bat' in command or '.cmd' in command):
            updated_command = '{Invoke-Expression -Command:"cmd.exe /c \'' + command.replace(';', ' && ') + \
                              '\'"}'
        else:
            # pure powershell commands where in you can pass in win_command_type as 'powershell'.
            updated_command = '{' + command + '}'

        main_command = 'Invoke-Command -ScriptBlock ' + updated_command

        if executing_user:
            secure_password_command = '$securePassword = ConvertTo-SecureString ' + password + \
                                      ' -AsPlainText -Force'
            credentials_command = '$credential = New-Object System.Management.Automation.PSCredential ' + \
                                  '.\\' + executing_user + ', $securePassword'
            final_command = secure_password_command + ';' + credentials_command + ';' + main_command + \
                            ' -Credential $credential -ComputerName localhost'
        else:
            final_command = main_command
    else:
        if executing_user:
            final_command = "su - " + executing_user + ' -c \"' + command + '\"'
        else:
            final_command = command

    return final_command


def check_if_std_output_contains_failure(Output):
    standard_error_content = re.sub('\r|\n| ', '', Output['StandardErrorContent'])
    if len(standard_error_content) > 0:
        return True
    for word in constants.neg_words_to_check:
        if re.compile(r'\b({0})\b'.format(word), flags=re.IGNORECASE).search(Output['StandardOutputContent']):
            return True
    return False


def log_standard_output(_logger, Output):
    if Output['StandardOutputContent'] is not None and len(Output['StandardOutputContent']) > 0:
        _logger.error('Standard Output Content is as followed: ' + Output['StandardOutputContent'])
    if Output['StandardErrorContent'] is not None and len(Output['StandardErrorContent']) > 0:
        _logger.error('Standard Error Content is as follows: ' + Output['StandardErrorContent'])


class SSMService:
    # Instantiate SSM service
    def __init__(self, _logger, session, region, customer_id, environment_type, instance_id):
        try:
            ssm_client = session.client('ssm', region_name=region, config=Config(retries=dict(max_attempts=3)))
            self.logger = _logger
            self.ssm_client = ssm_client
            self.customer_id = customer_id
            self.environment_type = environment_type
            self.instance_id = instance_id
        except Exception as err:
            _logger.exception(err)
            print("Error while creating SSM client. Please refer to the log file at- " + constants.logger_path)
            sys.exit(1)

    def execute_ssm_shell_command(self, platform, command, executing_user, password, timeout,
                                  win_command_type='wincmd'):
        try:
            _command = compose_command(platform, command, executing_user, password, win_command_type)
            if platform == 'Windows':
                document_name = 'AWS-RunPowerShellScript'
            else:
                document_name = 'AWS-RunShellScript'

            response = self.ssm_client.send_command(InstanceIds=[self.instance_id],
                                                    DocumentName=document_name,
                                                    Parameters={'commands': [_command],
                                                                'executionTimeout': [timeout]
                                                                }
                                                    )
            command_id = response['Command']['CommandId']
            self.logger.info('command id: {}'.format(command_id))
            self.logger.info('command: {}'.format(_command))
            return command_id
        except Exception as err:
            self.logger.exception(err)
            print("Error while executing shell command " + str(command) + " via SSM. Please refer to the log file at- "
                  + constants.logger_path)
            sys.exit(1)

    def check_command_execution_status(self, command_ids, ignore_error_in_output,
                                       timeout=constants.ssm_default_timeout):
        try:
            terminated_without_success = 0
            start_time = time.time()
            total_ids = len(command_ids)
            temp = 0
            time.sleep(5)
            while command_ids:
                temp += 1
                command_id = command_ids.pop(0)
                output = self.ssm_client.get_command_invocation(
                    CommandId=command_id,
                    InstanceId=self.instance_id
                )
                # Check if command execution is in terminated state
                if output['Status'] not in ['Pending', 'InProgress', 'Delayed']:
                    if output['Status'] == 'Success':
                        if not ignore_error_in_output:
                            failures_in_std = check_if_std_output_contains_failure(output)
                            if failures_in_std:
                                terminated_without_success += 1
                                self.logger.error('Standard output for command id- ' + command_id + ' contains failures')
                                log_standard_output(self.logger, output)
                    else:
                        terminated_without_success += 1
                        self.logger.error('Command id- ' + command_id + ' terminated with status = ' + output['Status'])
                        log_standard_output(self.logger, output)
                # If command is still running
                else:
                    command_ids.append(command_id)
                # If provided time limit gets exceeded
                if time.time() - start_time >= int(timeout):
                    self.logger.error('Timeout exceeded')
                    break
                # If loop completes 1 iteration over list, it will sleep for 30 seconds
                if temp == total_ids and command_ids:
                    total_ids = len(command_ids)
                    temp = 0
                    time.sleep(20)

            if not command_ids and terminated_without_success == 0:
                self.logger.info('All command ids terminated with status = Success')
                return True
            elif not command_ids and terminated_without_success != 0:
                self.logger.error('Few command ids terminated with failures')
                return False
            else:
                self.logger.error(
                    'Time-out occurred and status of command ids - ' + ', '.join(command_ids) + ' are unknown.')
                return False
        except Exception as err:
            self.logger.exception(err)
            print("Error while checking command execution status. Please refer to the log at - " + constants.logger_path)
            sys.exit(1)

    def get_command_output(self, command_id):
        try:
            output = self.ssm_client.get_command_invocation(
                CommandId=command_id,
                InstanceId=self.instance_id
            )
            return output['StandardOutputContent']
        except Exception as err:
            self.logger.exception(err)
            print("Error while retrieving output for ssm command - ' + command_id + 'Please refer to the log at - " +
                  constants.logger_path)
            sys.exit(1)
