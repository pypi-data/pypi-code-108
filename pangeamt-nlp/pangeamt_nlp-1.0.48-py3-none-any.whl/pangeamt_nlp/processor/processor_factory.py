import pkgutil
import inspect
import os
import importlib
from typing import Union
from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.processor.base.validator_base import ValidatorBase


class ProcessorFactory:
    PROCESSORS = {}
    INITIALIZED = False
    NAME = 'NAME'

    @staticmethod
    def _init()->None:
        if not ProcessorFactory.INITIALIZED:
            package_dir = os.path.dirname(__file__)
            for _, mod, is_package in pkgutil.walk_packages([package_dir], 'pangeamt_nlp.processor.'):
                # Import module
                mods = mod.split('.')
                module = mods[-1]
                package = '.'.join(mods[0:-1])
                imported_module = importlib.import_module('.' + module, package=package)

                # List all class in the imported module
                for _, cls in inspect.getmembers(imported_module, inspect.isclass):
                    if (issubclass(cls, NormalizerBase) and cls != NormalizerBase) or (
                            issubclass(cls, ValidatorBase) and cls != ValidatorBase):
                        if not hasattr(cls, ProcessorFactory.NAME):
                            raise ValueError(f'Processor {cls} has not attribute {ProcessorFactory.NAME}.')
                        name = getattr(cls, ProcessorFactory.NAME)
                        if name in ProcessorFactory.PROCESSORS:
                            raise ValueError(f'Processor {cls} {ProcessorFactory.NAME} attribute already exists')
                        ProcessorFactory.PROCESSORS[name] = cls
        ProcessorFactory.INITIALIZED = True

    @staticmethod
    def create(name: str, src_lang: str, tgt_lang: str, *argv, **kwargs) -> Union[NormalizerBase, ValidatorBase]:
        if not ProcessorFactory.INITIALIZED:
            ProcessorFactory._init()

        if name not in ProcessorFactory.PROCESSORS:
            raise ValueError(f'Processor {name} not found.')
        cls = ProcessorFactory.PROCESSORS[name]
        obj = cls(src_lang, tgt_lang, *argv, **kwargs)
        return obj

    @staticmethod
    def get_available():
        if not ProcessorFactory.INITIALIZED:
            ProcessorFactory._init()
        return ProcessorFactory.PROCESSORS

