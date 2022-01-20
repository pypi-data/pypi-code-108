import os
from pprint import pprint

from burlap.common import Satchel, is_local
from burlap.constants import *
from burlap.decorators import task

EZ_SETUP = 'ez_setup'
PYTHON_PIP = 'python-pip'
GET_PIP = 'get-pip'
BOOTSTRAP_METHODS = (
    EZ_SETUP,
    PYTHON_PIP,
    GET_PIP,
)


class PIPSatchel(Satchel):

    name = 'pip'

    @property
    def packager_system_packages(self):
        return {
            UBUNTU: [
                'gcc', 'python-dev', 'build-essential', 'python3-pip',
            ],
        }

    def set_defaults(self):
        self.env.bootstrap_method = PYTHON_PIP
        self.env.user = 'www-data'
        self.env.group = 'www-data'
        self.env.perms = '775'
        self.env.virtualenv_dir = '.env'
        self.env.requirements = 'pip-requirements.txt'
        self.env.python_version = '3.7'

    @task
    def has_pip(self):
        """
        Is pip3 installed on the system?
        """
        r = self.local_renderer
        with self.settings(warn_only=True):
            ret = (r.run('which pip3') or '').strip()
            if ret:
                print(f'Pip is installed at {ret}.')
            else:
                print('Pip is not installed.')
            return bool(ret)

    @task
    def bootstrap(self, force=0):
        """
        Install all the packages necessary for managing virtual environments with pip.
        """
        force = int(force)
        if self.has_pip() and not force:
            return

        r = self.local_renderer

        if r.env.bootstrap_method == GET_PIP:
            r.sudo('curl --silent --show-error --retry 5 https://bootstrap.pypa.io/get-pip.py | python')
        elif r.env.bootstrap_method == EZ_SETUP:
            r.run('wget http://peak.telecommunity.com/dist/ez_setup.py -O /tmp/ez_setup.py')
            with self.settings(warn_only=True):
                r.sudo('python /tmp/ez_setup.py -U setuptools')
            r.sudo('easy_install -U pip')
        elif r.env.bootstrap_method == PYTHON_PIP:
            r.sudo('apt-get install -y python3-pip')
        else:
            raise NotImplementedError('Unknown pip bootstrap method: %s' % r.env.bootstrap_method)

        # Upgrade pip
        r.run_or_local(f'python{self.env.python_version} -m pip install pip')

    @task
    def clean(self, virtualenv_dir=None):
        r = self.local_renderer
        with self.settings(warn_only=True):
            print('Deleting old virtual environment...')
            r.sudo('rm -Rf {virtualenv_dir}')

    @task
    def clean_virtualenv(self, *args, **kwargs):
        self.clean(*args, **kwargs)

    @task
    def virtualenv_exists(self, virtualenv_dir=None):
        """
        Return True if the virtual environment has been created.
        """
        r = self.local_renderer
        if not virtualenv_dir:
            virtualenv_dir = self.env.virtualenv_dir
        with self.settings(warn_only=True):
            ls_output = r.run_or_local('ls {virtualenv_dir}') or ''
            ret = 'bin' in ls_output.strip()  # Virtualenv should have a 'bin' directory

        if ret:
            self.vprint(f'Virtualenv exists at {virtualenv_dir}.')
        else:
            self.vprint(f'Virtualenv does not exist at {virtualenv_dir}.')

        return ret

    @task
    def what_requires(self, name):
        """
        List the packages that require the given package.
        """
        r = self.local_renderer
        r.env.name = name
        r.local('pipdeptree -p {name} --reverse')

    @task
    def create_virtualenv(self):
        """
        Create the virtual environment if it doesn't exist already.
        """
        r = self.local_renderer
        if not self.virtualenv_exists():
            print('Creating new virtual environment...')
            print('shell_env:', self.genv.shell_env)
            if is_local():
                r.local('python{python_version} -m venv {virtualenv_dir}')
            else:
                r.sudo('python{python_version} -m venv {virtualenv_dir}', user=r.env.user)

    def get_combined_requirements(self, requirements=None):
        """
        Returns all requirements files combined into one string.
        """

        def iter_lines(fn):
            with open(fn, 'r') as fin:
                for line in fin.readlines():
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if line.startswith('-r'):
                        recursive_requirements = line[3:]
                        self.vprint('Recursively including requirements from {}.'.format(recursive_requirements))
                        recursive_requirements_path = os.path.join(
                            self.genv.ROLES_DIR, self.genv.ROLE, recursive_requirements
                        )
                        yield from iter_lines(recursive_requirements_path)
                    else:
                        yield line

        requirements = requirements or self.env.requirements
        if isinstance(requirements, str):
            requirements = [requirements]

        content = []
        for requirement in requirements:
            requirements_path = self.find_template(requirement)
            content.extend(list(iter_lines(requirements_path)))

        return '\n'.join(content)

    @task
    def update_install(self, **kwargs):
        r = self.local_renderer
        r.env.quiet_flag = '' if self.verbose else '-q'

        options = [
            'requirements',
            'virtualenv_dir',
            'user',
            'group',
            'perms',
        ]
        for option in options:
            setattr(r.env, option, kwargs.pop(option, None) or getattr(r.env, option))

        # Make sure pip is installed.
        self.bootstrap()

        # Make sure our virtualenv is installed.
        self.create_virtualenv()

        # Collect all requirements.
        tmp_fn = r.write_temp_file(self.get_combined_requirements(requirements=r.env.requirements))

        # Copy up our requirements.
        r.env.pip_remote_requirements_fn = '/tmp/pip-requirements.txt'
        r.put(local_path=tmp_fn, remote_path=r.env.pip_remote_requirements_fn)

        # Ensure we're always using the latest pip.
        if is_local():
            r.local('{virtualenv_dir}/bin/pip {quiet_flag} install -U pip')
        else:
            r.sudo('{virtualenv_dir}/bin/pip {quiet_flag} install -U pip', user=r.env.user)

        # Install requirements from file.
        if is_local():
            r.local("{virtualenv_dir}/bin/pip {quiet_flag} install --exists-action w -r {pip_remote_requirements_fn}")
        else:
            r.sudo("{virtualenv_dir}/bin/pip {quiet_flag} install --exists-action w -r {pip_remote_requirements_fn}", user=r.env.user)

    @task
    def record_manifest(self):
        """
        Called after a deployment to record any data necessary to detect changes for a future deployment.
        """
        manifest = super().record_manifest()
        manifest['all-requirements'] = self.get_combined_requirements()
        if self.verbose:
            pprint(manifest, indent=4)
        return manifest

    @task(precursors=['packager', 'user'])
    def configure(self, *args, **kwargs):
        clean = int(kwargs.pop('clean', 0))
        if clean:
            self.clean_virtualenv()

        # Necessary to make warning message go away.
        # http://stackoverflow.com/q/27870003/247542
        self.genv['sudo_prefix'] += '-H '

        self.update_install(*args, **kwargs)

pip = PIPSatchel()
