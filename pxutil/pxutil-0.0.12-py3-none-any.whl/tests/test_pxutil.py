"""
Note: 
For pytest to support importing local modules, must create a __init__.py file to indicate it is a package.
"""
# Note: relative imports must use this syntax: from <> import <>
# from ..pxutil import bash, grep, trim_docstring
# Somehow direct import works with magic with pytest, even without tox or install pxutil as a system package.
# Not sure how it works exactly, rename __init__.py and setup.py from parent folder but it still works.
import pxutil as px
import pytest

def test_bash():
    ret = px.bash("pwd")
    assert ret.returncode == 0

def test_bashx():
    import os
    import io
    import sys    
    
    ## test default
    cmd = 'pwd'
    ret = px.bashx(cmd)
    assert ret.returncode == 0
    
    ## test x=False
    capturedOutput = io.StringIO()   # Create StringIO object
    sys.stdout = capturedOutput      # and redirect stdout.

    ret = px.bashx(cmd, x=False)   # capture stdout of print
    standard_output = capturedOutput.getvalue()
    
    sys.stdout = sys.__stdout__      # Reset redirect.
    assert ('+ %s' % cmd) not in standard_output
    assert ret.returncode == 0

    ## test x=False by environment variable BASH_CMD_PRINT
    os.environ['BASH_CMD_PRINT'] = 'False'
    capturedOutput = io.StringIO()   # Create StringIO object
    sys.stdout = capturedOutput      # and redirect stdout.

    ret = px.bashx(cmd, x=True)   # capture stdout of print
    standard_output = capturedOutput.getvalue()
    
    sys.stdout = sys.__stdout__      # Reset redirect.
    assert ('+ %s' % cmd) not in standard_output
    assert ret.returncode == 0    

    ## test e=True
    # Ref: https://docs.pytest.org/en/6.2.x/assert.html#assertions-about-expected-exceptions
    cmd = 'ls not_exit'
    # Capture SystemExit exception raised by sys.exit
    with pytest.raises(SystemExit) as excinfo:
        px.bashx(cmd, e=True)
    assert excinfo.type == SystemExit

    ## test e=True by environment variable BASH_EXIT_ON_ERROR
    os.environ['BASH_EXIT_ON_ERROR'] = 'true'
    cmd = 'ls not_exit'
    # Capture SystemExit exception raised by sys.exit
    with pytest.raises(SystemExit) as excinfo:
        px.bashx(cmd, e=False)
    assert excinfo.type == SystemExit    

def test_grep():
    ret = px.grep("de", "abc\ndef")
    assert ret == ["def"]

def test_trim_docstring():
    ret = px.trim_docstring(
        """
    ab
        cd
    """
    )
    # print(ret)
    assert ret == "ab\n    cd"

def test_replace_in_file():
    import os

    tempfile = 'test_replace_in_file.tmp'
    with open(tempfile,mode='w+') as f:
        f.write('Hello world\nHello you.')

    px.replace_in_file(tempfile,'Hello','Hi',backup=None)
    with open(tempfile,mode='r') as f:
        assert f.read() == 'Hi world\nHi you.'

    os.remove(tempfile)

    # import tempfile   
    # # tempfile is removed on close. Need a persistent temp file for this test
    # with tempfile.TemporaryFile(mode='w+') as f:
    #     f.write('Hello world!\nHello you.')
    #     f.seek(0)
    #     print(f.read())
    
    