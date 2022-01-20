from __future__ import absolute_import, division, print_function, unicode_literals

import getpass
import os
import shutil
import subprocess
import sys

from Crypto.PublicKey import RSA
import publisher.settings as settings
from publisher.exceptions import ValidationError
from publisher.touchsurgery import TouchSurgery
from publisher.utils import WorkingDirectory, get_command_output, get_input, get_platform, \
    call_command_and_print_exception


def setup_users_machine():
    """
    User Setup for publish
        1. Check if git is installed
        2. Check if Node.js is installed
        3. Install studio-report app
        4. Setup SSH
        5. Cloning the repo and git pull
    """
    if not git_installed():
        win_msg = 'Please install Github for windows from https://desktop.github.com/ before coming back and ' \
                  'continuing and running setup again.'
        mac_msg = 'Please install Git for Mac from https://git-scm.com/download/mac before running setup again.'

        print("%s" % mac_msg if 'darwin' in get_platform() else win_msg)
        sys.exit(1)

    if not node_installed():
        print("""
            Please install Node.js for your platform from: https://nodejs.org/en/download/ before running setup again.
        """)
        sys.exit(1)

    if not os.path.isdir("{report_folder}/node_modules".format(report_folder=settings.REPORT_FOLDER)):
        print("Installing studio-report tool.")
        install_studio_report_tool()

    print('Generating key and configuring user profile')
    check_and_create_directory(settings.SSH_DIRECTORY_PATH)
    sys.stdout.flush()

    login_success = False
    get_username()
    while not login_success:
        if login(get_email(), get_password(), create_rsa_return_pub_key()):
            login_success = True

    print("Configuring ssh config file ")
    check_and_create_file(settings.SSH_CONFIG_PATH)
    if not has_private_key():
        raise RuntimeError("Unable to proceed without a key. Please contact Hansel before trying again")
    configure_ssh_config()

    print("Installing and configuring git lfs")
    check_brew_installed()
    install_git_lfs()
    configure_git_lfs()

    check_and_create_directory(settings.GIT_DIRECTORY)
    for repository, checkout_directory in get_repositories_to_checkout():
        clone_repo(repository, checkout_directory)
        pull_repo(checkout_directory)


def get_repositories_to_checkout():
    return [(settings.PROCEDURE_REPOSITORY, settings.PROCEDURE_CHECKOUT_DIRECTORY),
            (settings.CHANNELS_REPOSITORY, settings.CHANNELS_CHECKOUT_DIRECTORY),
            (settings.TRANSLATIONS_REPOSITORY, settings.TRANSLATIONS_CHECKOUT_DIRECTORY)]


def git_installed():
    try:
        subprocess.check_output(['git', '--version'])
    except OSError:
        print("Git not installed")
        return False
    return True


def node_installed():
    try:
        subprocess.check_output(['node', '--version'])
    except OSError:
        print("Node.js is not installed")
        return False
    return True


def install_studio_report_tool():
    npm_command = ["npm.cmd", "i"] if sys.platform == "win32" else ["npm", "-i"]

    p = subprocess.Popen(
        npm_command, cwd=settings.REPORT_FOLDER, stdout=subprocess.PIPE
    )
    (output) = p.communicate()
    print(output)
    p.wait()


def get_username(all_repos=True):
    print("Please enter your name here:")
    sys.stdout.flush()
    username = get_input()
    if all_repos:
        subprocess.check_output(['git', 'config', '--global', 'user.name', username])
    else:
        subprocess.check_output(['git', 'config', 'user.name', username])


def get_email(all_repos=True):
    print("Please enter your touch surgery email here:")
    sys.stdout.flush()
    email = get_input()
    if all_repos:
        subprocess.check_output(['git', 'config', '--global', 'user.email', email])
    else:
        subprocess.check_output(['git', 'config', 'user.email', email])
    return email


def get_password():
    print("Please enter your touch surgery password here:")
    sys.stdout.flush()
    password = getpass.getpass()
    return password


def has_private_key():
    """Check whether the user has the correct private key
    """
    return os.path.exists(settings.RSA_PUBLIC_KEY_PATH)


def configure_ssh_config():
    """Creates and sets up an ssh config file, or appends the necessary entry to an existing one
    """
    shutil.copyfile(os.path.expanduser(settings.SSH_CONFIG_PATH), os.path.expanduser(settings.SSH_CONFIG_PATH + '.bak'))

    obsolete_stanza = (
        'Host {0}\n '
        'User ubuntu\n '
        'IdentitiesOnly true\n '
        'IdentityFile ~/.ssh/touchsurgery-studio.pem\n'
    ).format(settings.STUDIO_GIT_PATH)

    ssh_config_stanza = (
        'Host {0}\n'
        ' StrictHostKeyChecking no\n'
        ' User git\n'
        ' IdentitiesOnly true\n'
        ' IdentityFile {1}\n'
    ).format(settings.STUDIO_GIT_PATH, settings.RSA_PRIVATE_KEY_PATH)

    try:

        with open(os.path.expanduser(settings.SSH_CONFIG_PATH), "r") as config_file:
            current_config_text = config_file.read()
        ssh_config_missing = ssh_config_stanza not in current_config_text
        obsolete_stanza_present = obsolete_stanza in current_config_text

        # Remove outdated config info
        if obsolete_stanza_present:
            current_config_text = current_config_text.replace(obsolete_stanza, '')
            with open(os.path.expanduser(settings.SSH_CONFIG_PATH), "w") as config_file:
                config_file.write(current_config_text)

        # Add relevant config info
        if ssh_config_missing:
            with open(os.path.expanduser(settings.SSH_CONFIG_PATH), "a+") as config_file:
                config_file.write('\n' + '\n' + ssh_config_stanza)

    except Exception:
        print("Unable to configure the ssh config")
        raise


def check_brew_installed():
    """ Get Macs ready to brew
    """
    if 'darwin' in get_platform():
        output, _ = get_command_output(['brew', 'help'])
        if 'usage' not in output.lower():
            raise Exception("Please install Brew from here: https://brew.sh/")


def install_git_lfs():
    """Install git lfs
    """
    if 'darwin' in get_platform():
        output, _ = get_command_output(['which', 'git-lfs'])
        if 'usr' not in output.lower():
            call_command_and_print_exception(['brew', 'install', 'git-lfs'], "brew lfs install failure")

    call_command_and_print_exception(['git', 'lfs', 'install'], "lfs install failure")


def clone_repo(repository, directory):
    if not os.path.exists(directory):
        call_command_and_print_exception(['git', 'lfs', 'clone', repository, directory], "Clone repo failure")
    else:
        print("Not cloning repository: {0} already exists".format(directory))


def pull_repo(directory):
    with WorkingDirectory(directory):
        call_command_and_print_exception(['git', 'lfs', 'pull', 'origin', 'master'], "Git pull failure")


def check_and_create_directory(path):
    try:
        if not os.path.exists(path):
            os.mkdir(path)
    except Exception:
        print("Could not find or create the directory")
        raise ValidationError


def check_and_create_file(path):
    try:
        if not os.path.exists(path):
            subprocess.check_output(['touch', path])
    except Exception as e:
        print("Could not find or create the file")
        print(e)
        raise ValidationError


def configure_git_lfs():
    """Set relevant  lfs settings
    """
    call_command_and_print_exception(['git', 'config', '--global', 'lfs.url',
                                      'https://live.touchsurgery.com/api/v3/lfs'], "lfs config failure")
    call_command_and_print_exception(['git', 'config', '--global', 'lfs.activitytimeout', '60'], "lfs config failure")


def create_rsa_return_pub_key():
    private_key = settings.RSA_PRIVATE_KEY_PATH
    public_key = settings.RSA_PUBLIC_KEY_PATH

    key = RSA.generate(2048)
    if os.path.exists(private_key):
        os.chmod(private_key, 0o0600)

    with open(private_key, 'wb') as rsa_pri:
        os.chmod(private_key, 0o0600)
        rsa_pri.write(key.exportKey('PEM'))

    pubkey = key.publickey()
    with open(public_key, 'wb') as rsa_pub:
        pub_key = pubkey.exportKey('OpenSSH')
        rsa_pub.write(pubkey.exportKey('OpenSSH'))

    return pub_key.split()[1]


def login(email, password, pub_key):
    """Verify TouchSurgery user here with rsa key and TouchSurgery login
    """
    login_instance = TouchSurgery()
    if not login_instance.login(email, password):
        return False
    if not login_instance.upload_key(pub_key):
        print('Your rsa key is invalid, please try running setup again or contact pipeline.')
        raise ValidationError
    return True
