import argparse
import sys
import os
from distutils.dir_util import copy_tree
import pathlib
import shutil
import platform
import subprocess
from lsbatch.constants import *
from lsbatch.requests_handler import RequestHandler
from lsbatch.batch_job_operations import BatchJobOperations
from lsbatch.helper import Helper, ProgressBar
from lsbatch.log import Log

current_version = CURRENT_VERSION
virtual_env_name = VIRTUAL_ENV_NAME
command_run_python = ''
command_activate_virual_env = ''
run_in_shell = False
file_path = pathlib.Path(__file__).resolve()


def main():
    try:
        setup_commands()
        args = sys.argv[1:]
        script_path = os.getcwd()
        if len(args) == 0:
            Log.question(Messages.SelectTask)
            sys.argv.append(input())
            main()
        elif args[0] == 'init':
            initiate_batch(script_path)
        elif args[0] == 'pack':
            if Helper.validate_lsbatch_pack(script_path):
                Helper.zip_source_code(script_path)
        elif args[0] == 'help':
            print_help_section()
        elif args[0] == 'run':
            if os.path.exists(os.path.join(script_path, 'startup.py')):
                run_batch_job(script_path)
            else:
                Log.error(Messages.StartUpFileNotPresent.format(script_path))
        elif args[0] == 'install':
            if len(args) > 2:
                Log.error(ValidationMessages.LSBatchInstallArguments)
                return
            if len(args) == 1:
                lsbatch_install(script_path)
                return
            lsbatch_install_package(script_path, args[1])
        elif args[0] == 'uninstall':
            if len(args) != 2:
                Log.error(ValidationMessages.LSBatchUninstallArguments)
                return
            uninstall_package(script_path, args[1])
        elif args[0] == 'save':
            credentials = get_developer_api_credentials_from_arg(args[1:], 'save', ['settings'])
            if credentials is None:
                return
            BatchJobOperations.lsbatch_save(script_path, credentials['settings'])
        elif args[0] == 'publish':
            credentials = get_developer_api_credentials_from_arg(args[1:], 'publish')
            if credentials is None:
                return
            BatchJobOperations.lsbatch_publish(script_path)
        elif args[0] == 'configure':
            BatchJobOperations.lsbatch_configure()
        else:
            Log.error(ValidationMessages.LSBatchArguments)
    finally:
        try:
            latest_version = get_latest_version()
            if not (current_version == latest_version):
                Log.info(Messages.LatestVersionWarning)
        except Exception as ex:
            pass


def get_developer_api_credentials_from_arg(args, sub_command, additional_bool_arguments=None):
    parser = argparse.ArgumentParser(description=f'lsbatch {sub_command}', prog=f'lsbatch {sub_command}')
    parser.add_argument('-o', '--orgcode', dest=Constants.OrgCode, type=str, required=False)
    parser.add_argument('-t', '--token', dest=Constants.Token, type=str, required=False)
    parser.add_argument('-r', '--region', dest=Constants.Region, type=str, help=Messages.RegionArgumentHelp, required=False)
    parser.add_argument('-p', '--profile', dest=Constants.Profile, type=str, required=False)

    if additional_bool_arguments is not None:
        for arg in additional_bool_arguments:
            parser.add_argument(f'-{arg[0]}', f'--{arg}', action='store_true')

    credentials = parser.parse_args(args)
    credentials_dict = credentials.__dict__
    error_message = None
    if credentials_dict.get(Constants.Profile) is not None:
        if credentials_dict[Constants.Profile] == '':
            error_message = ValidationMessages.ProfileNameEmpty
        else:
            profile_credentials = BatchJobOperations.retrieve_configuration(credentials_dict[Constants.Profile])
            if profile_credentials is None:
                error_message = ValidationMessages.ProfileNameNotFound
            else:
                credentials_dict.update(profile_credentials)
    elif credentials_dict.get(Constants.OrgCode) is None or credentials_dict.get(
            Constants.Token) is None or credentials_dict.get(Constants.Region) is None:
        error_message = ValidationMessages.ArgumentsNotPassedCorrectly

    if error_message is None:
        error_message = Helper.validate_credentials(credentials_dict, True)
        if error_message is None:
            RequestHandler.set_up_credentials(credentials_dict)
            return credentials_dict
    Log.error(error_message)


def initiate_batch(script_path):
    try:
        import virtualenv
    except ImportError:
        Log.error(ValidationMessages.VirtualEnvironmentNotFound)
        return
    Log.question(Messages.YourBatchName)
    batch_job_name = input()
    progress_bar = ProgressBar(message=Messages.InstallingDependencies)
    progress_bar.start()
    try:
        batch_job_directory = os.path.join(script_path, batch_job_name)
        copy_tree(os.path.join(file_path.parent, 'lsq_batch_template'), batch_job_directory)
        add_gitignore(batch_job_directory)
        batch_details = Helper.retrieve_batch_details(batch_job_directory)
        batch_details["Name"] = batch_job_name
        Helper.update_batch_details(batch_job_directory, batch_details)
        returncode = create_virtual_environment(batch_job_directory)
        if not (returncode == 0):
            progress_bar.kill = True
            return
        progress_bar.stop = True
    except KeyboardInterrupt:
        progress_bar.kill = True
    except Exception as ex:
        progress_bar.kill = True
        raise ex


def lsbatch_install(script_path):
    if os.path.exists(os.path.join(script_path, 'src')):
        progress_bar = ProgressBar(message=Messages.InstallingDependencies)
        progress_bar.start()
        try:
            batch_template_path = os.path.join(file_path.parent, 'lsq_batch_template')
            for filename in os.listdir(batch_template_path):
                files_not_to_overrride = ['event.json', 'query.json', 'settings.json', 'sample_query_result.csv', 'batch_details.json']
                if not (filename == 'src' or filename == '__pycache__' or (
                        filename in files_not_to_overrride and os.path.exists(os.path.join(script_path, filename)))):
                    if os.path.isdir(os.path.join(batch_template_path, filename)):
                        copy_tree(os.path.join(batch_template_path, filename), os.path.join(script_path, filename))
                    else:
                        shutil.copy(os.path.join(batch_template_path, filename), script_path)
                if not (os.path.exists(os.path.join(script_path, '.gitignore'))):
                    add_gitignore(script_path)
            returncode = create_virtual_environment(script_path)
            if not (returncode == 0):
                progress_bar.kill = True
                return
            requirements_file_path = os.path.join(script_path, 'src', 'requirements.txt')
            if os.path.exists(requirements_file_path):
                process = subprocess.Popen(
                    '{} && pip install -r "{}"'.format(command_activate_virual_env, requirements_file_path),
                    shell=run_in_shell, stdout=subprocess.PIPE)
                process.communicate()
                if not (process.returncode == 0):
                    progress_bar.kill = True
                    return
            progress_bar.stop = True
        except KeyboardInterrupt:
            progress_bar.kill = True
        except Exception as ex:
            progress_bar.kill = True
            raise ex
    else:
        Log.error(ValidationMessages.NotFoundSourceFolder)


def remove_package_requirements_txt(path, package_name):
    with open(path, 'r') as f:
        data = f.readlines()
    with open(path, 'w') as f:
        for line in data:
            if not (package_name.lower() == line.split("==")[0].strip('\n').lower()):
                f.write(line)


def lsbatch_install_package(script_path, package):
    if os.path.exists(os.path.join(script_path, virtual_env_name)):
        package = package.lower()
        package_and_version = package.split("==")
        reqirements_path = os.path.join(script_path, 'src', 'requirements.txt')
        if package_in_default_packages(package_and_version[0]):
            Log.info(Messages.RequirementSatisfied)
            return
        if os.path.exists(reqirements_path):
            with open(reqirements_path) as f:
                data = f.readlines()
                for line in data:
                    if package + '\n' == line.lower() or package == line.lower():
                        Log.info(Messages.RequirementSatisfied)
                        return
        process = subprocess.Popen('{} && pip install "{}"'.format(command_activate_virual_env, package),
                                   shell=run_in_shell)
        process.wait()
        if process.returncode == 0:
            if os.path.exists(reqirements_path):
                remove_package_requirements_txt(reqirements_path, package_and_version[0])
            with open(reqirements_path, mode='a') as requirement_file:
                requirement_file.write(package + '\n')
    else:
        Log.error(virtual_env_name + ' not present in directory ' + script_path)


def print_help_section():
    Log.info(Messages.LSBatchHelpSection)


def create_virtual_environment(path):
    os.chdir(path)
    command_install_packages = 'pip install -r "{}"'.format(
        os.path.join(file_path.parent, 'virtual-env-requirements.txt'))
    command_create_virtul_env = '{} -m venv {}'.format(command_run_python, virtual_env_name)
    process2 = subprocess.Popen(command_create_virtul_env, stdout=subprocess.PIPE, shell=run_in_shell)
    process2.communicate()
    if not (process2.returncode == 0):
        return process2.returncode
    process3 = subprocess.Popen('{} && {}'.format(command_activate_virual_env, command_install_packages),
                                stdout=subprocess.PIPE, shell=run_in_shell)
    process3.communicate()
    if not (process3.returncode == 0):
        return process3.returncode
    return 0


def package_in_default_packages(package_name):
    default_requirement_file = os.path.join(file_path.parent, 'virtual-env-requirements.txt')
    with open(default_requirement_file, 'r') as f:
        data = f.readlines()
    for line in data:
        if package_name.lower() == line.split("==")[0].strip('\n').lower():
            return True
    return False


def uninstall_package(script_path, package):
    package_and_version = package.split("==")
    if os.path.exists(os.path.join(script_path, virtual_env_name)):
        if package_in_default_packages(package_and_version[0]):
            Log.error(ValidationMessages.CanNotUninstallDefaultPackage)
            return
        process = subprocess.Popen('{} && pip uninstall "{}"'.format(command_activate_virual_env, package),
                                   shell=run_in_shell)
        process.wait()
        if process.returncode == 0:
            requirement_path = os.path.join(script_path, 'src', 'requirements.txt')
            if os.path.exists(requirement_path):
                remove_package_requirements_txt(requirement_path, package_and_version[0])
    else:
        Log.error(virtual_env_name + ' not present in directory ' + script_path)


def run_batch_job(activation_path):
    os.chdir(activation_path)
    process = subprocess.Popen('{} && {} startup.py'.format(command_activate_virual_env, command_run_python),
                               shell=run_in_shell)
    process.wait()


def add_gitignore(path):
    gitignore_file_path = os.path.join(file_path.parent, 'gitignore.txt')
    if os.path.exists(gitignore_file_path):
        with open(gitignore_file_path, 'r') as gitignore_file:
            gitignore_file_content = gitignore_file.read()

        with open(os.path.join(path, '.gitignore'), 'w') as gitignore_file:
            gitignore_file.write(gitignore_file_content)


def get_latest_version():
    data = RequestHandler.get_package_info()
    latest_version = data['info']['version']
    return latest_version


def setup_commands():
    global command_run_python
    global command_activate_virual_env
    global run_in_shell
    if platform.system() == 'Windows':
        command_run_python = 'py'
        command_activate_virual_env = "{}\{}\{}".format(virtual_env_name, 'Scripts', 'activate.bat')
    else:
        command_run_python = 'python'
        command_activate_virual_env = "source {}/{}/{}".format(virtual_env_name, 'bin', 'activate')
        run_in_shell = True


if __name__ == '__main__':
    main()
