import os 

def nest_paths(paths: list):
    """
    Given a list of paths, convert them into a nested structure.
    """
    nested = []

    for path in paths:

        if os.path.sep not in path:
            nested.append(path)
            continue

        directory, _ = os.path.split(path)
        parts = directory.split(os.path.sep)

        branch = nested
        for part in parts:
            part = dirname_to_title(part)
            branch = find_or_create_node(branch, part)

        branch.append(path)

    return nested
