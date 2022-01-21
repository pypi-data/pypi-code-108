from os.path import expanduser
import os
from socket import SOCK_STREAM, AF_INET, socket
from typing import List
import click
from imecilabt.gpulab.model.job2 import Job


def sh_quote_arg(c: str) -> str:
    if "'" not in c:
        if ' ' not in c and '"' not in c and '$' not in c:
            return c
        else:
            return f"'{c}'"
    else:
        c = c.replace("'", """'"'"'""")
        return f"'{c}'"


def command_array_to_str(command: List[str]) -> str:
    return ' '.join([sh_quote_arg(c) for c in command])


# def _get_short_file_short_hash_id(filename: str) -> str:
#     with open(filename, 'r') as f:
#         return urlsafe_b64encode(hashlib.sha1(f.read().encode('utf-8')).digest()).decode('utf-8').replace('=', '')[0:10]
#
#
# def _get_str_short_hash_id(content: str) -> str:
#     return urlsafe_b64encode(hashlib.sha1(content.encode('utf-8')).digest()).decode('utf-8').replace('=', '')[0:10]


def _ensure_ssh_config_include(debug: bool = False) -> str:
    ssh_config_filename = expanduser('~/.ssh/config')
    ssh_config_gpulab_filename_base = 'gpulab_hosts_config'
    ssh_config_gpulab_filename = expanduser(f'~/.ssh/{ssh_config_gpulab_filename_base}')

    ssh_dir = expanduser('~/.ssh/')
    if not os.path.exists(ssh_dir):
        os.mkdir(ssh_dir, 0o700)
        click.secho(f'Created {ssh_dir}')

    # Check if Host already added
    must_add_include = True
    if os.path.exists(ssh_config_filename):
        created_ssh_config = False
        with open(ssh_config_filename, 'r') as f:
            for line in f:
                if line.lstrip().startswith(f'Include {ssh_config_gpulab_filename_base}'):
                    must_add_include = False
                    break
    else:
        created_ssh_config = True

    if must_add_include:
        with open(ssh_config_filename, 'a') as f:
            f.write(f'\n')
            f.write(f'Host *\n')
            f.write(f'   Include {ssh_config_gpulab_filename_base}\n')
            f.write(f'\n')
        if debug:
            if created_ssh_config:
                click.secho(f'Added include to {ssh_config_filename}')
            else:
                click.secho(f'Created {ssh_config_filename}')

    return ssh_config_gpulab_filename


def job_ssh_config_hostname(job: Job, use_proxy: bool) -> str:
    if use_proxy:
        return f'gpulab-{job.short_uuid}-proxy'
    else:
        return f'gpulab-{job.short_uuid}'


def _job_ssh_config_exists(job: Job, ssh_config_gpulab_filename: str):
    if os.path.exists(ssh_config_gpulab_filename):
        with open(ssh_config_gpulab_filename, 'r') as f:
            for line in f:
                if line.startswith(f'Host={job_ssh_config_hostname(job, True)}') or \
                        line.startswith(f'Host={job_ssh_config_hostname(job, False)}'):
                    return True
    return False


def set_jobs_ssh_config(login_pem_filename: str, jobs: List[Job], debug: bool = False):
    ssh_config_gpulab_filename = _ensure_ssh_config_include(debug)
    with open(ssh_config_gpulab_filename, 'w') as f:
        for job in jobs:
            _actual_write_job_ssh_config(f, login_pem_filename, job, proxy=False)
            _actual_write_job_ssh_config(f, login_pem_filename, job, proxy=True)
    if debug:
        click.secho(f'Rewrote {len(jobs)} jobs in {ssh_config_gpulab_filename}')
    os.chmod(ssh_config_gpulab_filename, 0o700)


def add_job_ssh_config(login_pem_filename: str, job: Job, return_proxy_fake_hostname: bool, debug: bool = False) -> str:
    ssh_config_gpulab_filename = _ensure_ssh_config_include(debug)
    if _job_ssh_config_exists(job, ssh_config_gpulab_filename):
        return job_ssh_config_hostname(job, return_proxy_fake_hostname)

    created = os.path.exists(ssh_config_gpulab_filename)
    with open(ssh_config_gpulab_filename, 'a') as f:
        fake_hostname = _actual_write_job_ssh_config(f, login_pem_filename, job, proxy=False)
        fake_hostname_proxy = _actual_write_job_ssh_config(f, login_pem_filename, job, proxy=True)
    if created:
        os.chmod(ssh_config_gpulab_filename, 0o700)
        click.secho(f'Created {ssh_config_gpulab_filename} for job {job.uuid}')
    else:
        click.secho(f'Appended {ssh_config_gpulab_filename} with job {job.uuid}')
    return fake_hostname if not return_proxy_fake_hostname else fake_hostname_proxy


def _actual_write_job_ssh_config(f, login_pem_filename: str, job: Job, *, proxy: bool) -> str:
    fake_hostname = job_ssh_config_hostname(job, proxy)
    f.write(f'\n')
    f.write(f'Host={fake_hostname}\n')
    f.write(f'   Hostname {job.state.resources.ssh_host}\n')
    f.write(f'   Port {job.state.resources.ssh_port}\n')
    f.write(f'   User {job.state.resources.ssh_username}\n')
    if proxy:
        f.write(f'   ProxyCommand ssh -i "{login_pem_filename}" -oPort={job.state.resources.ssh_port} '
                f'"{job.state.resources.ssh_proxy_username}@{job.state.resources.ssh_proxy_host}" -W %h:%p\n')
        # Note: ssh_config now supports ProxyJump, which looks nicer than ProxyCommand.
        #       But I'm not sure if all currently used openssh versions already support it.
    f.write(f'   IdentityFile "{login_pem_filename}"\n')
    f.write(f'   IdentitiesOnly yes\n')  # use only IdentityFile specified here, not agent provided IDs
    f.write(f'   PubkeyAuthentication yes\n')
    f.write(f'   ChallengeResponseAuthentication no\n')
    f.write(f'   HostbasedAuthentication no\n')
    f.write(f'   GSSAPIAuthentication no\n')
    f.write(f'   KbdInteractiveAuthentication no\n')
    f.write(f'   PasswordAuthentication no\n')
    f.write(f'\n')
    return fake_hostname


def find_free_ssh_tunnel_port(debug: bool = False) -> int:
    start_port = 2222
    port = start_port
    while port < start_port + 42:
        with socket(AF_INET, SOCK_STREAM) as s:
            free = s.connect_ex(('localhost', port)) != 0
            if debug:
                click.echo(f'port {port} is free: {free}')
            if free:
                return port
        port += 1
    raise Exception('Could not find a free port for SSH tunnel.')
