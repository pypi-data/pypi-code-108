import json
from abc import ABC
from typing import Dict, Union

from pydantic import ValidationError

from tktl.core.exceptions import NoContentsFoundException, UserRepoValidationException
from tktl.core.schemas.project import ProjectValidationOutput


class ValidationOutputBase(ABC):
    title: str
    summary: str
    text: str

    @classmethod
    def format_outputs(cls, outputs: Dict):
        if outputs:
            text = cls.text + "\n## Outputs\n"
            for k, v in outputs.items():
                text += f"- {k}: {v}\n"
            return text
        else:
            return cls.text

    @classmethod
    def get_check_created_output(cls):
        return ProjectValidationOutput(title=cls.title, summary=cls.summary, text="")

    @classmethod
    def default_output(cls, passed: bool, debug_output: str):
        return f"""
Debug Output
{debug_output}
        """


class ConfigFileValidationFailure(ValidationOutputBase):
    title: str = """Invalid Config File ❌"""
    summary: str = """We've identified erros in your configuration file (tktl.yaml). See below for details. Pushes will not succeed or result in new builds"""
    text = """"""

    @classmethod
    def format_step_results(cls, validation_errors: ValidationError):
        debug_output = ""
        for error in json.loads(validation_errors.json()):
            debug_output += f"""
- Value for: {': '.join(f'`{i}`' for i in error['loc'])} is invalid: `{error['msg']}`
"""
        default_output = cls.default_output(passed=False, debug_output=debug_output)
        return default_output


class ProjectValidationFailure(ValidationOutputBase):
    title: str = """Missing Files or Directory ❌"""
    summary: str = """We've identified invalid configuration of your repository. See below for details. Pushes will not succeed or result in new builds"""
    text = """"""

    @classmethod
    def format_step_results(
        cls,
        validation_errors: Union[UserRepoValidationException, NoContentsFoundException],
    ):
        debug_output = f"""
Missing files in repository: {' '.join(validation_errors.missing_files) if
        validation_errors.missing_files else '`NA`'}
Missing directories in repository: {' '.join(validation_errors.missing_directories) if
        validation_errors.missing_directories else '`NA`'}
tktl.yaml config file present: {'❌' if validation_errors.missing_config else '✅'}
        """
        default_output = cls.default_output(passed=False, debug_output=debug_output)

        return default_output
