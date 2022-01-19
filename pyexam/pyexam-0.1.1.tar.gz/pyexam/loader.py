import yaml
from pydantic import ValidationError

from . import Exam
from .exceptions import LoadError


def load(file: str) -> Exam:
    try:
        with open(file, 'r') as stream:
            data = yaml.safe_load(stream)
            exam = Exam(**data)
            return exam
    except OSError as e:
        raise LoadError('Unable to load exam file') from e
    except yaml.YAMLError as e:
        raise LoadError('Invalid exam yaml format') from e
    except ValidationError as e:
        raise LoadError('Invalid exam yaml contents') from e
    except Exception as e:
        raise LoadError('Unknown exception') from e
