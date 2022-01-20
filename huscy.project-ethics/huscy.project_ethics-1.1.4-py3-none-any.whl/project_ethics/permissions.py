from rest_framework.permissions import BasePermission


class EthicPermission(BasePermission):

    def has_permission(self, request, view):
        if request.method == 'POST':
            return (request.user.has_perm('projects.change_project') or
                    request.user.has_perm('projects.change_project', view.project))

        return True

    def has_object_permission(self, request, view, obj):
        return (request.user.has_perm('projects.change_project') or
                request.user.has_perm('projects.change_project', view.project))


class EthicsFilePermission(BasePermission):

    def has_permission(self, request, view):
        if request.method == 'POST':
            return (request.user.has_perm('projects.change_project') or
                    request.user.has_perm('projects.change_project', view.ethics.project))

        return True

    def has_object_permission(self, request, view, obj):
        can_change_project = (
            request.user.has_perm('projects.change_project') or
            request.user.has_perm('projects.change_project', view.ethics.project)
        )

        if not can_change_project:
            return False

        '''
        if request.method == 'DELETE':
            return request.user.has_perm('project_ethics.delete_ethicfile')
        '''

        return True
