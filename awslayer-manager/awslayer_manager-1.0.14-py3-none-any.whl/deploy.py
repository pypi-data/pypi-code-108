import os
import shutil

from .helpers import build_in_container


def deploy_layer(runtime, env):
    print('Beginning deployment...')
    os.chdir('.layer')

    print('Building layer...')
    error = build_in_container(runtime)
    if error:
        os.chdir('..')
        shutil.rmtree('.layer')
        exit()

    print('Deploying layer...')
    error = os.system(f'sls deploy --stage {env}')
    if error:
        print("\033[91mDeployment failed!\033[0m")
    else:
        print(f"\033[92mDeployment to {env} complete!\033[0m")