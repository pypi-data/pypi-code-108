from django.http import JsonResponse
from .. import split_user_set, YSYangRepository


def post_existing_repository_required(decoratee):
    """Decorator for views that expect a 'repository' arg on the given request.

    If the repository arg is provided and valid, the given repository will
    be loaded and passed into the decoratee as param 'targetrepo'.
    """
    def decorated(request):
        if request.method != 'POST':
            return decoratee(request, targetrepo=None)

        user = request.user.username
        repo = request.POST.get('repository')
        if not repo:
            return JsonResponse({}, status=400,
                                reason="No repository specified")

        try:
            owner, reponame = split_user_set(repo)
        except ValueError:
            return JsonResponse({}, status=400,
                                reason="Invalid repository parameter")

        if user != owner and not request.user.is_superuser:
            return JsonResponse({}, status=403,
                                reason="Only superusers may modify the "
                                "contents of another user's repository")

        try:
            targetrepo = YSYangRepository(owner, reponame)
        except (ValueError, OSError):
            return JsonResponse({}, status=404, reason="No such repository")

        return decoratee(request, targetrepo=targetrepo)

    return decorated
