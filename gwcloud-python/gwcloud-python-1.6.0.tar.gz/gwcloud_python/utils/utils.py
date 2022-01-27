from pathlib import Path
import re


def write_file_at_path(root_path, file_path, file_contents, preserve_directory_structure=True):
    """Write a file at the given path, with the given contents

    Parameters
    ----------
    root_path : str or pathlib.Path
        The base directory
    file_path : pathlib.Path
        The file path within the base directory, including the name of the file
    file_contents : bytes
        The contents of the file
    preserve_directory_structure : bool, optional
        Create any directories present in `file_path`, by default True
    """
    if preserve_directory_structure:
        path = root_path / file_path
    else:
        path = root_path / Path(file_path.name)

    path.parents[0].mkdir(parents=True, exist_ok=True)
    path.write_bytes(file_contents)


def remove_path_anchor(path):
    """Removes the path anchor, making it a relative path

    Parameters
    ----------
    path : pathlib.Path
        Path from which to strip anchor

    Returns
    -------
    Path
        Relative path
    """
    if path.is_absolute():
        return path.relative_to(path.anchor)
    else:
        return path


def rename_dict_keys(input_dict, key_sets):
    """Renames the keys in a dictionary

    Parameters
    ----------
    input_dict : dict
        Dictionary for which to change the keys
    key_sets : list
        list of tuples of the format `(old_key, new_key)`

    Returns
    -------
    dict
        Copy of `input_dict` with old keys subbed for new keys
    """
    output_dict = input_dict.copy()
    for old_key, new_key in key_sets:
        output_dict[new_key] = output_dict.pop(old_key, None)

    return output_dict


def convert_dict_keys(input_dict, key_sets=[]):
    """Convert the keys of a dictionary from camelCase to snake_case

    Parameters
    ----------
    input_dict : dict
        Dictionary for which to convert the keys
    key_sets : list, optional
        List of tuples of the format `(old_key, new_key)` which will also be applied to the dict, by default []

    Returns
    -------
    dict
        Copy of `input_dict` with keys converted from camelCase to snake_case, and optional other key sets exchanged
    """
    convert_key_sets = []
    for old_key in input_dict.keys():
        new_key = re.sub('([A-Z]+)', r'_\1', old_key).lower()
        if old_key != new_key:
            convert_key_sets.append((old_key, new_key))
    return rename_dict_keys(input_dict, convert_key_sets + key_sets)
