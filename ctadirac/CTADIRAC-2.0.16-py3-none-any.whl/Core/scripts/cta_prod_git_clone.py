#!/usr/bin/env python
"""
Clone a given branch of a git repository
branch is optional
Usage:
   cta-prod-git-clone <repo_url> <branch>
"""

__RCSID__ = "$Id$"

# generic imports
from git import Repo

# DIRAC imports
import DIRAC
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script

@Script()
def main():
  Script.parseCommandLine(ignoreErrors=True)
  args = Script.getPositionalArgs()
  branch = None
  if len(args) == 1:
    repo_url = args[0]
  elif len(args) == 2:
    repo_url = args[0]
    branch = args[1]
  else:
    Script.showHelp()

  git_clone(repo_url, branch)
  DIRAC.exit()

def git_clone(repo_url, branch=None):
  ''' Clone a given branch of a git repo '''
  if branch is None:
    Repo.clone_from(repo_url, repo_url.split("/")[-1])
  else:
    Repo.clone_from(repo_url, repo_url.split("/")[-1], branch=branch)


if __name__ == '__main__':
  main()

