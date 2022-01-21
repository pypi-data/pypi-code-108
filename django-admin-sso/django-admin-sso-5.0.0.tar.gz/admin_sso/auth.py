from django.contrib.auth import get_user_model

from admin_sso.models import Assignment


class DjangoSSOAuthBackend:
    def get_user(self, user_id):
        cls = get_user_model()
        try:
            return cls.objects.get(pk=user_id)
        except cls.DoesNotExist:
            return None

    def authenticate(self, request, **kwargs):
        sso_email = kwargs.pop("sso_email", None)

        assignment = Assignment.objects.for_email(sso_email)
        if assignment is None:
            return None

        return assignment.user
