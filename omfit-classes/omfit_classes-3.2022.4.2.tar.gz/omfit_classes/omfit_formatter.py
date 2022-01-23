import os
import sys
import re

# perform checks and raise good redeable errors for users
python_version = sys.version_info.major + sys.version_info.minor * 0.1
if python_version < 3.6:
    print('OMFIT FATAL ERROR: You are running Python version %s. OMFIT requires Python 3.6+' % python_version)
    sys.exit(1)
try:
    import black
except ImportError:
    print('OMFIT FATAL ERROR: Your Python installation `%s` does not have the `black` package installed' % sys.executable)
    sys.exit(1)

__all__ = ['omfit_formatter', 'omfit_file_formatter']


# this is to disable black's magic-trailing-comma feature
def maybe_should_explode(self, closing):
    return False


black.Line.maybe_should_explode = maybe_should_explode


def omfit_formatter(content):
    """
    Format Python string according to OMFIT style
    Based on BLACK: https://github.com/psf/black with 140 chars
    Equivalent to running: `black -S -l 140 -t py36 filename`

    NOTE: some versions of black has issues when a comma trails a parenthesis
    Version 19.3b0 is ok

    :param content: string with Python code to format

    :return: formatted Python code
             None if nothing changed
             False if formatting was skipped due to an InvalidInput
    """
    mode = black.FileMode(target_versions=[black.TargetVersion.PY36], line_length=140, is_pyi=False, string_normalization=False)
    try:
        return black.format_file_contents(content, fast=True, mode=mode)
    except black.NothingChanged:
        return None
    except black.InvalidInput:
        return False


def omfit_file_formatter(filename, overwrite=True):
    """
    Format Python file according to OMFIT style
    Based on BLACK: https://github.com/psf/black with 140 chars
    Equivalent to running: `black -S -l 140 -t py36 filename`

    :param filename: filename of the Python file to format
        If a directory is passed, then all files ending with .py will be processed

    :param overwrite: overwrite original file or simply return if the file has changed

    :return: formatted Python code
        None if nothing changed
        False if style enforcement is skipped or the input was invalid
        If a directory, then a dictionary with each processed file as key is returned
    """

    def tqdm(passthrough):
        return passthrough

    import json

    try:
        from tqdm import tqdm
    except ImportError:
        pass

    # loop over list of files
    if isinstance(filename, list):
        out = {}
        for filename in tqdm(filename):
            out[filename] = omfit_file_formatter(filename, overwrite=overwrite)
        return out

    # make sure the file exists
    filename = os.path.abspath(filename)
    if not os.path.exists(filename):
        print(f'omfit_formatter: file {filename} does not exists')
        return False

    # recursively go in sub-directories
    if os.path.isdir(filename):
        out = {}
        for root, dirs, files in tqdm(list(os.walk(filename))):
            for filename in files:
                if filename.endswith(".py"):
                    out[filename] = omfit_file_formatter(root + os.sep + filename, overwrite=overwrite)
        return out

    # apply format
    with open(filename, "rb") as buf:
        content, encoding, newline = black.decode_bytes(buf.read())
    try:
        fmt_content = omfit_formatter(content)
    except Exception as _excp:
        raise _excp.__class__(f'omfit_formatter failed on `{filename}` with exception: ' + str(_excp))

    # overwrite original file if there was a change
    if fmt_content and overwrite:
        with open(filename, "w", encoding=encoding) as buf:
            buf.write(fmt_content)
    elif fmt_content is False:
        print(f'omfit_formatter: syntax error {filename}')

    # return diff, None if nothing changed, False if invalid input
    return fmt_content


if '__main__' == __name__:
    if len(sys.argv) == 1:
        sys.exit(0)
    elif len(sys.argv[1:]) == 1:
        out = omfit_file_formatter(sys.argv[1])
    else:
        out = omfit_file_formatter(sys.argv[1:])
    if out is None or (isinstance(out, dict) and all([o is None for o in out.values()])):
        sys.exit(0)
    sys.exit(1)
