import random
import string

import hvac
import hvac.exceptions
import jsonmerge
import yaml
import zx
from loguru import logger
from minio import Minio


class RemoteServer(object):
    def __init__(self, username: str, password: str,
                 ip: str, port: int, ssh_key: str = None):
        self.username = username
        self.password = password
        self.ip = ip
        self.port = port
        self.ssh_key = ssh_key
        self.hostname = None

    @logger.catch
    def add_to_rundeck(self, hostname: str,
                       vault_url: str,
                       vault_token: str,
                       vault_tenant: str,
                       minio_url: str,
                       minio_access_key: str,
                       minio_secret_key: str):

        self._enable_passwordless_sudo()
        self._update_hostname(hostname)
        self._add_sudo_user_with_ssh_key(
            'rundeck',
            'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC+BjvvlnGkQSVeEd89u0OhZjWxEW+b+Wf7zSQZ663JZDdSZG6/+eqDeTx7wKasBwllmKtFQsCt3490BrebT2/75HdIO4AmoYnG/5OAqIRsNccFmTJIwCuZWM+vegjyFE4e3y9U+xgBLde+Y+CyRohoQnNCNv/92D5vVJgJ4uQbPpSXRcYqZgTHcekAUe8hO0a9Qk0GJxwjjFCwlOiWOTQgYZ4Hd+UdgXRmhMKQZTmMgXxpKdWZsoJ5Ay6Ebxf2LpDOMv5ErRDFBXW4k1gtzSAgpdsfkBKbWrUgm0dGmYT7Wx1RB87qq/6idhPKpV8QlzDi10sNC62RMb9wC0touOv5zZUeA2ruuHveRqfFt4Vo1aGBsqGbrCJVa6brkTBIYUq+w+ZHdlvnjxLxufbNwzodX3vzAmd0lt7YO/C+DBT0N/UMvGm7NH2lRdxJU7/LI5OY80MpdVAAZRvkzg9bmIB7a0ZZ4WLt/mELsZn8Jr1eExxeFGBl4POC0vmHKJxtndriyTtI/wt1JGlMPeilaW44FP9SwjSQcGy46vKOCTlzh13SvALXA9gMTnOUaLUGvprnSAOpkFNSBL6PZULNbEavFA8BNCrLGe3j7iTtaT8fCi3k2EFKagDs/lvkhLFM5RIXBxNLqFT51AlcWXq6bybdG0a7zyEJcXrWndnVUzkXIw== rundeck@ansible.zadapps.info')
        self._update_ssh_credentials(
            hostname, vault_tenant, vault_token, vault_url)
        self._update_rundeck_minio_nodes_file(minio_url, minio_access_key, minio_secret_key,
                                              '/tmp/infrastructure_s3_nodes.yaml',
                                              'rundeck.zadapps.info', 'infrastructure_s3_nodes.yaml')
        self._update_ansible_minio_inventory_file(minio_url, minio_access_key, minio_secret_key,
                                                  '/tmp/ansible_inventory.yaml',
                                                  'rundeck.zadapps.info', 'ansible_inventory.yaml')
        self.print_final_ssh_server_info()

    @logger.catch
    def _enable_passwordless_sudo(self):
        self._run_command(
            rf'''"echo '{self.password}' | sudo -S sed -i 's/^%sudo\sALL.*$/%sudo ALL=(ALL:ALL) NOPASSWD: ALL/g' /etc/sudoers"''')

    @logger.catch
    def _update_hostname(self, hostname: str):
        self._run_command(rf'''"sudo hostnamectl set-hostname {hostname}"''')
        self._run_command(
            rf'''"sudo sed -i 's/^127.0.1.1.*$/127.0.1.1 {hostname}/g' /etc/hosts"''')
        self.hostname = hostname

    @logger.catch
    def _add_sudo_user_with_ssh_key(self, username: str, public_ssh_key: str):
        self._run_command(
            rf'''"sudo useradd -m -s /bin/bash -G sudo {username}"''')
        self._run_command(rf'''"sudo mkdir -p /home/{username}/.ssh -m 0700 \
        && sudo chown -R {username}. /home/{username}/.ssh \
        && echo '{public_ssh_key}' | sudo tee /home/{username}/.ssh/authorized_keys \
        && sudo chmod 0600 /home/{username}/.ssh/authorized_keys \
        && sudo chown {username}. /home/{username}/.ssh/authorized_keys"''')

    @logger.catch
    def _read_vault_secret(self, vault_url: str, vault_token: str, path: str):
        vault_api_client = hvac.Client(url=vault_url, token=vault_token)
        return vault_api_client.secrets.kv.v2.read_secret_version(path)['data']['data']

    @logger.catch
    def _change_user_password(self, username: str, password: str):
        self._run_command(
            rf'''"echo -e '{password}\n{password}' | sudo passwd {username}"''')

    @logger.catch
    def _update_ssh_port(self, port: int):
        self._run_command(
            rf'''"sudo sed -i 's/^.*Port.*$/Port {port}/g' /etc/ssh/sshd_config"''')
        logger.info(f'ssh port updated to {port}')
        self._restart_systemd_service('sshd')
        logger.info(f'ssh service restarted')

    @logger.catch
    def _restart_systemd_service(self, name: str):
        self._run_command(rf'''"sudo systemctl restart {name}"''')

    @logger.catch
    def _write_vault_secret(self, vault_url: str, vault_token: str, path: str, secret: dict):
        vault_api_client = hvac.Client(url=vault_url, token=vault_token)
        return vault_api_client.secrets.kv.v2.create_or_update_secret(
            path=path,
            secret=secret)

    @logger.catch
    def _update_rundeck_minio_nodes_file(self, minio_url: str, access_key: str, secret_key: str,
                                         local_file_path: str, bucket: str, minio_file_name: str):
        api_client = Minio(minio_url, access_key, secret_key)
        api_client.fget_object(
            bucket, minio_file_name, local_file_path,
        )

        server_credentials = {self.hostname: {'hostname': f'{self.ip}:{self.port}',
                                              'nodename': self.hostname,
                                              'ssh-keypath': 'keys/ssh/ansible/privateKey',
                                              'sshport': self.port,
                                              'username': 'rundeck'}}
        self._merge_yaml_file_content_with_json_object(local_file_path,
                                                       server_credentials)
        self._put_file_to_minio(minio_url, access_key, secret_key,
                                local_file_path, bucket, minio_file_name)

    @logger.catch
    def _update_ansible_minio_inventory_file(self, minio_url: str, access_key: str, secret_key: str,
                                             local_file_path: str, bucket: str, minio_file_name: str):
        api_client = Minio(minio_url, access_key, secret_key)
        api_client.fget_object(
            bucket, minio_file_name, local_file_path,
        )

        server_credentials = {'all': {'hosts': {self.hostname: {'ansible_host': self.ip,
                                                                'ansible_port': self.port,
                                                                'ansible_user': 'rundeck'}}}}
        self._merge_yaml_file_content_with_json_object(local_file_path,
                                                       server_credentials)
        self._put_file_to_minio(minio_url, access_key, secret_key,
                                local_file_path, bucket, minio_file_name)

    @logger.catch
    def _merge_yaml_file_content_with_json_object(self, local_file_path: str,
                                                  json_object: dict):
        with open(local_file_path, 'r') as nodes_yaml_file:
            nodes_object = yaml.full_load(nodes_yaml_file)
            new_nodes_object = jsonmerge.merge(nodes_object, json_object)
        with open(local_file_path, 'w') as nodes_yaml_file:
            yaml.dump(new_nodes_object, nodes_yaml_file, allow_unicode=True)

    @logger.catch
    def _run_command(self, command: str, print_it: bool = 1):
        if not self.ssh_key:
            command_prefix = rf'''sshpass -p "{self.password
            }" ssh -o StrictHostKeyChecking=no {self.username}@{self.ip} -p {self.port}'''
            zx.run_shell(rf'''{command_prefix} {command}''', print_it)
        else:
            command_prefix = rf'''ssh -o StrictHostKeyChecking=no {
            self.username}@{self.ip} -i ~/.ssh/ansible -p {self.port}'''
            zx.run_shell(rf'''{command_prefix} {command}''', print_it)

    @logger.catch
    def _put_file_to_minio(self, url: str, access_key: str, secret_key: str,
                           local_file_path: str, bucket: str, minio_file_name: str):
        api_client = Minio(url, access_key, secret_key)
        api_client.fput_object(
            bucket, minio_file_name, local_file_path,
        )

    @logger.catch
    def _update_users_passwords(self, users: tuple, password: str):
        for ssh_user in users:
            self._change_user_password(ssh_user, password)

    @logger.catch
    def _update_ssh_credentials(self, hostname, vault_tenant, vault_token, vault_url):
        try:
            remote_server_ssh_info = self._read_vault_secret(vault_url,
                                                             vault_token,
                                                             f'tenant/{vault_tenant}/server/{hostname}/ssh')
            self._update_users_passwords(
                ('root', 'abukamel'), remote_server_ssh_info['password'])
            self._update_ssh_port(int(remote_server_ssh_info['port']))
            self.port = int(remote_server_ssh_info['port'])
            self.password = remote_server_ssh_info['password']
        except (Exception, hvac.exceptions.InvalidPath):
            print('Secret not found, creating vault secret')
            new_ssh_port = random.randrange(40000, 49999)
            new_ssh_password = ''.join(random.choice(
                string.ascii_letters + string.digits) for _ in range(32))
            self._update_users_passwords(
                ('root', 'abukamel'), new_ssh_password)
            self._update_ssh_port(new_ssh_port)
            self.port = new_ssh_port
            self.password = new_ssh_password
            self._write_vault_secret(vault_url,
                                     vault_token,
                                     path=f'tenant/{vault_tenant}/server/{hostname}/ssh',
                                     secret=dict(ip=self.ip,
                                                 password=self.password,
                                                 user='root',
                                                 port=str(self.port)))

    @logger.catch
    def _get_file_from_minio(self, url: str, access_key: str, secret_key: str,
                             local_file_path: str, bucket: str, minio_file_name: str):
        api_client = Minio(url, access_key, secret_key)
        api_client.fget_object(
            bucket, minio_file_name, local_file_path,
        )

    @logger.catch
    def print_final_ssh_server_info(self):
        print(
            'Copy and paste the following commands to add server to your local ssh config')
        print('command storm -v || pip3 install stormssh')
        print(
            rf'storm add --id_file="~/.ssh/id_ed25519" {self.hostname} {self.username}@{self.ip}:{self.port}')
