"""Views for uploading YANG files."""
import errno
import os
import shutil
import tempfile
import traceback

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from yangsuite import get_logger, get_path
from .. import atomic_create
from .utility import post_existing_repository_required

log = get_logger(__name__)


@login_required
@post_existing_repository_required
def upload_files_to_repo(request, targetrepo):
    """Upload specified YANG files and add them to a repository.

    Args:
      request (django.http.HTTPRequest): HTTP POST request.
    Returns:
      JsonResponse: {reply: result of YSYangRepository.add_yang_files()}
    """
    user = request.user.username

    scratchdir = tempfile.mkdtemp(dir=get_path('scratch', user=user))
    try:
        upload_errors = upload_files_to_directory(
            request.FILES.getlist('files'), scratchdir)

        result = targetrepo.add_yang_files(scratchdir)
        result['errors'] = upload_errors + result['errors']

        return JsonResponse({'reply': result})
    except Exception as e:
        log.debug(traceback.format_exc())
        return JsonResponse({}, status=500, reason=str(e))
    finally:
        if os.path.exists(scratchdir):
            shutil.rmtree(scratchdir)


def upload_files_to_directory(files, destdir):
    """Write the provided files to the target directory.

    Helper method for upload_files_to_repo; may be used for additional purposes
    in the future.

    See also ysdevices.views.download_yang_files().

    Args:
      files (io.StringIO): In-memory file content.
      destdir (str): Directory path to write files to

    Returns:
      list: of (filename, message) that could not be uploaded successfully.
    """
    if not os.path.isdir(destdir):
        raise OSError(errno.ENOENT, os.strerror(errno.ENOENT), destdir)

    try:
        import resource
        # On some systems (MacOS X, etc.) the default "open files" limit
        # is as low as 256, which can easily be hit when uploading a full
        # set of files from a single router. Give us room to grow:
        current, hardlimit = resource.getrlimit(resource.RLIMIT_NOFILE)
        target = min(2048, hardlimit)
        if current < target:
            resource.setrlimit(resource.RLIMIT_NOFILE,
                               (target, hardlimit))
            log.debug("Temporarily increased RLIMIT_NOFILE from %d to %d",
                      current, target)

    except ImportError:
        # Assume we are on Windows - 'resource' is only for Mac/Linux
        current = 0
        target = 0

    errors = []

    try:
        for fileitem in files:
            if not fileitem.name.endswith('.yang'):
                errors.append((fileitem.name,
                               'Does not appear to be a .yang file'))
                continue
            destfile = os.path.join(destdir, fileitem.name)
            try:
                with atomic_create(destfile, reraise=True,
                                   encoding='utf-8') as fd:
                    for chunk in fileitem.chunks():
                        fd.write(chunk.decode('utf-8'))
            except (IOError, UnicodeDecodeError) as exc:
                # Such as if user attempted to upload a non-YANG file
                errors.append((fileitem.name, str(exc)))
    finally:
        if current < target:
            resource.setrlimit(resource.RLIMIT_NOFILE,
                               (current, hardlimit))
            log.debug("Restored RLIMIT_NOFILE to base value of %d",
                      current)

    return errors
