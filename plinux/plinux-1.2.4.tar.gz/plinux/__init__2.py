import functools
import inspect
import json
import logging
import os
import platform
import shlex
import socket
import time
import warnings
from dataclasses import dataclass
from subprocess import Popen, PIPE, TimeoutExpired
from typing import Any, Union

from paramiko import SSHClient, ssh_exception, AutoAddPolicy

logger_name = 'Plinux'
logger = logging.getLogger(logger_name)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(fmt='%(asctime)-15s | %(levelname)s | %(name)s | %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')

# Console logger
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)


@dataclass
class ResponseParser:
    """Bash response parser"""

    response: Any

    @property
    def stdout(self) -> Union[str, dict]:
        return self.response[1]

    @property
    def stderr(self) -> str:
        return self.response[2]

    @property
    def exited(self) -> int:
        try:
            return int(self.response[0])
        except TypeError:
            return 0

    @property
    def ok(self) -> bool:
        return self.response[0] == 0

    @property
    def command(self) -> str:
        return self.response[3]

    @property
    def motd(self) -> str:
        """Get message of the day"""
        return self.response[4]

    def json(self):
        return json.loads(self.stdout)


class Plinux:
    """Base class to work with linux"""

    def __init__(self,
                 host: str = '127.0.0.1',
                 username: str = None,
                 password: str = None,
                 port: int = 22,
                 logger_enabled: bool = True):
        """Create a client object to work with linux host"""

        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.logger = logger
        self.logger.disabled = not logger_enabled

    def __str__(self):
        return f'Local host: {self.get_current_os_name()}\n' \
               f'Remote IP: {self.host}\n' \
               f'Username: {self.username}\n' \
               f'Password: {self.password}\n' \
               f'Host availability: {self.is_host_available()}\n' \
               f'Credentials are correct: {self.is_credentials_valid()}'

    def is_host_available(self, port: int = 0, timeout: int = 5):
        """Check remote host is available using specified port"""

        # return self._client().get_transport().is_active()
        port_ = port or self.port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((self.host, port_))
            return False if result else True

    def list_all_methods(self):
        """Returns all available public methods"""
        return [method for method in dir(self) if not method.startswith('_')]

    def run_cmd_local(self, cmd: str, timeout: int = 60):
        """Main function to send commands using subprocess

        :param cmd: string, command
        :param timeout: timeout for command
        :return: Decoded response

        """

        with Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE) as process:
            # process.wait(timeout)
            try:
                self.logger.info(f'COMMAND: "{cmd}"')
                stdout, stderr = process.communicate(timeout=timeout)
                data = (stdout + stderr).decode().strip()
                self.logger.info(f'RESULT: "{data}"')
                return data
            except TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                data = stdout + stderr
                self.logger.exception('Connection timeout')
                return data.decode()

    def _client(self, sftp: bool = False, timeout: int = 15):
        """https://www.paramiko.org/"""

        client = SSHClient()
        client.set_missing_host_key_policy(AutoAddPolicy())

        try:
            client.connect(self.host, username=self.username, password=self.password, timeout=timeout)

            if sftp:
                return client.open_sftp()
            return client
        except ssh_exception.AuthenticationException as err:
            self.logger.exception('Authentication error')
            raise err
        except ssh_exception.NoValidConnectionsError as err:
            # Fixme add more sophisticated verification
            self.logger.exception('There is no valid connection. Try to use "_local" or vice versa method.')
            raise err
        except TimeoutError as err:
            self.logger.exception('Timeout exceeded.')
            raise err

    def run_cmd(self, cmd: str, sudo: bool = False, timeout: int = 30) -> ResponseParser:
        """Base method to execute SSH command on remote server

        :param cmd: SSH command
        :param sudo: Execute specified command as sudo user
        :param timeout: Execution timeout
        :return: ResponseParser class
        """

        client = self._client()

        try:
            command = f"sudo -S -p '' -- sh -c '{cmd}'" if sudo else cmd
            self.logger.info(f'[{self.host}] ' + command)

            stdin, stdout, stderr = client.exec_command(command, timeout=timeout)

            if sudo:
                stdin.write(self.password + '\n')
                stdin.flush()

            # Get exit code
            exited = stdout.channel.recv_exit_status()

            # Get STDOUT
            stdout = stdout.read().decode().strip()
            out = stdout if stdout else None
            self.logger.info(f'{exited}: {out}')

            # Get STDERR
            stderr = stderr.read().decode().strip()

            # Clear stderr if password prompt detected
            if '[sudo] password for' in stderr:
                stderr = None

            err = stderr if stderr else None
            if err:
                self.logger.error(err)

            response = exited, out, err, command
            return ResponseParser(response)
        finally:
            client.close()

    # noinspection PyTypeChecker
    def run_cmd_session(self, cmds: tuple = None, buffer_size: int = 4096) -> ResponseParser:
        """Send command using session. Returns entity name if noe command provided.

        :param cmds: List of commands to execute
        :param buffer_size: Bytes size to receive. Default 4096.
        :return:
        """

        client = self._client()

        with client.invoke_shell() as ssh:
            self.logger.info(f'[{self.host}] ' + ' -> '.join(cmds))

            ssh.settimeout(5)
            motd = ssh.recv(buffer_size).decode().strip()

            result = {}

            # Send command one-by-one
            for cmd in cmds:
                ssh.send(f'{cmd}\n')
                time.sleep(0.5)
                response = ssh.recv(buffer_size).decode().splitlines()
                result[cmd] = response[1:-1]

            response = None, result, result, cmds, motd
            return ResponseParser(response)

    @staticmethod
    def get_current_os_name():
        return platform.system()

    @property
    def __sudo_cmd(self):
        return f'sudo -S <<< {self.password}'

    def is_credentials_valid(self):
        try:
            self.run_cmd('whoami')
            return True
        except ssh_exception.AuthenticationException:
            self.logger.exception(f'Invalid credentials ({self.username, self.password})')
            return False

    def get_os_version(self):
        return self.run_cmd('lsb_release -a')

    def get_ip(self):
        return self.run_cmd('hostname -I')

    def get_hostname(self):
        return self.run_cmd('hostname')

    def get_package_version(self, package: str) -> ResponseParser:
        """Get package (.deb) version

        :param package: Deb name
        :return:
        """

        cmd = f"dpkg -s {package} | grep Version | awk '{{print $2}}'"
        return self.run_cmd(cmd)

    def get_installed_packages_versions(self) -> dict:
        """Get all installed packages and their versions"""

        response = self.run_cmd('dpkg --list | grep ii').stdout
        result = {package.split()[1].removesuffix(':amd64'): package.split()[2] for package in response.splitlines()}
        return result

    def is_package_upgradable(self, package: str, show_version: bool = True) -> Union[bool, str]:
        """Check package newer version. Return it if exists.

        :param show_version:
        :param package:
        :return:
        """

        cmd = fr"apt list --installed {package} 2>/dev/null | egrep -o '\[.*\]'"
        result = self.run_cmd(cmd).stdout

        try:
            if 'upgradable' in result:  # There is newer package version
                if show_version:  # Get precise version
                    new_version = result.split('to: ')[1].removesuffix(']')
                    return new_version
                return True
        except TypeError:
            self.logger.error(f'Package ({package}) not found on destination server.')
        return False

    # FIXME
    def change_hostname(self, name: str):
        cmd = f'{self.__sudo_cmd} -- sh -c "echo {name} > /etc/hostname; hostname -F /etc/hostname"'
        self.run_cmd(cmd)
        cmd = f"""{self.__sudo_cmd} -- sh -c 
        'sed -i "/127.0.1.1.*/d" /etc/hosts; echo "127.0.1.1 {name}" >> /etc/hosts'"""
        return self.run_cmd(cmd)

    def get_date(self):
        return self.run_cmd('date')

    # ---------- Service management ----------
    def get_service(self, name: str):
        """Get whole service info"""

        return self.run_cmd(f'systemctl status {name}')

    def get_service_status(self, name: str) -> str:
        """Get service status"""

        cmd = f'systemctl is-active {name}'
        return self.run_cmd(cmd).stdout

    def is_service_active(self, name: str) -> bool:
        cmd = f'systemctl is-active --quiet {name}'
        return self.run_cmd(cmd).ok

    def stop_service(self, name: str):
        return self.run_cmd(f'systemctl stop {name}', sudo=True)

    def kill_service(self, name: str):
        return self.run_cmd(f'systemctl kill {name}', sudo=True)

    def start_service(self, name: str):
        return self.run_cmd(f'systemctl start {name}', sudo=True)

    def restart_service(self, name: str):
        return self.run_cmd(f'systemctl restart {name}', sudo=True)

    def get_service_journal(self, name: str):
        return self.run_cmd(f'journalctl -u {name}', sudo=True)

    def list_active_services(self, no_legend: bool = True, all_services: bool = False):
        """
        List all active services and it's status

        :param no_legend:
        :param all_services: To see loaded but inactive units, too
        :return:
        """

        cmd = 'systemctl list-units -t service'
        if no_legend:
            cmd += ' --no-legend'
        if all_services:
            cmd += ' --all'
        return self.run_cmd(cmd)

    def enable(self, name: str):
        """Enable service using systemctl"""

        return self.run_cmd(f'systemctl enable {name}', sudo=True)

    def disable(self, name: str):
        """Disable service using systemctl"""

        return self.run_cmd(f'systemctl disable {name}', sudo=True)

    def is_enabled(self, name: str) -> bool:
        """Get unit service status

        :param name: Service name
        :return:
        """

        response = self.run_cmd(f'systemctl is-enabled {name}').stdout

        try:
            return True if 'enabled' in response else False
        except TypeError:
            return False

    def get_pid(self, name: str, sudo: bool = False) -> Union[int, list]:
        """Get process pid

        :param name: Process name
        :param sudo: To elevate permission (in CentOS)
        """

        result = self.run_cmd(f'pidof {name}', sudo=sudo).stdout

        try:
            return int(result)
        except ValueError:
            return list(map(int, result.split()))
        except TypeError as err:
            self.logger.exception(f'Cannot get pid ({name}). Try to use sudo.')
            raise err

    def get_netstat_info(self, params: str = ''):
        """Get netstat info

        Necessary to install net-tool: "yum -y install net-tools"

        :param params: "ltpu" - Active Internet connections (only servers)
        :return:
        """

        cmd_ = 'netstat' if not params else f'netstat -{params}'
        return self.run_cmd(cmd_)

    # ----------- File and directory management ----------
    def check_exists(self, path: str, sudo: bool = False) -> bool:
        r"""Check file and directory exists.

        For windows path: specify network path in row format or use escape symbol.
        You must be connected to the remote host.
        Usage: check_exists('\\\\172.16.0.25\\d$\\New Text Document.txt')

        For linux path: linux style path.
        Usage: check_exists('/home/user/test.txt')

        :param path: Full path to file/directory
        :param sudo:
        :return:
        """

        # Linux
        if '/' in path:
            cmd = f'test -e {path}'
            response = self.run_cmd(cmd, sudo=sudo)
            return response.ok
        # Windows
        elif '\\' in path:
            return os.path.exists(path)
        raise SyntaxError('Incorrect method usage. Check specified path.')

    def cat_file(self, path: str, sudo: bool = False):
        return self.run_cmd(f'cat {path}', sudo=sudo)

    def get_json(self, path: str, sudo: bool = False, pprint: bool = False) -> dict:
        """Read JSON file as string and pretty print it into console"""

        file = self.cat_file(path, sudo=sudo)
        jsoned = json.loads(file.stdout)
        if pprint:
            print(json.dumps(jsoned, indent=4), sep='')
        return jsoned

    def create_file(self, path: str, sudo: bool = True):
        return self.run_cmd(f'touch {path}', sudo=sudo)

    def clear_file(self, path: str, sudo: bool = True):
        """Clear file.

        :param path:
        :param sudo:
        :return:
        """

        return self.run_cmd(f'cat /dev/null > {path}', sudo=sudo)

    def get_file_permissions(self, path: str, human: bool = False, sudo: bool = False):
        """Display file or file system status.

        :param path: File path
        :param human: Access rights in human readable form otherwise in in octal
        :param sudo:
        :return:
        """

        cmd = f'stat -c %A {path}' if human else f'stat -c %a {path}'
        return self.run_cmd(cmd, sudo=sudo)

    def get_file_size(self, path: str, sudo: bool = False):
        """Get file size

        :param sudo:
        :param path: File path
        :return: size in bytes
        """

        return self.run_cmd(f'stat -c "%s" {path}', sudo=sudo)

    def grep_line_in_file(self, path: str, string: str, directory: bool = False, sudo: bool = True):
        """Grep line in file or directory

        :param sudo:
        :param path: File/directory path
        :param string: string pattern to grep
        :param directory: If True - grep in directory with files
        :return:
        """

        if directory:
            return self.run_cmd(f'grep -rn "{string}" {path}', sudo=sudo)
        return self.run_cmd(f'grep -n "{string}" {path}', sudo=sudo)

    def change_line_in_file(self, path: str, old: str, new: str, sudo: bool = True):
        """Replace line and save file.

        :param sudo:
        :param path: File path
        :param old: String to replace
        :param new: New string
        :return:
        """

        return self.run_cmd(f'sed -i "s!{old}!{new}!" {path}', sudo=sudo)

    def delete_line_from_file(self, path: str, string: str, sudo: bool = True):
        return self.run_cmd(f"sed -i '/{string}/d' {path}", sudo=sudo)

    def get_last_file(self, directory: str = '', name: str = '', sudo: bool = True):
        """Get last modified file in a directory

        :param sudo:
        :param name: Filename to grep
        :param directory: Directory path to precess. Home by default
        :return:
        """

        directory_ = directory or f'/home/{self.username}'
        cmd = f'ls {directory_} -Art| grep {name} | tail -n 1' if name else f'ls {directory} -Art | tail -n 1'
        return self.run_cmd(cmd, sudo=sudo)

    def remove(self, path: str, sudo: bool = True):
        """Remove file(s) and directories

        Usage:\n
        path=/opt/1 remove the directory\n
        path=/opt/1/* remove all file in the directory\n
        path=/opt/1/file.txt remove specified file in the directory\n

        :param sudo:
        :param path: Path to a file or directory.
        """

        return self.run_cmd(f'for file in {path}; do rm -rf "$file"; done', sudo=sudo)

    def extract_files(self, src: str, dst: str, mode: str = 'tar', quite: bool = True, sudo: bool = False):
        """Extract file to specified directory

        :param sudo:
        :param src: Full path to archive (with extension)
        :param dst:
        :param mode: "tar", "zip"
        :param quite: Suppress list of unpacked files
        :return:
        """

        unzip_cmd = f'unzip -q {src} -d {dst}' if quite else f'unzip {src} -d {dst}'
        tar_cmd = f'tar -xzvf {src}.tar.gz -C {dst}'

        cmd = tar_cmd if mode == 'tar' else unzip_cmd

        return self.run_cmd(cmd, sudo=sudo)

    def copy_file(self, src: str, dst: str, sudo: bool = True):
        """Copy file to another location

        :param sudo:
        :param src: Source full path
        :param dst: Destination
        :return:
        """

        return self.run_cmd(f'cp {src} {dst}', sudo=sudo)

    def get_md5(self, path: str, raw: bool = False, sudo: bool = True):
        """
        Get file md5

        :param sudo:
        :param path: File path
        :param raw: Return md5 sum only (not Response object)
        """

        result = self.run_cmd(f'md5sum {path}', sudo=sudo).stdout
        if raw:
            return result.split(path)[0].strip()
        return result

    def get_processes(self):
        """Get processes using PS"""

        return self.run_cmd('ps -aux')

    #  ----------- Power management -----------
    def reboot(self):
        return self.run_cmd('shutdown -r now', sudo=True)

    def shutdown(self):
        return self.run_cmd('shutdown -h now', sudo=True)

    #  ----------- Directory management -----------
    def create_directory(self, path: str, sudo: bool = True):
        return self.run_cmd(f'mkdir {path}', sudo=sudo)

    def list_dir(self, path: str, params=None, sudo: bool = False):
        """List directory

        :param path: Directory path
        :param params: Additional params. For example: "la"
        :param sudo:
        :return:
        """

        cmd = f'ls {path} -{params}' if params else f'ls {path}'
        return self.run_cmd(cmd, sudo=sudo)

    def count_files(self, path: str):
        """Count files number in directory.

        :param path:
        :return:
        """
        return self.run_cmd(f'ls {path} | wc -l')

    #  ----------- SFTP -----------
    @property
    def sftp(self):
        return self._client(sftp=True)

    def upload(self, local: str, remote: str):
        r"""Upload file/dir to the host and check exists after.

        Usage: tool.upload(r'd:\python_tutorial.pdf', '/home/user/python_tutorial.pdf'')

        :param local: Source full path
        :param remote: Destination full path
        :return: bool
        """

        self.sftp.put(local, remote, confirm=True)
        self.logger.info(f'Uploaded {local} to {remote}')
        return self.exists(remote)

    def download(self, remote: str, local: str, callback=None) -> bool:
        r"""Download a file from the current connection to the local filesystem and check exists after.

        Usage: tool.download('/home/user/python_tutorial.pdf', 'd:\dust\python_tutorial.pdf')

        :param remote: Remote file to download. May be absolute, or relative to the remote working directory.
        :param local: Local path to store downloaded file in, or a file-like object
        :param callback: func(int, int)). Accepts the bytes transferred so far and the total bytes to be transferred
        :return: bool
        """

        self.sftp.get(remote, local, callback=callback)
        self.logger.info(f'Downloaded {remote} to {local}')
        return self.exists(local)

    def change_password(self, new_password: str):
        """Change password

        BEWARE USING! You'll lost connection to a server after completion.

        echo username:new_password | sudo chpasswd

        :param new_password: New password with no complex check.
        :return:
        """

        return self.run_cmd(f'sudo -S <<< {self.password} -- sh -c "echo {self.username}:{new_password} | chpasswd"')

    # ---------- Disk ----------
    def get_disk_usage(self, mount_point: str = '/'):
        """Get disk usage

        :param mount_point:
        :return:
        """

        cmd = f'df {mount_point} -h' if mount_point else 'df -h'
        return self.run_cmd(cmd)

    def get_free_space(self, mount_point: str = '/', *params):
        """Get free space.

        By default with -h parameter.

        >>> self.get_free_space('')  # get all info
        >>> self.get_free_space('/opt')  # df / -h --output=avail | tail -n 1
        >>> self.get_free_space('/opt', '--block-size=K')  # df /opt --block-size=K --output=avail | tail -n 1
        >>> self.get_free_space('/opt', '-h', '-H')  # df /opt -h -H --output=avail | tail -n 1

        :param mount_point:
        :return:
        """

        params_ = shlex.join(params) if params else '-h'
        cmd = f'df {mount_point} {params_} --output=avail | tail -n 1'

        return self.run_cmd(cmd)

    def debug_info(self):
        """Show debug log. Logger must be enabled"""

        self.logger.info('Linux client created.')
        self.logger.info(f'Local host: {self.get_current_os_name()}')
        self.logger.info(f'Remote IP: {self.host}')
        self.logger.info(f'Username: {self.username}')
        self.logger.info(f'Password: {self.password}')
        self.logger.info(f'Available: {self.is_host_available()}')
        self.logger.info(f'Available: {self.is_host_available()}')

    # ---------- User management ----------
    def kill_user_session(self, name: str):
        """
        Kill all user's ssh session and processes

        :param name: user name
        :return:
        """

        return self.run_cmd(f'pkill -9 -u {name}', sudo=True)

    def sqlite3(self, db: str, sql: str, sudo: bool = False, params: str = ''):
        """Simple work with the SQLite. Can use ".json" in response.

        :param db: DB path
        :param sql: SQL request
        :param params: i.e. "-line -header", "-csv"
        :param sudo:
        :return:
        """

        cmd = f'sqlite3 {db} "{sql}" {params}'
        return self.run_cmd(cmd, sudo=sudo)

    # OpenSSL
    def validate_ssl_key(self, path: str) -> bool:
        """Validate key

        :param path: key path
        :return:
        """

        result = self.run_cmd(f'openssl rsa -in {path} -check')
        return True if 'RSA key ok' in result.stdout else False

    def get_ssl_md5(self, path: str):
        """Get cert or key md5

        :param path:
        :return:
        """

        return self.run_cmd(f'openssl x509 -noout -modulus -in {path} | openssl md5')

    def get_ssl_certificate(self, x509: bool = True, port: int = 443):
        """Get certificate info

        :param x509: Get x509 if specified
        :param port: 443 by default
        :return:
        """

        cmd = f'openssl s_client -showcerts -connect {self.host}:{port} </dev/null'
        if x509:
            cmd += ' | openssl x509 -text'
        return self.run_cmd(cmd)

    def get_ssl_fingerprint(self, path: str, algorithm: str = 'sha1', brief: bool = True) -> str:
        """Get SSL/TLS thumbprint

        :param path:
        :param algorithm:
        :param brief: Get fingerprint in "C3587D1515236324AB03686BF7F23B015D284351" format
        :return:
        """

        cmd_general = f'openssl x509 -noout -fingerprint -{algorithm} -inform pem -in {path}'
        if brief:
            cmd = f'{cmd_general} | awk -F "=" \'{{gsub(":","");print $2}}\''
        else:
            cmd = f'{cmd_general} | awk -F "=" \'{{print $2}}\''
        return self.run_cmd(cmd).stdout

    def get_ssl_serial(self, path: str) -> str:
        """Get serial number from certificate

        :param path:
        :return:
        """

        cmd_general = f'openssl x509 -noout -serial -inform pem -in {path}'  # | awk -F "=" \'{{print $2}}\''
        cmd = f'{cmd_general} | awk -F "=" \'{{print $2}}\''

        return self.run_cmd(cmd).stdout

    # Aliases
    ps = get_processes
    ls = list_dir
    cp = copy_file
    date = get_date
    os = get_os_version
    exists = check_exists
    netstat = get_netstat_info
    start = start_service
    stop = stop_service
    status = get_service_status
    restart = restart_service
    version = get_os_version
    rm = remove
    chpasswd = change_password
    count = count_files
    stat = get_file_permissions
    md5 = get_md5


class local_execution:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.function = func

    def __call__(self, *args, **kwargs):

        # If you specify deprecation reason
        if isinstance(self.function, str):

            fmt = 'Deprecated function/method "{name}" has been invoked: {reason}.'
            if inspect.isclass(args[0]):
                fmt = 'Deprecated class has been invoked "{name}": {reason}.'

            @functools.wraps(args[0])
            def wrapper(*args_, **kwargs_):
                warnings.simplefilter('always', DeprecationWarning)
                warnings.warn(fmt.format(name=args[0].__name__, reason=self.function),
                              category=DeprecationWarning,
                              stacklevel=2)
                warnings.simplefilter('default', DeprecationWarning)

                return args[0](*args_, **kwargs_)

            return wrapper

        # Used is no 'reason' specified
        elif inspect.isclass(self.function) or inspect.isfunction(self.function):

            fmt = 'Deprecated function/method "{name}" has been invoked.'
            if inspect.isclass(self.function):
                fmt = 'Deprecated class has been invoked "{name}".'

            warnings.simplefilter('always', DeprecationWarning)
            warnings.warn(fmt.format(name=self.function.__name__), category=DeprecationWarning, stacklevel=2)
            warnings.simplefilter('default', DeprecationWarning)

            return self.function(*args, **kwargs)
        else:
            raise TypeError(repr(type(self.function)))
