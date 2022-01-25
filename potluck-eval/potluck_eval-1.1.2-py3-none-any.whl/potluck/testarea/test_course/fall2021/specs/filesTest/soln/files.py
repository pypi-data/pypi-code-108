"""
This solution file includes functions for reading from supplied starter
files, writing to new files, and even appending to provided starter files
(and we need those to have their side effects cleaned up properly in the
end!).
"""


def listFile(filename):
    """
    Prints out the contents of a file, with line numbers at the start of
    each line.
    """
    with open(filename, 'r') as fin:
        ln = 1
        for line in fin:
            print(ln, line, end='') # line has a newline at the end
            ln += 1


def grep(filename, fragment, writeTo):
    """
    Finds just lines of the file which contain the given fragment, and
    writes them into the writeTo file.
    """
    with open(filename, 'r') as fin:
        with open(writeTo, 'w') as fout:
            for line in fin:
                if fragment in line:
                    fout.write(line)


def addRecords(filename, records):
    """
    Given a filename and a list of strings, adds one line to the file
    for each string, consisting of just that string plus a newline. If
    called multiple times, the file will grow longer each time.
    """
    with open(filename, 'a') as fout:
        for record in records:
            fout.write(record + '\n')
