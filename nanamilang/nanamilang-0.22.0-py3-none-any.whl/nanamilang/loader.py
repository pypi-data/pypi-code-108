"""NanamiLang (Module) Loader API"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

import os

from nanamilang.shortcuts import truncated


class Loader:
    """NanamiLang Loader class"""

    base: str = ''
    loader_cls = None
    truncated__n: int = 67
    nanamilang_module_class = None
    include_traceback: bool = False

    @classmethod
    def initialize(cls,
                   nanamilang_module_class,
                   chosen_loader_class,
                   base=None,
                   includetb=None,
                   truncated__n: int = 67) -> None:
        """NanamiLang Loader, should be called on startup"""

        cls.base = base or cls.base
        cls.truncated__n = truncated__n
        cls.include_traceback = includetb
        cls.loader_cls = chosen_loader_class
        cls.nanamilang_module_class = nanamilang_module_class

    @classmethod
    def slurp(cls, module_name: str) -> (None or str):
        """
        NanamiLang Loader, virtual Loader.slurp() class method

        It takes module_name as a parameter, and supposed to:
        1. Somehow resolve module file path on disk or somewhere else
        2. Somehow load it from file path on disk or from somewhere else
        3. Read a content from that file object, and return that content
        """

        raise NotImplementedError

    @classmethod
    def load(cls, module_name: str, module_env_inst) -> None:
        """NanamiLang Loader, use Loader.slurp() to load *.nml module"""

        if not callable(cls.nanamilang_module_class):
            print('Loader: can not work with specified nanamilang_module_class')
            return None

        try:
            source = cls.loader_cls.slurp(module_name)
        except NotImplementedError:
            print('Loader: Unable to load cause of Loader has no slurp() method implemented')
            return None

        if not source:
            print('Loader: Unable to load because of no source found for module', module_name)
            return None

        # Code above is responsible to check whether slurp() implemented or not; source available or not

        evaluated_module_instance = cls.nanamilang_module_class(name=module_name, source=source).evaluate()

        # We also do not use isinstance(dt, NException) assertion because I want to keep this module atomic

        error_list = [dat_type.format(include_traceback=cls.include_traceback)
                      for dat_type in evaluated_module_instance.results() if dat_type.name == 'NException']

        if error_list:
            for error in error_list:
                print(truncated(error, cls.truncated__n))  # print each error from collected errors listing
            return None

        # Code above is responsible to check whether module has errors, so we can not continue with loading

        module_env_inst.grab(evaluated_module_instance)  # <- Module.Environ should take care of populating

        return None  # <- we should return NoneType in explicit way because we need to keep the consistency


class LocalIOLoader(Loader):
    """Use this loader to be able to load from disk"""

    @classmethod
    def slurp(cls, module_name: str) -> (None or str):
        """
        NanamiLang Loader - Local IO Loader

        :param module_name: module name as a string
        :return: if available - *.nml module source code
        """

        maybe_located_somewhere = None

        maybe_located_here = os.path.join(cls.base,
                                          f'{module_name}.nml')
        if os.path.exists(maybe_located_here):
            maybe_located_somewhere = maybe_located_here
        nanamilang_path = os.environ.get('NANAMILANG_PATH')
        if nanamilang_path:
            # UNIX-like behavior: NANAMILANG_PATH should be present
            # like any other PATH-like environment variable in UNIX,
            # that is - directories separated by semi-colon ':' char.
            # For each directory in NANAMILANG_PATH we're looking for a
            # {module_name}.nml file. And load first occurrence we found
            for each_directory in nanamilang_path.split(':'):
                maybe_located_there = os.path.join(each_directory,
                                                   f'{module_name}.nml')
                if os.path.exists(maybe_located_there):
                    maybe_located_somewhere = maybe_located_there
                    break
        if not maybe_located_somewhere:
            return None
        with open(maybe_located_somewhere, 'r', encoding='utf-8') as reader:
            return reader.read()

        # this implementation will try to load *.nml module from current directory, otherwise - from NANAMILANG_PATH
