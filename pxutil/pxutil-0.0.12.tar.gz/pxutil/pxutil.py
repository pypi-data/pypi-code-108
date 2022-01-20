#!/usr/bin/env python3
"""
Some handy utilities from Peter Jiping Xie  
"""
# __all__ = ['bash','trim_docstring','grep']

import sys
import re
import pdb

if sys.version_info < (3, 5):
    raise Exception("Require python 3.5 or above.")

# util should not configure logging.basicConfig because it will change the logging of the python files which import this util.
# logging.basicConfig(
#     level=logging.WARNING,
#     format='%(asctime)s [%(lineno)-4d] [%(levelname)7s]: %(message)s',
#     datefmt="%Y-%m-%d %I:%M:%S",
# )
# log = logging.getLogger("pxutil")


def bash(cmd, encoding=None):
    """    
    subprocess.run with intuitive options to execute system commands just like shell bash command.
    
    Inspired by https://pypi.org/project/bash/.
    
    cmd: string 
    return: CompletedProcess object in text (decode as locale encoding), with attributes stdout, stderr and returncode.
    
    Usage example: 
    ret = bash('ls')
    print(ret.stdout, ret.stderr, ret.returncode)
    
    Warning of using shell=True: https://docs.python.org/3/library/subprocess.html#security-considerations
    """
    from subprocess import run, PIPE  # Popen, CompletedProcess
    import sys
    import locale

    if sys.version_info >= (
        3,
        7,
    ):  # version_info is actually a tuple, so compare with a tuple
        if encoding:
            return run(cmd, shell=True, capture_output=True, text=True, encoding=encoding)
        else:
            return run(cmd, shell=True, capture_output=True, text=True)

    elif sys.version_info >= (3, 5):
        if encoding is None:        
            # get system default locale encoding
            encoding=locale.getdefaultlocale()[1] 
        # print('encoding: %s' % encoding)
        r = run(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        r.stdout = r.stdout.decode(encoding)
        r.stderr = r.stderr.decode(encoding)
        return r
    else:
        raise Exception("Require python 3.5 or above.")
        # Alternately can call Popen directly, but it will return stderr, stdout as bytes and need to decode first. Don't bother, just upgrade Python version.
        """ Example
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        code = p.returncode
        """

def bashx(cmd, x=True, e=False):
    """    
    run system cmd like bash -x
    
    Print the cmd with + prefix before executing
    Don't capture the output or error 
    
    Arguments
    ---------
    cmd: string - command to run
    x:  When True, print the command with prefix + like shell 'bash -x' before running it 
    e:  When True, exit the python program when returncode is not 0, like shell 'bash -e'.
    
    return
    ------
    CompletedProcess object with only returncode.
    
    Shell environment variables
    ---------------------------
    You can set the following environment variables which have the same effect of but overwrite argument options.
    BASH_CMD_PRINT=True     same as x=True    
    BASH_EXIT_ON_ERROR=True same as e=True

    Usage example: 
    ret = shx('ls')
    print(ret.returncode)
    
    Warning of using shell=True: https://docs.python.org/3/library/subprocess.html#security-considerations
    """
    from subprocess import run # CompletedProcess
    import sys
    import os

    if sys.version_info >= (
        3,
        5,
    ):  # version_info is actually a tuple, so compare with a tuple
        x_env = os.getenv('BASH_CMD_PRINT', None)
        # BASH_CMD_PRINT overwrites x argument
        if x_env is not None:
            if x_env.lower() == 'true':
                x = True
            elif x_env.lower() == 'false':
                x = False

        e_env = os.getenv('BASH_EXIT_ON_ERROR', None)
        # BASH_EXIT_ON_ERROR overwrites x argument
        if e_env is not None:
            if e_env.lower() == 'true':
                e = True
            elif e_env.lower() == 'false':
                e = False

        if x:
            print('+ %s' % cmd)

        ret=run(cmd, shell=True)
        
        if e and ret.returncode !=0:
            print('Error: Command returns error code %s. Exiting the program...' % ret.returncode)
            sys.exit(1)
        else:
            return ret
    else:
        raise Exception("Require python 3.5 or above.")

def trim_docstring(docstring):
    """
    Trim leading indents, leading and trailing blank lines from multiple liner using triple quote like docstring.
    
    Reference: https://www.python.org/dev/peps/pep-0257/#handling-docstring-indentation
    
    Argument: multiple liner string, typically using triple quote.
    Return: trimmed multiple line string 
    
    Note: textwrap.dedent(docstring) does the same job, but not removing leading blank lines.
    """
    import sys

    if not docstring:
        return ""
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = (
        sys.maxsize
    )  # sys.maxint in Python 2 is replaced with sys.maxsize in Python 3
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxsize:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    return "\n".join(trimmed)


def grep(pattern, string=None, filename=None):
    """ simulate linux grep command
    
    return lines matching a pattern in a string or a file.
    
    Parameters:
    pattern: regular expression string
    
    Usage examples:
    result = grep('keyword', filename='a.txt' )
    for i in result:
        print(i)
        
    Notes: 
    If the matched list is too big, you can modify it to use yield generator.
    """
    if string == None and filename == None:
        print('grep: No string nor filename provided in the arguments.')
        return []
    if string != None:
        extended_pattern = ".*" + pattern + ".*"
        return re.findall(extended_pattern, string)
    if filename != None:
        result = []
        with open(filename) as f:
            extended_pattern = ".*" + pattern + ".*"
            for l in f:
                result += re.findall(extended_pattern, l)
        return result

def replace_in_file(files, old, new, backup=None):
    """
    Replace in place directly on a file.
    
    Arguments:
    files - single or list of files, e.g. 'a.txt' or ['a.txt',]
    old - old string to replace
    new - new string
    backup - backup file suffix, e.g. '.bak'. None means no backup
    """
    import fileinput

    with fileinput.FileInput(files, inplace=True, backup=backup) as file:
        for line in file:
            # yes, this print will write into the file instead to stdout.
            # end = '' so it does not print another blank new line.
            print(line.replace(old, new), end='')   

def time2seconds(time):
    """ delta time string to number of seconds

    time: e.g. '2d' for 2 days, supported units: d-day, h-hour, m-minute, s-second
    return: integer number of seconds

    Note: Month and year duration varies. Not worth doing for the sake of simplicity.
    """
    assert len(re.findall(r'^\d+[s|m|h|d]$', str(time))) == 1, 'Invalid time string format.'
    tmap = {'s':1,'m':60,'h':3600,'d':3600 * 24}
    unit = time[-1]
    value = int(time[:-1])
    return value * tmap[unit]

def purge(dir, age='0s', filename_filter='*'):
    """ Purge files and subfolders older than certain age
    
    Params
    ------
    dir:   directory to purge files and subfolders
    age:    e.g. '2h', support d-day, h-hour, m-minute, s-second
    filename_filter:  glob format, e.g. debug.log* 
    
    Usage examples:
    purge('/root/tmp/', '24h', 'debug.log*')

    Note: It retains the parent folder dir. Use shutil.rmtree if you want to remove the folder as well. 
    """
    import os
    import time
    from glob import glob
    import shutil

    if not os.path.isdir(dir):
        print("%s is not a valid directory." % dir)
        return 1

    now = time.time()
    fullpath = os.path.join(dir,filename_filter)

    for f in glob(fullpath):
        # use ctime instead of mtime. e.g. youtube-dl downloads a old video from youtube, mtime is retained, but ctime is when it is downloaded.
        if os.stat(f).st_ctime <= now - time2seconds(age):
            # os.remove(f)
            if os.path.isfile(f) or os.path.islink(f):
                try:
                    os.remove(f)
                except OSError as e:
                    print('Failed to remove %s. Reason: %s' % (f, e))
            elif os.path.isdir(f):
                shutil.rmtree(f,ignore_errors=True)        

def test_self():
    ret = time2seconds('2m')
    print(ret)
    # pdb.set_trace()
    
if __name__ == "__main__":
    print('Test self')
    test_self()
