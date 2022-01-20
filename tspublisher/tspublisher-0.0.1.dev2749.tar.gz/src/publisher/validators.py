from __future__ import absolute_import, division, print_function, unicode_literals

from abc import abstractmethod

import os

from ruamel.yaml import YAMLError, safe_load

import publisher.settings as settings
from publisher.exceptions import SingleProceduresNotFoundError, MissingYamlFileError, ValidationError, \
    CombinedValidationError, InvalidYamlFileError
from publisher.utils import get_content_directories


class Validator(object):

    def __init__(self, working_directory):
        self.working_directory = working_directory

    @abstractmethod
    def validate(self):
        pass


class SingleProcedureValidator(Validator):

    def validate(self):
        procedure_directories = get_content_directories(self.working_directory)

        if len(procedure_directories) != 1:
            print(procedure_directories)
            raise SingleProceduresNotFoundError()


class YamlFileValidator(Validator):

    def __init__(self, yaml_file):
        self.yaml_file = yaml_file

    def validate(self):
        if not os.path.exists(self.yaml_file):
            raise MissingYamlFileError(self.yaml_file)

        try:
            with open(self.yaml_file, 'rb') as y:
                safe_load(y)
        except YAMLError:
            raise InvalidYamlFileError(self.yaml_file)


class ProcedureYamlFileValidator(YamlFileValidator):

    def __init__(self, procedure_directory):
        self.yaml_file = os.path.join(procedure_directory, 'procedure.yml')


class PhaseYamlFileValidator(YamlFileValidator):

    def __init__(self, phase_directory):
        self.yaml_file = os.path.join(phase_directory, 'phase.yml')


class AssetDirectoryValidator(Validator):

    def __init__(self, base_directory):
        self.asset_directory = os.path.join(base_directory, 'assets')

    def validate(self):
        if not os.path.exists(self.asset_directory):
            os.mkdir(self.asset_directory)


def validate_procedure_directory():
    SingleProcedureValidator(settings.PROCEDURE_CHECKOUT_DIRECTORY).validate()


def validate_save():

    validate_procedure_directory()

    procedure_directory = os.path.join(settings.PROCEDURE_CHECKOUT_DIRECTORY,
                                       get_content_directories(settings.PROCEDURE_CHECKOUT_DIRECTORY)[0])

    validators = [ProcedureYamlFileValidator(procedure_directory), AssetDirectoryValidator(procedure_directory)]

    phase_directories = [os.path.join(procedure_directory, d) for d in get_content_directories(procedure_directory)]

    validators += [PhaseYamlFileValidator(d) for d in phase_directories]
    validators += [AssetDirectoryValidator(d) for d in phase_directories]

    errors = []

    for v in validators:
        try:
            v.validate()
        except ValidationError as e:
            errors.append(e)

    if len(errors) > 0:
        raise CombinedValidationError(errors)
