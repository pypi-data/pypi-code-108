from os import environ, getcwd
import os.path
import re, io, atexit, subprocess, shlex


class PyEnv:
    def __init__(self, env_path: str = '.env', stringIO: bool = False, auto_close: bool = False, verbose: bool = False):
        self.env_path = env_path
        self.stringIO = stringIO
        self.auto_close = auto_close
        self.verbose = verbose
        self.stringIOObject = None
        self.transferDocumentFilePath = None
        if self.auto_close:
            atexit.register(self.closer)

    def closer(self):
        if self.stringIOObject:
            if self.verbose:
                print('Auto-closing StringIO Object')
            self.stringIOObject.close()

    def _read_env_file(self, explicit_file_path = None):
        env_file_path = [explicit_file_path if explicit_file_path != None else self.env_path][0]
        if not self.stringIO:
            try:
                with open(os.path.join(environ['PWD'], env_file_path), 'r', encoding='utf-8') as envfile:
                    return envfile.readlines()
            except TypeError:
                if self.verbose:
                    raise TypeError('Invalid env file type.')
            except FileNotFoundError:
                try:
                    with open(env_file_path, 'r', encoding='utf-8') as envfile:
                        return envfile.readlines()
                except FileNotFoundError:
                    if self.verbose:
                        raise FileNotFoundError('Unable to find env file.')
        else:
            self.stringIOObject = io.StringIO()
            env_file = io.open(env_file_path, mode='r', encoding='utf-8').read()
            self.stringIOObject.write(env_file)
            return self.stringIOObject

    def cli(self, command):
        env_file = self._read_env_file()
        try:
            for env in env_file:
                en_v = re.sub("['\"]", '', env.replace('\n', ''))
                idx = en_v.find('=')
                environ[str(en_v[:idx])] = str(en_v[idx+1:])
            if command or command != '':
                subprocess.run(shlex.split(command), cwd=getcwd(), env=environ.copy())
        except TypeError as error:
            if self.verbose:
                raise TypeError('Unable to load .env via client. Reason: {}'.format(error))

    def load_env(self):
        env_file = self._read_env_file()
        if self.stringIO:
            return env_file
        try:
            for env in env_file:
                en_v = re.sub("['\"]", '', env.replace('\n', ''))
                idx = en_v.find('=')
                environ[str(en_v[:idx])] = str(en_v[idx+1:])
        except TypeError as error:
            if self.verbose:
                raise TypeError('Unable to load .env via module import. Reason: {}'.format(error))

    def load_env_object(self, filepath = None):
        env_obj = {}
        env_file = self._read_env_file(filepath)
        try:
            for env in env_file:
                en_v = re.sub("['\"]", '', env.replace('\n', ''))
                idx = en_v.find('=')
                env_obj[str(en_v[:idx])] = str(en_v[idx+1:])
            return env_obj
        except TypeError as error:
            raise TypeError('Unable to load .env as object via module import: Reason: {}'.format(error))
    
    def transfer_env_variables(self, new_env, preserve):
        old_env_file = self.load_env_object()
        new_env_file = self.load_env_object(new_env)
        new_data = []
        for key, value in old_env_file.items():
            try:
                if preserve:
                    new_env_file[key]
                else:
                    new_env_file[key] = value
            except KeyError:
                new_env_file[key] = value
        for key, value in new_env_file.items():
            new_data.append('{}={}\n'.format(key, value))
        with open(new_env, 'w', encoding='utf-8') as write_new_env_file:
            write_new_env_file.writelines(new_data)
        self.transferDocumentFilePath = new_env
    
    def clear_self_initialized_variables(self):
        envs = None
        if self.transferDocumentFilePath != None:
            envs = self.load_env_object(self.transferDocumentFilePath)
        else:
            envs = self.load_env_object()
        try:
            for key in envs.keys():
                del environ[key]
        except KeyError:
            # silently ignore the error from absense of given key
            pass

def load_env(env_path: str = '.env', stringIO: bool = False, auto_close: bool = False, verbose: bool = False):
    return PyEnv(env_path, stringIO, auto_close, verbose).load_env()


def load_env_object(env_path: str = '.env', verbose: bool = False):
    return PyEnv(env_path, verbose=verbose).load_env_object()


def load_env_cli(env_path: str = '.env', command: str = '', verbose: bool = False):
    return PyEnv(env_path, verbose=verbose).cli(command)


def transfer_new_env(old_env_path: str, new_env_path: str, preserve: bool = True):
    return PyEnv(old_env_path).transfer_env_variables(new_env_path, preserve)


def clear_env(env_path: str = '.env', module_init_only: bool = True):
    if module_init_only is False:
        environ.clear()
        return
    return PyEnv(env_path).clear_self_initialized_variables()
