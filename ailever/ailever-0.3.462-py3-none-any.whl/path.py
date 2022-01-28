import os

def refine(path):
    r"""
    path = refine(path)
    """

    pathname_components = []
    while True:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            pathname_components.insert(0, parts[0])
            break
        elif parts[1] == path: # sentinel for relative paths
            pathname_components.insert(0, parts[1])
            break
        else:
            path = parts[0]
            pathname_components.insert(0, parts[1])
    return os.path.join(*pathname_components)

