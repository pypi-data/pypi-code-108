"""Views for copying YANG files over SCP."""

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from yangsuite import get_logger

from .utility import post_existing_repository_required
from ysfilemanager.scp_importer import (
    scp_status,
    scp_files_to_repository,
    scp_files_from_xe_workspace,
)

log = get_logger(__name__)


@login_required
@post_existing_repository_required
def scp_files_to_repo(request, targetrepo):
    """SCP files from the given remote directory to a repository.

    Returns:
      JsonResponse: {reply: result message}
    """
    user = request.user.username
    if request.method == 'GET':
        if user in scp_status:
            return JsonResponse(scp_status[user])
        return JsonResponse({}, status=404, reason="No copy in progress")

    host = request.POST.get('host')
    username = request.POST.get('ssh_username')
    password = request.POST.get('ssh_password')
    remote_path = request.POST.get('remote_path')
    remote_type = request.POST.get('remote_type')
    if not remote_type:
        include_subdirs = request.POST.get('include_subdirs', 'false')
        include_subdirs = (include_subdirs == 'true')

    if not (host and username and password and remote_path):
        return JsonResponse({}, status=400,
                            reason="Missing mandatory parameters")

    if remote_type == "xe_workspace":
        result = scp_files_from_xe_workspace(host, targetrepo, user,
                                             username, password,
                                             ws_root=remote_path)
    else:
        result = scp_files_to_repository(host, targetrepo, user,
                                         username, password,
                                         remote_paths=[remote_path],
                                         include_subdirs=include_subdirs)

    if result['status'] != 200:
        return JsonResponse({},
                            status=result['status'],
                            reason=result['reason'])
    else:
        return JsonResponse({'reply': result['result']})
