'''
Get the current branch version info from Git.
Based on https://stackoverflow.com/questions/14989858/get-the-current-git-hash-in-a-python-script
'''
import subprocess

def gitVersion():
    '''
    Return the current Git tag (if any) and revision as a string
    '''
    try:
        # this command returns the tag if there is one, otherwise just the short hash:
        out = subprocess.check_output(['git', 'describe', '--always'])
        version = out.strip().decode('ascii')
    except OSError:
        version = "unknown"

    return version

def gitBranch():
    '''
    Return the current Git branch name as a string
    '''
    try:
        # this command returns the current branch name:
        out = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
        branch = out.strip().decode('ascii')
    except OSError:
        branch = "unknown"

    return branch
