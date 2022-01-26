import inspect
import pathlib
from pathlib import Path
from typing import Optional

from fexception import FFileNotFoundError
from .type_checks import type_check


def file_check(file_path: str, file_description: Optional[str] = None) -> None:
    """
    Checks if the file exists.

    Raises a cleanly formatted reason if the key validation is unsuccessful.

    No return output.

    Args:
        file_path (str):
        \t\\- The file path being checked.
        file_description (str, optional):
        \t\\- Name of the file being checked.\\
        \t\\- Defaults to None.

    Raises:
        FFileNotFoundError (fexception):
        \t\\- The file ({file_description}) does not exist in the validating file path ({file_path}).
        FFileNotFoundError (fexception):
        \t\\- The file does not exist in the validating file path ({file_path}).
    """
    type_check(
        file_path,
        str,
        # Caller override two calls before.
        caller_override={
            'module': Path(inspect.currentframe().f_back.f_back.f_code.co_filename).stem,
            'name': inspect.currentframe().f_back.f_back.f_code.co_name,
            'line': inspect.currentframe().f_back.f_back.f_lineno,
            'tb_remove': 'file_checks'}
    )

    if file_description:
        type_check(
            file_description,
            str,
            # Caller override two calls before.
            caller_override={
                'module': Path(inspect.currentframe().f_back.f_back.f_code.co_filename).stem,
                'name': inspect.currentframe().f_back.f_back.f_code.co_name,
                'line': inspect.currentframe().f_back.f_back.f_lineno,
                'tb_remove': 'file_checks'}
        )

    # Checks if the file does not exist
    file = pathlib.Path(file_path)
    if not file.exists():
        # Sets message based on description choice.
        if file_description:
            exc_args = {
                'main_message': f'The file ({file_description}) does not exist '
                                f'in the validating file path ({file_path}).',
                'suggested_resolution': 'Ensure the file path is the correct path to your file.'
            }
        else:
            exc_args = {
                'main_message': f'The file does not exist in the validating file path ({file_path}).',
                'suggested_resolution': 'Ensure the file path is the correct path to your file.'
            }
        # Caller override two calls before.
        caller_override = {
            'module': Path(inspect.currentframe().f_back.f_back.f_code.co_filename).stem,
            'name': inspect.currentframe().f_back.f_back.f_code.co_name,
            'line': inspect.currentframe().f_back.f_back.f_lineno,
            'tb_remove': 'file_checks'
        }
        raise FFileNotFoundError(exc_args, tb_limit=None, caller_override=caller_override)
