import os
from argparse import ArgumentError
from string import Template

import yaml


class Docker(object):
    @staticmethod
    def _get_main_docker_compose_service():
        for name, info in Docker._gel_all_docker_compose_services().items():
            if 'build' in info:
                return name

    @staticmethod
    def _gel_all_docker_compose_services():
        docker_compose_file = None
        for dkf in ['docker-compose.yml', 'docker-compose.yaml']:
            if os.path.exists(dkf):
                docker_compose_file = dkf
                break
        if docker_compose_file is not None:
            with open(docker_compose_file) as file:
                return yaml.load(file, Loader=yaml.FullLoader)['services']
        return {}

    @staticmethod
    def command_interceptor(command, *remainders, service=None, **env_vars):
        if service is None:
            remainders = list(remainders)
            if remainders and remainders[0] in Docker._gel_all_docker_compose_services():
                service = remainders[0]
                remainders.pop(0)
            else:
                service = Docker._get_main_docker_compose_service()
        elif service not in Docker._gel_all_docker_compose_services():
            raise ArgumentError(None, 'No such service: "%s"' % service)

        env_vars = ' '.join(f'--env {env}={env_vars[env]}' for env in env_vars.keys())
        if env_vars:
            service = f'{env_vars} {service}'
        return Template(command).safe_substitute(service=service), tuple(remainders)
