import os
import sys

global_log_file_name = 'python-utils.log'

# logger file path
logger_path = os.path.join(sys.path[1], 'python-utils.log')

# SSM default timeout
ssm_default_timeout = '600'
backup_default_timeout = '600'

# Negative words to check in STD Output of SSM get_command_invocation
neg_words_to_check = ['failed', 'error', 'cannot']

# Server platform identifiers
ec2_instance_platform_mappings = {'Linux': ['RHEL', 'LINUX'],
                                  'Windows': ['Win', 'Windows']}
