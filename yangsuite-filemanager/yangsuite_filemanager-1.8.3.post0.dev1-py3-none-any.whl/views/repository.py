import json
import traceback

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required

from yangsuite import get_logger
from ..filemanager import (
    YSYangRepository,
    split_user_set,
    do_validation, validation_status,
)


log = get_logger(__name__)


@login_required
def manage_repos(request, repository=None):
    """Load the repo management page."""
    return render(request, 'ysfilemanager/repository.html', {
        'repository': repository or '',
    })


def repository_required(decoratee):
    """Decorator for views that expect a 'repository' arg on the given request.

    If the arg is provided and valid, it's split with :func:`split_user_set`
    and passed into the decorated function as args 'owner' and 'reponame'.

    Returns:
      JsonResponse: if repository parameter is missing or incorrect.
    """
    def decorated(request):
        if request.method == 'POST':
            repository = request.POST.get('repository')
        else:
            repository = request.GET.get('repository')

        if repository in ['', None]:
            return JsonResponse({}, status=400,
                                reason="No repository specified")

        try:
            owner, reponame = split_user_set(repository)
        except ValueError:
            return JsonResponse({}, status=400,
                                reason="Invalid repository string")

        return decoratee(request, owner, reponame)
    return decorated


@login_required
def get_repos(request):
    """Get the list of available repositories.

    Superusers can get the listing for all users; regular users
    can only access their own repositories.

    Args:
      request (django.http.HTTPRequest): HTTP GET request
    Returns:
      JsonResponse: {'repositories': {
        'user1': [set1, set2],
        'user2': [set3], ...]}
    """
    if request.user.is_superuser:
        return JsonResponse(
            {'repositories': YSYangRepository.all_repos()})
    else:
        user = request.user.username
        return JsonResponse({
            'repositories': {
                user: YSYangRepository.user_repos(user),
            }})


@login_required
@repository_required
def get_repo_contents(request, owner, reponame):
    """Get the modules available in the given repository.

    Args:
      request (django.http.HTTPRequest): HTTP GET request, with parameter
        'repository' = "username:reponame"
    Returns:
      JsonResponse: {'modules': [{name: 'name', revision: 'revision'}, {...}]}
    """
    user = request.user.username

    if user != owner and not request.user.is_superuser:
        return JsonResponse({}, status=403,
                            reason="Only superusers may access the contents "
                            "of another user's repository")
    try:
        return JsonResponse({
            'modules': [{'name': m[0], 'revision': m[1]} for m in
                        YSYangRepository(owner, reponame)
                        .get_modules_and_revisions()]})
    except OSError:
        # Most likely ENOENT or ENOTDIR
        return JsonResponse({}, status=404, reason="No such repository?")


@login_required
def create_repo(request):
    """Create a new repository.

    Args:
      request (django.http.HTTPRequest): HTTP POST request
    Returns:
      JsonResponse: nothing?
    """
    reponame = request.POST.get('reponame')

    if not reponame:
        return JsonResponse({}, status=400, reason="No repository name given")

    user = request.user.username

    srcrepo = None
    source = request.POST.get('source')
    if source:
        try:
            srcuser, srcreponame = split_user_set(source)
        except ValueError:
            return JsonResponse({}, status=400,
                                reason='Invalid source repository string')
        try:
            srcrepo = YSYangRepository(srcuser, srcreponame)
        except OSError:
            return JsonResponse({}, status=404,
                                reason='No such source repository')
    try:
        newrepo = YSYangRepository.create(user, reponame)
    except OSError:
        return JsonResponse({}, status=403,
                            reason="A repository by that name already exists")

    if srcrepo:
        newrepo.add_yang_files(srcrepo.path, remove=False)

    return JsonResponse({'repository': newrepo.slug}, status=200)


@login_required
@repository_required
def delete_repo(request, owner, reponame):
    """Delete a repository.

    Args:
      request (django.http.HTTPRequest): HTTP POST request, with parameter
        'repository' = "username:reponame"
    """
    user = request.user.username

    if user != owner and not request.user.is_superuser:
        return JsonResponse({}, status=403,
                            reason="Only superusers may delete "
                            "another user's repository")
    try:
        YSYangRepository.delete(owner, reponame)
        return JsonResponse({})
    except ValueError as e:
        log.debug(traceback.format_exc())
        return JsonResponse({}, status=400, reason="Bad request")
    except OSError:
        log.debug(traceback.format_exc())
        return JsonResponse({}, status=404, reason="No such repository?")
    except RuntimeError as e:
        log.debug(traceback.format_exc())
        return JsonResponse({}, status=403, reason=str(e))


@login_required
@repository_required
def delete_modules_from_repo(request, owner, reponame):
    """Delete modules from a repository.

    Args:
      request (django.http.HTTPRequest): HTTP POST request, with parameters
        'repository': "username:reponame", 'modules': JSON list of name,rev
    """
    user = request.user.username

    if user != owner and not request.user.is_superuser:
        return JsonResponse({}, status=403,
                            reason="Only superusers may modify "
                            "another user's repository")

    try:
        repo = YSYangRepository(owner, reponame)
    except OSError:
        return JsonResponse({}, status=404, reason="No such repository?")

    modules = request.POST.get('modules')
    if modules:
        try:
            modules = json.loads(modules)
        except ValueError:
            return JsonResponse({}, status=400,
                                reason="Invalid modules argument")
    if not modules:
        return JsonResponse({}, status=400, reason="No modules specified")

    try:
        results = repo.remove_modules(modules)
        return JsonResponse(results)
    except ValueError:
        return JsonResponse({}, status=400, reason="Bad request")


@login_required
def check_repo(request):
    """Check whether the given repository is complete and valid.

    Args:
      request (django.http.HTTPRequest): HTTP POST (begin check) or GET
        (check progress) request.
    Returns:
      JsonResponse
    """
    user = request.user.username

    if request.method == 'POST':
        repo = request.POST.get('repository')
        if not repo:
            return JsonResponse({}, status=400,
                                reason="No repository specified")

        user = request.user.username
        try:
            owner, reponame = split_user_set(repo)
        except ValueError:
            return JsonResponse({}, status=400,
                                reason="Invalid repository string")

        if user != owner and not request.user.is_superuser:
            return JsonResponse({}, status=403,
                                reason="Only superusers may validate "
                                "another user's repository")

        try:
            repo = YSYangRepository(owner, reponame)
        except OSError:
            return JsonResponse({}, status=404,
                                reason="No such repository?")
        return JsonResponse(do_validation(user, repo))
    else:
        return JsonResponse(validation_status(user))


@login_required
def show_repo_module(request, repository, module):
    """Render the contents of the requested YANG module in the given repo."""
    user = request.user.username

    try:
        repo = YSYangRepository(*split_user_set(repository))
    except OSError:
        return HttpResponse(status=404, reason="YANG repository not found")
    except ValueError:
        return HttpResponse(status=400, reason="Invalid repository string")

    if user != repo.owner and not request.user.is_superuser:
            return JsonResponse({}, status=403,
                                reason="Only superusers may access the "
                                "contents of another user's repository")

    module_path = repo.module_path(module)
    if not module_path:
        return HttpResponse(status=404, reason="Module not found")
    text = open(module_path).read()
    return render(request, 'ysfilemanager/module.html', {
        'repository': repository,
        'reponame': repo.reponame,
        'module': module,
        'lines': text.split("\n"),
    })
