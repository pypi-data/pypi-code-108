from captur_ml_sdk.dtypes.exceptions import InvalidFilePathError

import re


def get_image_components(imagefile, file_extension=""):
    """
    Get a dictionary of the input imagefile string.
    For example, gs://captur-ml/scooter-parking/batch-files/bay-no-bay.jsonl
    would return:
    {
        "bucket": "captur-ml",
        "problem-type": "scooter-parking",
        "batch-files-folder": "batch-files",
        "batch-file-name": "bay-no-bay.jsonl",
    }

    args:
        imagefile: the full string path for the file
        file_extension: the required file extension (WITH preceding '.')

    raises:
        InvalidFilePathError if the filename string is badly formatted
    """
    match_regular_word = '[\w][\w\d\-\_]*'
    match_image_components_path = f'^(?:gs\:\/\/)(?P<bucket>{match_regular_word})/(?P<problem>{match_regular_word})/(?P<folder>{match_regular_word})/(?P<name>{match_regular_word}{file_extension})$'
    rgx = re.search(match_image_components_path, imagefile)

    if rgx is None:
        raise InvalidFilePathError(
            f'Image file {imagefile} is formatted incorrectly. Image file must be in format: '
            f'gs://<BUCKET_NAME>/<PROBLEM_TYPE>/<BATCH_FILES_FOLDER>/<BATCH_FILE_NAME>{file_extension}'
        )

    return {
        "bucket": rgx.group("bucket"),
        "problem-type": rgx.group("problem"),
        "batch-files-folder": rgx.group("folder"),
        "batch-file-name": rgx.group("name"),
    }
