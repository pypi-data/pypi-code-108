from rest_framework.permissions import BasePermission


class SurveyManagerPermission(BasePermission):
    def has_permission(self, request, view):
        """
        Allows access only to survey managers.
        Managers can create, update and list surveys, other users can view details
        """
        user = request.user
        view_manager = not (
            "pk" in request.parser_context["kwargs"] and request.method == "GET"
        )  # allow only retieve
        return not view_manager or (
            user
            and hasattr(user, "can_manage_surveys")
            and user.can_manage_surveys(request=request, view=view)
        )

    def has_object_permission(self, request, view, obj):
        """
        controle who can see a specific survey.
        """
        user = request.user
        return (
            user
            and hasattr(user, "can_see_survey")
            and user.can_see_survey(request=request, view=view, obj=obj)
        )
