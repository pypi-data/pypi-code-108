"""
This is the "remotes" module implementing solutions to work with remote data / resource files.

>>> git_clone()
True

"""

import os
import git
import logging


def git_clone(repolist=None, git_dir=None):
    """ clones a git repo and recursively updates its submodules"""
    # git_dir='C:/Users/steve/AppData/Local/Temp/wowgen_extra'
    chk = True

    if not git_dir:
        if os.environ.get('WOWGEN_EXTRA'):
            git_dir = os.environ.get('WOWGEN_EXTRA')
        else:
            chk = False
    # repo url, target folder, branch
    if not repolist:
        repolist = [("https://git.cccwi.de/2dwt/wowgen.git", "wowgen.git", "main")]

    if chk:
        for repotupel in repolist:
            logging.info(f'working at git repo {repotupel}')
            # git clone to path
            git_dir_repo = str(os.path.join(git_dir, repotupel[1]))
            os.makedirs(os.path.split(git_dir_repo)[0], exist_ok=True)

            # clone, or remove and clone
            try:
                if repotupel[2]:
                    repo = git.Repo.clone_from(repotupel[0], git_dir_repo, branch=repotupel[2], depth=1,
                                               env={"GIT_SSL_NO_VERIFY": "1"})
                else:
                    repo = git.Repo.clone_from(repotupel[0], git_dir_repo, depth=1,
                                               env={"GIT_SSL_NO_VERIFY": "1"})
            except git.exc.GitCommandError as err:
                repo = git.Repo(git_dir_repo)

            with repo.git.custom_environment(GIT_SSL_NO_VERIFY='1'):
                os.environ['GIT_SSL_NO_VERIFY'] = "1"
                repo.remotes.origin.fetch()
                repo.submodule_update(recursive=True, init=True)

            # check that the repository loaded correctly
            if repo.bare:
                chk = False
                logging.error('Could not load repository at {} :'.format(git_dir_repo))

    if not chk:
        logging.error('failure in {repolist}. git target dir set to {git_dir}')
        return False
    else:
        return True


if __name__ == "__main__":
    import doctest

    doctest.testmod(verbose=True)
