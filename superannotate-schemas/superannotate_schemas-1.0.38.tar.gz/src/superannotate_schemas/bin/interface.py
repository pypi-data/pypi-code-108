import os
from os.path import expanduser
import json
import errno
from pathlib import Path

from superannotate_schemas.schemas.external import PixelAnnotation as ExternalPixelAnnotation
from superannotate_schemas.schemas.external import VectorAnnotation as ExternalVectorAnnotation
from superannotate_schemas.schemas.external import VideoAnnotation as ExternalVideoAnnotation
from superannotate_schemas.schemas.external import DocumentAnnotation as ExternalDocumentAnnotation

from superannotate_schemas.schemas.internal import PixelAnnotation as InternalPixelAnnotation
from superannotate_schemas.schemas.internal import VectorAnnotation as InternalVectorAnnotation
from superannotate_schemas.schemas.internal import VideoAnnotation as InternalVideoAnnotation
from superannotate_schemas.schemas.internal import DocumentAnnotation as InternalDocumentAnnotation
from superannotate_schemas.exceptions import InvalidInput

from superannotate_schemas import __version__
from superannotate_schemas.utils import uniquify
from superannotate_schemas.validators import AnnotationValidators


class CLIInterface:
    """
    This is to validate Pixel, Vector, Image and Document annotations.
    """
    DEFAULT_PATH = "schemas/"
    EXTERNAL_SCHEMAS = (
        ExternalPixelAnnotation, ExternalVectorAnnotation, ExternalDocumentAnnotation, ExternalVideoAnnotation
    )
    INTERNAL_SCHEMAS = (
        InternalPixelAnnotation, InternalVectorAnnotation, InternalDocumentAnnotation, InternalVideoAnnotation
    )

    @staticmethod
    def _create_folder(path: str):
        if not os.path.exists(os.path.dirname(path)):
            try:
                os.makedirs(os.path.dirname(path))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise

    @staticmethod
    def validate(*paths, project_type, internal=False, verbose=False, report_path=None):
        if not paths:
            raise InvalidInput("Please provide paths.")
        if project_type not in AnnotationValidators.VALIDATORS.keys():
            raise InvalidInput(
                f"Invalid project type, valid types are: {', '.join(AnnotationValidators.VALIDATORS.keys())}"
            )

        validator_class = AnnotationValidators.get_validator(project_type, internal)
        validation_result = []
        for path in paths:
            if Path(path).is_file():
                with open(path, "r") as file:
                    data = json.load(file)
                    validator = validator_class(data)
                    if not validator.is_valid():
                        report = validator.generate_report()
                        if verbose:
                            print(f"{'-'* 4}{path}\n{report}")
                        if report_path:
                            with open(uniquify(f"{report_path}/{(Path(path).name)}"), "w") as validation_report:
                                validation_report.write(report)
                        else:
                            validation_result.append({path: False})
            else:
                print(f"Skip {path}")
        if not verbose:
            print(validation_result)

    @staticmethod
    def version():
        return f"Version : {__version__}"
