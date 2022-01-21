import os
import shutil
import sys
import time
from optparse import OptionParser
import cursor

from .deploy import deploy_layer
from .helpers import get_service_name, get_runtime
from .init import init_layer


def main():
    parser = OptionParser(description='A simple AWS Lambda Layer manager.', prog='awslayer',
                          epilog='\033[1mTo get more help with this package, contact the repo owner.\033[0m')

    parser.add_option('-e', '--env', dest='env', default='dev', choices=['dev', 'stage', 'prod'],
                      help="Specify environment, 'dev' by default", metavar='ENV')

    (options, args) = parser.parse_args()

    cursor.hide()

    env_str = f'{options.env.upper()}'
    if env_str == 'PROD':
        env_str = f'\033[5;41;30m {options.env.upper()} \033[0m'
    else:
        env_str = f'\033[31m {options.env.upper()} \033[0m'

    print(f'\033[33mSelected environment:\033[0m {env_str}')

    for i in range(3, 0, -1):
        sys.stdout.write(f'\033[1;33mBeginning in:  \033[31m{str(i)}\033[0m\r')
        sys.stdout.flush()
        time.sleep(1)

    service = get_service_name()
    runtime = get_runtime()

    init_layer(service, runtime, options.env)
    deploy_layer(runtime, options.env)

    print('\033[92mCleaning...\033[0m')
    os.chdir('..')
    shutil.rmtree('.layer')
    print(f"\033[92mDone!\033[0m")

    cursor.show()


if __name__ == '__main__':
    dir = os.getcwd()
    try:
        main()
    except:
        shutil.rmtree(f'{dir}/.layer')
        cursor.show()
        sys.exit(1)
