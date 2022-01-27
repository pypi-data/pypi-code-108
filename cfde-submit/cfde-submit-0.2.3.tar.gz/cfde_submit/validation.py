import os
import logging

from bdbag import bdbag_api
from frictionless import FrictionlessException, Package, validate
from cfde_submit.exc import ValidationException, InvalidInput

logger = logging.getLogger(__name__)


def ts_validate(data_path, schema=None):
    """Validate a given TableSchema using frictionless.

    Arguments:
        data_path (str): Path to the TableSchema JSON or BDBag directory
                or BDBag archive to validate.
        schema (str): The schema to validate against. If not provided,
                the data is only validated against the defined TableSchema.
                Default None.

    Returns:
        dict: The validation results.
            is_valid (bool): Is the TableSchema valid?
            raw_errors (list): The raw Exceptions generated from any validation errors.
            error (str): A formatted error message about any validation errors.
    """
    if os.path.isfile(data_path):
        archive_file = data_path
        try:
            data_path = bdbag_api.extract_bag(data_path, temp=True)
        except Exception as e:
            raise InvalidInput("Error extracting %s: %s" % (archive_file, e))
        if not bdbag_api.is_bag(data_path):
            raise InvalidInput("Input %s does not appear to be a valid BDBag. This tool requires a"
                               " prepared BDBag archive when invoked on an existing archive file."
                               % archive_file)

    # If data_path is a directory, find JSON
    if os.path.isdir(data_path):
        if "data" in os.listdir(data_path):
            data_path = os.path.join(data_path, "data")
        desc_file_list = [filename for filename in os.listdir(data_path)
                          if filename.endswith(".json") and not filename.startswith(".")]
        if len(desc_file_list) < 1:
            raise ValidationException("No TableSchema JSON file found")
        elif len(desc_file_list) > 1:
            raise ValidationException("Mutiple JSON files found in directory")
        else:
            data_path = os.path.join(data_path, desc_file_list[0])

    # Read into Package
    try:
        pkg = Package(data_path)
        report = validate(pkg, schema=schema)
    except FrictionlessException as e:
        raise ValidationException("Validation error\n%s" % e.error.message)

    if not report.valid:
        if report.errors:
            msg = report.errors[0]['message']
        else:
            for task in report['tasks']:
                if not task.valid:
                    msg = task['resource']['path'] + "\n"
                    msg += task['errors'][0]['message']
        raise ValidationException("Validation error in %s" % msg)


def validate_user_submission(data_path, schema, output_dir=None, delete_dir=False,
                             handle_git_repos=True, bdbag_kwargs=None):
    """
    Arguments:
        data_path (str): The path to the data to ingest into DERIVA. The path can be:
                1) A directory to be formatted into a BDBag
                2) A Git repository to be copied into a BDBag
                3) A premade BDBag directory
                4) A premade BDBag in an archive file
        schema (str): The named schema or schema file link to validate data against.
                Default None, to only validate against the declared TableSchema.
        output_dir (str): The path to create an output directory in. The resulting
                BDBag archive will be named after this directory.
                If not set, the directory will be turned into a BDBag in-place.
                For Git repositories, this is automatically set, but can be overridden.
                If data_path is a file, this has no effect.
                This dir MUST NOT be in the `data_path` directory or any subdirectories.
                Default None.
        delete_dir (bool): Should the output_dir be deleted after submission?
                Has no effect if output_dir is not specified.
                For Git repositories, this is always True.
                Default False.
        handle_git_repos (bool): Should Git repositories be detected and handled?
                When this is False, Git repositories are handled as simple directories
                instead of Git repositories.
                Default True.
        bdbag_kwargs (dict): Extra args to pass to bdbag
    """

    # Validate TableSchema in BDBag
    logger.debug("Validating TableSchema in BDBag '{}'".format(data_path))
    ts_validate(data_path, schema=schema)
    logger.debug("Validation successful")
    return data_path
