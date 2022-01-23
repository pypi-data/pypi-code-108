"""
An alternate solution file for the files example task.
"""


def listFile(filename):
    """
    Prints out the contents of a file, with line numbers at the start of
    each line.
    """
    fin = open(filename, 'r')
    lines = fin.readlines()
    fin.close()

    for ln in range(len(lines)):
        print(ln + 1, lines[ln], end='')


def grep(filename, fragment, writeTo):
    """
    Finds just lines of the file which contain the given fragment, and
    writes them into the writeTo file.
    """
    matching = []
    with open(filename, 'r') as fin:
        for line in fin:
            if fragment in line:
                matching.append(line)

    with open(writeTo, 'w') as fout:
        for line in matching:
            fout.write(line)


def addRecords(filename, records):
    """
    Given a filename and a list of strings, adds one line to the file
    for each string, consisting of just that string plus a newline. If
    called multiple times, the file will grow longer each time.
    """
    with open(filename, 'a') as fout:
        fout.write('\n'.join(records) + '\n')
