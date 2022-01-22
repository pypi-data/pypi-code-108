from cloudmesh.common.console import Console

attribute_indent = 4


def check_file_for_tabs(filename, verbose=True):
    """identifies if the file contains tabs and returns True if it
    does. It also prints the location of the lines and columns. If
    verbose is set to False, the location is not printed.

    :param verbose: if true prints information about issues
    :param filename: the filename
    :rtype: True if there are tabs in the file
    """
    file_contains_tabs = False
    with open(filename) as f:
        lines = f.read().splitlines()

    line_no = 1
    for line in lines:
        if "\t" in line:
            file_contains_tabs = True
            location = [
                i for i in range(len(line)) if line.startswith('\t', i)]
            if verbose:
                Console.error("Tab found in line {} and column(s) {}"
                              .format(line_no,
                                      str(location).replace("[", "").replace(
                                          "]", "")),
                              traceflag=False)
        line_no += 1
    return file_contains_tabs
