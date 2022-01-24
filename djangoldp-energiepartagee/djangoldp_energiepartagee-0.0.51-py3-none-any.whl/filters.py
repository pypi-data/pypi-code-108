from djangoldp.filters import LDPPermissionsFilterBackend
from rest_framework_guardian.filters import ObjectPermissionsFilter
from djangoldp.utils import is_anonymous_user


class ContributionFilterBackend(ObjectPermissionsFilter):
    def filter_queryset(self, request, queryset, view):
        if request.user.is_superuser:
            return queryset
        else:
            from .models import Relatedactor
            user_actors_id = Relatedactor.get_user_actors_id(user=request.user, role='admin')
            return queryset.filter(actor_id__in=user_actors_id)


class ProfileFilterBackend(ObjectPermissionsFilter):
    def filter_queryset(self, request, queryset, view):
        if is_anonymous_user(request.user):
            return view.model.objects.none()
        elif request.user.is_superuser:
            return queryset
        else:
            return queryset.filter(user=request.user)


class RelatedactorFilterBackend(ObjectPermissionsFilter):
    def filter_queryset(self, request, queryset, view):
        if request.user.is_superuser:
            return queryset
        else:
            from .models import Relatedactor
            user_actors_id = Relatedactor.get_user_actors_id(user=request.user)
            return queryset.filter(actor_id__in=user_actors_id)


class SuperUserOnlyFilterBackend(ObjectPermissionsFilter):
    def filter_queryset(self, request, queryset, view):
        if request.user.is_superuser:
            return queryset   
