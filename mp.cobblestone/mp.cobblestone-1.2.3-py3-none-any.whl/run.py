# -----------------------------------------------------------------------
# Copyright 2020 Mina Pêcheux

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at the root of the repo.

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -----------------------------------------------------------------------

import click
import logging
import pathlib
import os
import shlex
import shutil
import subprocess
from functools import lru_cache
from time import sleep

import docker
from PyInquirer import prompt
from prompt_toolkit.validation import Validator, ValidationError

import cobblestone


logging.basicConfig(level=logging.INFO,
                    format='[Cobblestone] %(levelname)s :: %(message)s')


class PasswordNotEmptyValidator(Validator):
    def validate(self, document):
        if document.text == '':
            raise ValidationError(
                message='Your password cannot be empty!',
                cursor_position=len(document.text))  # Move cursor to end


# MAIN CONFIG ----------

CONFIGURATIONS = {
    'neo4j': {
        'subtypes': False,
        'has_rel_props': True,
        'defaults': {
            'ref_uid': 'uid',
            'ref_rel': 'rel',
            'port': 7687,
            'web_port': 7474,
            'db_user': 'neo4j',
            'db_password': '',
            'db_name': 'cobblestone'
        },
        'docker_image': 'neo4j:3.5.8',
        'docker_volumes': {
            'db/data': {'bind': '/data', 'mode': 'rw'},
            'db/logs': {'bind': '/logs', 'mode': 'rw'},
            'db/plugins': {'bind': '/plugins', 'mode': 'rw'},
        },
        'run_environment': None,
    },
    'mongo': {
        'subtypes': False,
        'has_rel_props': False,
        'defaults': {
            'ref_uid': 'uid',
            'ref_rel': 'rel',
            'port': 27017,
            'db_user': 'default',
            'db_password': 'default',
            'db_name': 'cobblestone'
        },
        'docker_image': 'mongo:4.2.11',
        'docker_volumes': {
            'db': {'bind': '/data/db', 'mode': 'rw'},
        },
        'run_environment': lambda env, dft: {
            'MONGO_INITDB_ROOT_USERNAME': env.get('DB_USER', dft.get('db_user')),
            'MONGO_INITDB_ROOT_PASSWORD': env.get('DB_PASSWORD', dft.get('db_password')),
            'MONGO_INITDB_DATABASE': env.get('DB_NAME', dft.get('db_name')),
        },
    },
    'sql': {
        'has_rel_props': True,
        'subtypes': True,
        'sqlite': {
            'docker_image': None,
            'docker_volumes': None,
            'run_environment': None,
        },
        'mysql': {
            'defaults': {
                'ref_uid': 'uid',
                'ref_rel': 'rel',
                'port': 3306,
                'db_user': 'default',
                'db_password': 'default',
                'db_name': 'cobblestone'
            },
            'docker_image': 'mysql:5.7.22',
            'docker_volumes': {
                'db': {'bind': '/var/lib/mysql', 'mode': 'rw'},
            },
            'docker_wait': 20,
            'run_environment': lambda env, dft: {
                'MYSQL_USER': env.get('DB_USER', dft.get('db_user')),
                'MYSQL_PASSWORD': env.get('DB_PASSWORD', dft.get('db_password')),
                'MYSQL_ROOT_PASSWORD': env.get('DB_PASSWORD', dft.get('db_password')),
                'MYSQL_DATABASE': env.get('DB_NAME', dft.get('db_name')),
            },
        },
        'postgres': {
            'defaults': {
                'ref_uid': 'uid',
                'ref_rel': 'rel',
                'port': 5432,
                'db_user': 'default',
                'db_password': 'default',
                'db_name': 'cobblestone'
            },
            'docker_image': 'postgres:13.1',
            'docker_volumes': {
                'db': {'bind': '/var/lib/postgresql/data', 'mode': 'rw'},
            },
            'docker_wait': 20,
            'run_environment': lambda env, dft: {
                'POSTGRES_USER': env.get('DB_USER', dft.get('db_user')),
                'POSTGRES_PASSWORD': env.get('DB_PASSWORD', dft.get('db_password')),
                'POSTGRES_DB': env.get('DB_NAME', dft.get('db_name')),
            },
        },
    },
}

AUTH_METHODS = {
    'In my database': 'db',
    'In Keycloak': 'keycloak',
}

DOCKER_NETWORK_NAME = 'cobblestone'
API_HOST = '127.0.0.1'
API_PORT = '8000'


def DOCKER_DB_CONTAINER_NAME(project_name: str) -> str:
    return f'{project_name}-database'

# ----------------------

# UTILS ----------------


def db(answers: list) -> str:
    return answers.get('database', '').lower()


def db_subtype(answers: list) -> str:
    return answers.get('database_subtype', '').lower()


@lru_cache(maxsize=128)
def get_defaults(db: str, db_subtype: str = '') -> dict:
    config = CONFIGURATIONS.get(db, {})
    if config.get('subtypes', False):
        config = config.get(db_subtype)
    return config.get('defaults', {})


def is_url(s: str) -> bool:
    return s.startswith('https://') or s.startswith('http://')

# ----------------------


def get_configuration(quick: bool = False) -> dict:
    config = {'quick': quick}

    quick_questions = [
        {
            'type': 'input',
            'name': 'api_host',
            'message': 'What is your API hostname?',
            'default': API_HOST,
        },
        {
            'type': 'input',
            'name': 'api_port',
            'message': 'What is your API port?',
            'default': API_PORT,
        },
        {
            'type': 'list',
            'name': 'database',
            'message': 'What database do you want to use?',
            'choices': ['Neo4J', 'Mongo', 'SQL'],
            'default': 0,
        },
        {
            'type': 'list',
            'name': 'database_subtype',
            'message': 'What type of SQL database?',
            'choices': ['Sqlite', 'MySQL', 'Postgres'],
            'default': 0,
            'when': lambda answers: db(answers) == 'sql',
        },
        {
            'type': 'list',
            'name': 'auth_method',
            'message': 'Where is your auth data (for OAuth2 tokens) stored?',
            'choices': ['In my database', 'In Keycloak'],
            'default': 0,
        },
    ]
    advanced_questions = [
        {
            'type': 'input',
            'name': 'db_user',
            'message': 'What\'s your DB username?',
            'default': lambda answers: get_defaults(db(answers), db_subtype(answers)).get('db_user', ''),
            'when': lambda answers: db(answers) != 'neo4j' and db_subtype(answers) != 'sqlite',
        },
        {
            'type': 'password',
            'name': 'db_password',
            'message': 'What\'s your DB password?',
            'default': lambda answers: get_defaults(db(answers), db_subtype(answers)).get('db_password', ''),
            'when': lambda answers: db(answers) != 'neo4j' and db_subtype(answers) != 'sqlite'
        },
        {
            'type': 'password',
            'name': 'db_password',
            'message': 'What\'s your DB password?',
            'default': '',
            'when': lambda answers: db(answers) == 'neo4j',
            'validate': PasswordNotEmptyValidator
        },
        {
            'type': 'input',
            'name': 'db_host',
            'message': 'What\'s your DB host URL?',
            'default': '0.0.0.0',
            'when': lambda answers: db_subtype(answers) != 'sqlite',
        },
        {
            'type': 'input',
            'name': 'db_main_port',
            'message': 'What\'s your DB bolt port?',
            'default': lambda answers: str(get_defaults(db(answers), db_subtype(answers)).get('port', '')),
            'when': lambda answers: db(answers) == 'neo4j',
        },
        {
            'type': 'input',
            'name': 'db_web_port',
            'message': 'What\'s your DB web port?',
            'default': lambda answers: str(get_defaults(db(answers), db_subtype(answers)).get('web_port', '')),
            'when': lambda answers: db(answers) == 'neo4j',
        },
        {
            'type': 'input',
            'name': 'db_main_port',
            'message': 'What\'s your DB port?',
            'default': lambda answers: str(get_defaults(db(answers), db_subtype(answers)).get('port', '')),
            'when': lambda answers: db_subtype(answers) != 'sqlite' and db(answers) != 'neo4j',
        },
        {
            'type': 'input',
            'name': 'db_name',
            'message': 'What\'s your DB name?',
            'default': lambda answers: get_defaults(db(answers), db_subtype(answers)).get('db_name', ''),
            'when': lambda answers: db(answers) == 'mongo' or db(answers) == 'sql',
        },
        {
            'type': 'input',
            'name': 'ref_uid',
            'message': 'What suffix should be used for ref fields ids?',
            'default': lambda answers: get_defaults(db(answers), db_subtype(answers)).get('ref_uid', 'uid'),
        },
        {
            'type': 'confirm',
            'name': 'has_rel_props',
            'message': 'Do you want to have relationship properties?',
            'when': lambda answers: not CONFIGURATIONS.get(db(answers), {'has_rel_props': False})['has_rel_props'],
            'default': lambda answers: CONFIGURATIONS.get(db(answers), {'has_rel_props': False})['has_rel_props'],
        },
        {
            'type': 'input',
            'name': 'ref_rel',
            'message': 'What suffix should be used for ref fields relationship properties?',
            'when': lambda answers: CONFIGURATIONS.get(db(answers), {'has_rel_props': False})['has_rel_props'] or answers.get('has_rel_props', False),
            'default': lambda answers: get_defaults(db(answers), db_subtype(answers)).get('ref_rel', 'rel'),
        },
        {
            'type': 'confirm',
            'name': 'autogenerate_token_secret',
            'message': 'Auto-generate a token secret for OAuth2?',
            'default': True,
            'when': lambda answers: answers.get('auth_method') == 'In my database',
        },
        {
            'type': 'input',
            'name': 'keycloak_host',
            'message': 'What\'s your Keycloak host?',
            'default': 'http://localhost:8080',
            'when': lambda answers: answers.get('auth_method') == 'In Keycloak',
        },
        {
            'type': 'input',
            'name': 'keycloak_realm',
            'message': 'What\'s your Keycloak realm?',
            'default': 'cobblestone',
            'when': lambda answers: answers.get('auth_method') == 'In Keycloak',
        },
        {
            'type': 'input',
            'name': 'keycloak_client_id',
            'message': 'What\'s your Keycloak Client ID?',
            'default': 'cobblestone',
            'when': lambda answers: answers.get('auth_method') == 'In Keycloak',
        },
        {
            'type': 'password',
            'name': 'keycloak_client_secret',
            'message': 'What\'s your Keycloak Client secret?',
            'when': lambda answers: answers.get('auth_method') == 'In Keycloak',
        },
    ]
    questions = quick_questions + (advanced_questions if not quick else [])

    answers = prompt(questions)
    config.update(answers)
    return config


def _load_env_util() -> dict:
    command = shlex.split('env -i bash -c "source .env && env"')
    proc = subprocess.Popen(command, stdout=subprocess.PIPE)
    env = {}
    for line in proc.stdout:
        (key, _, value) = line.decode().partition('=')
        env[key] = value.strip()
    proc.communicate()
    return env


def load_env() -> dict:
    logging.info('Loading up environment')
    env = os.environ.copy()
    env.update(_load_env_util())
    if env.get('TOKEN_SECRET_KEY') == '***':
        out = subprocess.run(
            ['openssl', 'rand', '-hex', '32'], stdout=subprocess.PIPE)
        env['TOKEN_SECRET_KEY'] = out.stdout.decode().strip()
    return env


def run_database(
    project_name: str,
    client: docker.client.DockerClient,
    env: dict,
    port: int = None
):
    if env.get('DATABASE_IS_REMOTE', 'false') == 'false':
        db = env.get('DB_TYPE')
        db_subtype = env.get('DB_SUBTYPE')
        config = CONFIGURATIONS.get(db, {})
        if config.get('subtypes', False):
            config = config.get(db_subtype)

        image_name = config.get('docker_image', None)

        # no docker image associated with this configuration:
        # aborting container run
        if image_name is None:
            return

        dft = config.get('defaults', {})
        if port is None:
            port = env.get('DB_PORT', dft['port'])
            if not isinstance(port, int):
                port = int(port)

        logging.info(f'Running database (port = {port})')
        db_container_name = DOCKER_DB_CONTAINER_NAME(project_name)
        ports = {
            f'{dft["port"]}/tcp': port
        }
        if 'web_port' in dft:
            ports[f'{dft["web_port"]}/tcp'] = dft['web_port']

        volumes = config.get('docker_volumes', None)
        volumes = {f'{os.getcwd()}/{k}': v for k, v in volumes.items()}

        run_env = config.get('run_environment', None)

        ns = client.networks.list(names=[DOCKER_NETWORK_NAME])
        if len(ns) == 0:
            client.networks.create(DOCKER_NETWORK_NAME)
        # clean currently running DB container if there is one
        try:
            c = client.containers.get(db_container_name)
            c.remove(force=True)
        except docker.errors.NotFound:
            pass
        client.containers.run(
            image_name,
            name=db_container_name,
            network=DOCKER_NETWORK_NAME,
            volumes=volumes,
            ports=ports,
            environment=run_env(env, dft) if run_env else {},
            detach=True,
            remove=False)
        docker_wait = config.get('docker_wait', 0)
        if docker_wait > 0:
            print('...')
        sleep(0.5 + docker_wait)


def stop_database(project_name: str, client: docker.client.DockerClient):
    logging.info('Stopping database')
    try:
        container = client.containers.get(
            DOCKER_DB_CONTAINER_NAME(project_name))
    except docker.errors.NotFound:
        logging.warn('No cobblestone database is currently running')
        return

    container.stop()


def run_project_container(
    project_name: str,
    client: docker.client.DockerClient,
    env: dict,
    port: int
):
    logging.info(f'Running API in docker (port = {port})')
    image_name = f'cobblestone/{project_name}'

    db = env.get('DB_TYPE')
    config = CONFIGURATIONS.get(db)
    if config.get('subtypes', False):
        db_subtype = env.get('DB_SUBTYPE')
        config = config.get(db_subtype, None)
    dft = config.get('defaults', {})
    deploy_env = config.get('deploy_environment', {})
    deploy_env.update(env)
    deploy_env['API_HOST'] = project_name
    deploy_env['API_PORT'] = 80
    deploy_env['DB_PORT'] = dft.get('port')
    if 'web_port' in dft:
        deploy_env['DB_WEB_PORT'] = dft['web_port']
    deploy_env['DB_HOST'] = f'{project_name}-database'

    client.containers.run(
        image_name,
        name=project_name,
        network=DOCKER_NETWORK_NAME,
        environment=deploy_env,
        ports={
            '80/tcp': port,
        },
        detach=True,
        remove=True)


def init_project(project_path: str, config: dict):
    j = os.path.join
    db = config['database'].lower()
    db_subtype = config.get('database_subtype', '').lower()
    api_host = config['api_host']
    api_port = config['api_port']

    # check user parameters
    token_secret = '***'
    if config.get('autogenerate_token_secret', True):
        out = subprocess.run(
            ['openssl', 'rand', '-hex', '32'], stdout=subprocess.PIPE)
        token_secret = out.stdout.decode().strip()
    auth_method = AUTH_METHODS.get(config.get('auth_method'), 'db')
    if auth_method == 'keycloak':
        keycloak_host = config.get('keycloak_host', None)
        if keycloak_host is None or len(keycloak_host) == 0 or not is_url(keycloak_host):
            logging.error(
                'Keycloak authentication requires you to specify your keycloak host.')
            return
        keycloak_realm = config.get('keycloak_realm', None)
        if keycloak_realm is None or len(keycloak_realm) == 0:
            logging.error(
                'Keycloak authentication requires you to specify your keycloak realm.')
            return
        keycloak_client_id = config.get('keycloak_client_id', None)
        if keycloak_client_id is None or len(keycloak_client_id) == 0:
            logging.error(
                'Keycloak authentication requires you to specify your keycloak client ID.')
            return
        keycloak_client_secret = config.get('keycloak_client_secret', None)
        if keycloak_client_secret is None or len(keycloak_client_secret) == 0:
            logging.error(
                'Keycloak authentication requires you to specify your keycloak client secret.')
            return

    os.makedirs(project_path)
    cobblestone_install_path = cobblestone.__path__[0]
    sub_path = os.path.join(project_path, 'cobblestone')
    os.makedirs(sub_path)

    # copy base files
    for f in ['config.py', 'security.py', 'server.py', 'tokens.py']:
        shutil.copyfile(j(cobblestone_install_path, f), j(sub_path, f))
    # copy correct database file (depending on DB config)
    shutil.copyfile(j(cobblestone_install_path, f'database_{db}.py'), j(
        sub_path, 'database.py'))

    # copy correct controllers folder
    shutil.copytree(j(cobblestone_install_path, 'controllers', db),
                    j(sub_path, 'controllers'))
    #   (+ add __init__.py)
    pathlib.Path(j(sub_path, 'controllers', '__init__.py')).touch()
    #   (+ add auth.py)
    shutil.copyfile(j(cobblestone_install_path, 'controllers', f'auth_{auth_method}.py'),
                    j(sub_path, 'controllers', 'auth.py'))
    # copy correct helpers folder (depending on DB config)
    shutil.copytree(j(cobblestone_install_path, 'helpers', db),
                    j(sub_path, 'helpers'))
    #   (+ add common helpers)
    shutil.copyfile(j(cobblestone_install_path, 'helpers', 'types.py'),
                    j(sub_path, 'helpers', 'types.py'))
    shutil.copyfile(j(cobblestone_install_path, 'helpers', 'utils.py'),
                    j(sub_path, 'helpers', 'utils.py'))
    # copy correct models folder (depending on DB config)
    shutil.copytree(j(cobblestone_install_path, 'models', db),
                    j(sub_path, 'models'))
    shutil.copyfile(j(cobblestone_install_path, 'models', '__init__.py'),
                    j(sub_path, 'models', '__init__.py'))
    #   (+ add __init__.py)
    # copy routes folder
    shutil.copytree(j(cobblestone_install_path, 'routes'),
                    j(sub_path, 'routes'))

    # copy gitignore
    shutil.copyfile(j(cobblestone_install_path, 'scripts', 'gitignore'),
                    j(project_path, '.gitignore'))
    # copy server start script
    shutil.copyfile(j(cobblestone_install_path, 'scripts', 'run-server.sh'),
                    j(project_path, 'run-server.sh'))
    # copy correct db start script (depending on DB config)
    shutil.copyfile(j(cobblestone_install_path, 'scripts', f'run-db_{db}.sh'),
                    j(project_path, 'run-db.sh'))
    # copy correct db init script (depending on DB config)
    shutil.copyfile(j(cobblestone_install_path, 'scripts', f'db_init_{db}.py'),
                    j(project_path, 'db_init.py'))
    # copy correct requirements file (depending on DB config)
    shutil.copyfile(j(cobblestone_install_path, 'scripts', f'requirements_{db}.txt'),
                    j(project_path, 'requirements.txt'))
    # copy project Dockerfile
    shutil.copyfile(j(cobblestone_install_path, 'Dockerfile'),
                    j(project_path, 'Dockerfile'))

    # add executable permissions to scripts
    os.chmod(j(project_path, 'run-db.sh'), 0o755)
    os.chmod(j(project_path, 'run-server.sh'), 0o755)

    # write .env file
    if not config.get('quick', False):
        ref_config = CONFIGURATIONS[db]
        with open(j(project_path, '.env'), 'w') as FILE:
            FILE.write(f'export TOKEN_SECRET_KEY={token_secret}\n\n')
            FILE.write(f'export API_HOST={api_host}\n')
            FILE.write(f'export API_PORT={api_port}\n\n')
            FILE.write(f'export AUTH_METHOD={auth_method}\n\n')
            if auth_method == 'keycloak':
                FILE.write(f'export KEYCLOAK_HOST={keycloak_host}\n')
                FILE.write(f'export KEYCLOAK_REALM={keycloak_realm}\n')
                FILE.write(f'export KEYCLOAK_CLIENT_ID={keycloak_client_id}\n')
                FILE.write(
                    f'export KEYCLOAK_CLIENT_SECRET={keycloak_client_secret}\n\n')
            FILE.write(f'export DB_TYPE={db}\n')
            FILE.write(f'export DB_SUBTYPE={db_subtype}\n')
            FILE.write(f'export DB_USER={config.get("db_user", ref_config["defaults"].get("db_user", ""))}\n')
            FILE.write(
                f'export DB_PASSWORD={config.get("db_password", ref_config["defaults"].get("db_password", ""))}\n')
            FILE.write(f'export DB_HOST={config.get("db_host", "")}\n')
            FILE.write(f'export DB_PORT={config.get("db_main_port", "")}\n')
            FILE.write(f'export DB_WEB_PORT={config.get("db_web_port", "")}\n')
            if (db_name := config.get('db_name', '')):
                FILE.write(f'export DB_NAME={db_name}\n')
            has_rel_props = config.get('has_rel_props', CONFIGURATIONS.get(
                db, {'has_rel_props': False})['has_rel_props'])
            FILE.write(
                f'\nexport HAS_RELATIONSHIP_PROPERTIES={has_rel_props}\n')
            FILE.write(f'\nexport PRIMARY_KEY={config.get("ref_uid")}\n')
            FILE.write(f'\nexport REF_REL={config.get("ref_rel")}\n')


def start_project(project_path: str, debug: bool = False):
    j = os.path.join

    # check for missing .env file (if quick config)
    if not os.path.exists(j(project_path, '.env')):
        logging.error('Missing a .env file. Either run a full init (without the --quick flag) '
                      'or add a custom .env at the root of your project folder.')
        return

    client = docker.from_env()

    os.chdir(project_path)
    # load env variables
    env = load_env()
    auth_method = env.get('AUTH_METHOD')
    sleep(0.5)
    # install requirements
    logging.info('Installing requirements')
    subprocess.run(['python', '-m', 'pip', 'install',
                    '-r', 'requirements.txt'])
    sleep(0.5)
    # start database (if it is local)
    project_name = os.path.basename(project_path)
    run_database(project_name, client, env)
    # start server
    logging.info('Running server')
    if debug:
        subprocess.call(['./run-server.sh', '--debug'], env=env)
    else:
        subprocess.call(['./run-server.sh'], env=env)
    sleep(0.5)
    # if auth data is in database, init database with some starting admin user
    if auth_method == 'db':
        os.system('db_init.py')


def deploy_project(project_path: str, autorun: bool = False, port: int = None, db_port: int = None):
    # check for missing .env file (if quick config)
    if not os.path.exists(os.path.join(project_path, '.env')):
        logging.error('Missing a .env file. Either run a full init (without the --quick flag) '
                      'or add a custom .env at the root of your project folder.')
        return

    client = docker.from_env()
    api_client = docker.APIClient(base_url='unix://var/run/docker.sock')
    image_name = f'cobblestone/{os.path.basename(project_path)}'

    # load env variables
    os.chdir(project_path)
    env = load_env()
    db = env.get('DB_TYPE')

    # build docker image
    logging.info('Building Docker image')
    try:
        streamer = api_client.build(
            path=project_path,
            tag=image_name,
            rm=True,
            decode=True
        )
        for chunk in streamer:
            if 'stream' in chunk:
                for line in chunk['stream'].splitlines():
                    print(line)
    except Exception as e:
        print(e['message'])
        return

    # directly run container
    port = port if port else 8000
    if autorun:
        # run database container
        project_name = os.path.basename(project_path)
        run_database(project_name, client, env, port=db_port)
        # run API container
        run_project_container(project_name, client, env, port=port)

    # or debug run command
    else:
        project_name = os.path.basename(project_path)
        run_message = 'Image built successfully! ' + \
            f'To run it:\n\n\tcobblestone run {project_name}\n'
        logging.info(run_message)


def run_project(project_path: str, port: int, db_port: int):
    client = docker.from_env()
    # load env variables
    os.chdir(project_path)
    env = load_env()
    db = env.get('DB_TYPE')
    # run database container
    project_name = os.path.basename(project_path)
    run_database(project_name, client, env, port=db_port)
    # run API container
    # (clean currently running API container if there is one)
    try:
        c = client.containers.get(project_name)
        c.remove(force=True)
    except docker.errors.NotFound:
        pass
    run_project_container(project_name, client, env, port=port)


def stop_project(project_path: str, container: docker.models.containers.Container):
    client = docker.from_env()
    # stop database container
    project_name = os.path.basename(project_path)
    stop_database(project_name, client)
    # stop API container
    logging.info(f'Stopping API in docker')
    container.stop()


@click.group()
def main():
    pass


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.argument('project_name', type=str)
@click.option('--overwrite', help='If passed, any already existing project with the same name will be overwritten',
              type=bool, is_flag=True)
@click.option('--quick', help='If passed, asks for a quick config setup - no .env file is produced',
              type=bool, is_flag=True)
def init(project_name, overwrite, quick):
    project_path = os.path.abspath(project_name)
    # check for previous files
    if os.path.exists(project_path):
        if not overwrite:
            logging.error('A project with the same name already exists. '
                          'Either choose another path, or use a different project name.')
            return
        logging.warning(
            'A project with the same name already exists. It will be replaced.')

    config = get_configuration(quick=quick)
    if len(config):  # abort if setup cancelled by user
        if os.path.exists(project_path):
            shutil.rmtree(project_path)
        init_project(project_path, config)


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.argument('project_name', type=str)
@click.option('--debug', help='If passed, runs the server in hot-reload dev mode',
              type=bool, is_flag=True)
def start(project_name, debug):
    project_path = os.path.abspath(project_name)
    # check for non-existent project
    if not os.path.exists(project_path):
        logging.error(f'You must init the project "{project_name}" first. '
                      f'Run:\n\tcobblestone init {project_name}')
        return

    start_project(project_path, debug=debug)


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.argument('project_name', type=str)
@click.option('--port', help='Port to expose on the new container to access the '
              'deployed API', type=int, default=8000)
@click.option('--db-port', help='Port to expose on the friend container to access the '
              'database', type=int)
@click.option('--autorun', help='If passed, automatically creates a container when'
              ' the image is finished building', type=bool, is_flag=True)
def deploy(project_name, port, db_port=None, autorun=False):
    project_path = os.path.abspath(project_name)
    # check for non-existent project
    if not os.path.exists(project_path):
        logging.error(f'You must init the project "{project_name}" first. '
                      'Run:\n\tcobblestone init {project_name}')
        return

    deploy_project(project_path, autorun, port, db_port=db_port)


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.argument('project_name', type=str)
@click.option('--port', help='Port to expose on the new container to access the '
              'deployed API', type=int, default=8000)
@click.option('--db-port', help='Port to expose on the friend container to access the '
              'database', type=int)
@click.option('--image', help='Specific docker image name', type=str)
def run(project_name, port, db_port=None, image=None):
    project_path = os.path.abspath(project_name)

    if image is None:
        image = f'cobblestone/{os.path.basename(project_path)}'

    client = docker.from_env()
    # check for non-existent image
    try:
        _ = client.images.get(image)
    except docker.errors.ImageNotFound:
        logging.error(f'You must deploy the project "{project_name}" first. '
                      'Run:\n\tcobblestone deploy {project_name}')
        return

    run_project(project_path, port, db_port=db_port)


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.argument('project_name', type=str)
@click.option('--container', help='Specific docker container name', type=str)
def stop(project_name, container=None):
    project_path = os.path.abspath(project_name)

    if container is None:
        container_name = project_name
    else:
        container_name = container

    client = docker.from_env()
    # check for non-existent image
    try:
        container = client.containers.get(container_name)
    except docker.errors.NotFound:
        logging.warn(
            f'The project "{project_name}" is not currently running in Docker.')
        return

    stop_project(project_path, container)


main.add_command(init)
main.add_command(start)
main.add_command(deploy)
main.add_command(run)
main.add_command(stop)


if __name__ == '__main__':
    main()
