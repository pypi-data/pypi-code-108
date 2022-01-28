from djangoldp.utils import is_anonymous_user, is_authenticated_user
from djangoldp.permissions import LDPBasePermission, SuperUserPermission, LDPPermissions
from djangoldp_energiepartagee.filters import *
  

class ContributionPermissions(SuperUserPermission):
    filter_backends = [ContributionFilterBackend]

    def get_object_permissions(self, request, view, obj):
        # super users have full permissions
        perms = super().get_object_permissions(request, view, obj)

        # an admin can view and change own actors
        if is_authenticated_user(request.user):
            from .models import Relatedactor

            # admins
            admin_actor_pks = Relatedactor.get_mine(user=request.user, role='admin').values_list('pk', flat=True)
            if obj.actor.pk in admin_actor_pks:
                perms = perms.union({'view', 'change'})

            # members
            member_actor_pks = Relatedactor.get_mine(user=request.user, role='member').values_list('pk', flat=True)
            if obj.actor.pk in member_actor_pks:
                perms = perms.union({'view'})

        return perms


class ProfilePermissions(SuperUserPermission):
    filter_backends = [ProfileFilterBackend]

    def get_object_permissions(self, request, view, obj):
        perms = super().get_object_permissions(request, view, obj)

        # an admin or member can view, add and change its own profile
        if request.user == obj.user:
            perms = perms.union({'view', 'change'})

        return perms


class ActorPermissions(LDPPermissions):
    filter_backends = []

    def get_object_permissions(self, request, view, obj):
        from .models import Relatedactor

        perms = super().get_object_permissions(request, view, obj)

        # an admin can change own actor
        if Relatedactor.objects.filter(user=request.user.id, actor=obj, role='admin').exists():
            perms = perms.union({'change'})

        return perms


class RelatedactorPermissions(SuperUserPermission):
    filter_backends = [RelatedactorFilterBackend]

    def get_object_permissions(self, request, view, obj):
        perms = super().get_object_permissions(request, view, obj)

        # an admin can change own relatedactor, a member can view them
        if request.user == obj.user:
            if obj.role == 'admin':
                perms = perms.union({'view', 'change'})
            else:
                perms = perms.union({'view'})
        
        # an admin can view and change relatedactors related to the actor(s) he is admin
        from .models import Relatedactor
        user_actors_id = Relatedactor.get_user_actors_id(user=request.user, role='admin')
        if obj.actor.id in user_actors_id:
            perms = perms.union({'view', 'change'})

        # a member can view relatedactors related to the actor(s) he is member
        from .models import Relatedactor
        user_actors_id = Relatedactor.get_user_actors_id(user=request.user, role='member')
        if obj.actor.id in user_actors_id:
            perms = perms.union({'view'})

        return perms

    def get_container_permissions(self, request, view, obj=None):
        perms = super().get_container_permissions(request, view, obj)
        
        if is_authenticated_user(request.user):
            perms = perms.union({'add'})

        # print(perms)
        return perms


class HasRelatedActorPermissions(SuperUserPermission):
    '''A permissions class which grants view permissions to any user associated with the actor of the model'''
    filter_backends = []

    def get_object_permissions(self, request, view, obj):
        from djangoldp_energiepartagee.models import Actor, Relatedactor

        perms = super().get_object_permissions(request, view, obj)

        if is_authenticated_user(request.user):
            related_actors = Relatedactor.get_mine(request.user)
            if hasattr(obj, 'actor') and isinstance(obj.actor, Actor):
                if related_actors.filter(actor=obj.actor).exists():
                    perms = perms.union({'view'})
            elif hasattr(obj, 'actors'):
                connected_actor_pks = obj.actors.all().values_list('pk', flat=True)
                if related_actors.filter(pk__in=connected_actor_pks).exists():
                    perms = perms.union({'view'})
            else:
                raise KeyError(str(obj) + ' must have a Key to Actor, accessible either by obj.actor or obj.actors to use RelatedActorPermissions')

        return perms


class SuperUserOnlyPermission(SuperUserPermission):
    '''super users have all permissions, everyone else has none'''
    filter_backends = [SuperUserOnlyFilterBackend]

    # def has_permission(self, request, view):
    #     if request.user.is_superuser:
    #         return True
    #     return False

    def get_object_permissions(self, request, view, obj):
        perms = super().get_object_permissions(request, view, obj)

        return perms    