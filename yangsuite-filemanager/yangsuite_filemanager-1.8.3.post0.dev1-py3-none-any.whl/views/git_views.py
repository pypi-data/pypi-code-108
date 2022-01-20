"""Views for copying YANG files from Git."""

import os
import sys
import shutil
import tempfile
import traceback

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from yangsuite import get_logger, get_path

from .utility import post_existing_repository_required

log = get_logger(__name__)

try:
    import git
except ImportError as e:
    log.error('Git not installed.  See https://git-scm.com/ for instructions')


git_status = {}


@login_required
@post_existing_repository_required
def git_files_to_repo(request, targetrepo):
    """Clone the given git repository and import YANG modules to a YANG repo.

    Returns:
      JsonResponse: {reply: result message}
    """
    if 'git' not in sys.modules:
        msg = 'Git not installed.  See https://git-scm.com/ for instructions'
        log.error(msg)
        return JsonResponse({}, status=500, reason=msg)

    user = request.user.username
    if request.method == 'GET':
        if user in git_status:
            return JsonResponse(git_status[user])
        return JsonResponse({}, status=404,
                            reason="No git operation in progress")

    url = request.POST.get('url')
    if not url:
        return JsonResponse({}, status=400,
                            reason="No Git repository specified")
    subdir = request.POST.get('subdirectory', '')
    while subdir.startswith('/'):
        subdir = subdir[1:]
    branch = request.POST.get('branch')
    if not branch:
        branch = "master"

    include_subdirs = request.POST.get('include_subdirs', 'false')
    include_subdirs = (include_subdirs == 'true')

    scratchdir = tempfile.mkdtemp(dir=get_path('scratch', user=user))
    srcdir = os.path.abspath(os.path.join(scratchdir, subdir))
    if not srcdir.startswith(scratchdir):
        # Illegal subdir path
        shutil.rmtree(scratchdir)
        return JsonResponse({}, status=400, reason="Invalid subdirectory")

    git_status[user] = {
        'value': 0,
        'max': 2,
        'info': 'Preparing...'
    }

    try:
        git_status[user]['value'] += 1
        git_status[user]['info'] = "Cloning Git repository..."
        git.Repo.clone_from(url=url, to_path=scratchdir, branch=branch)

        if not os.path.isdir(srcdir):
            return JsonResponse({}, status=404, reason="No such subdirectory")

        git_status[user]['value'] += 1
        git_status[user]['info'] = "Adding files to YANG repository..."

        result = targetrepo.add_yang_files(srcdir,
                                           include_subdirs=include_subdirs)
        return JsonResponse({'reply': result})
    except git.exc.GitCommandError as exc:
        msg = str(exc)
        if "Repository not found" in msg:
            return JsonResponse({}, status=404,
                                reason="No such Git repository")
        elif "Remote branch" in msg and "not found in upstream" in msg:
            return JsonResponse({}, status=404, reason="No such Git branch")
        else:
            log.error("Git exception: %s", exc)
            log.debug(traceback.format_exc())
            return JsonResponse({}, status=500,
                                reason='Error in executing "{0}"'
                                .format(exc._cmdline))
    finally:
        if os.path.exists(scratchdir):
            shutil.rmtree(scratchdir, ignore_errors=True)
        del git_status[user]
