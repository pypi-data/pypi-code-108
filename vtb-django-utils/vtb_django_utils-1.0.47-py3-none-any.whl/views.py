from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View
from mozilla_django_oidc.views import OIDCLogoutView

from vtb_django_utils.utils.settings import get_settings


def keycloak_logout(request):
    """ logout endpoint URL """
    logout_endpoint = get_settings('OIDC_OP_LOGOUT_ENDPOINT')
    return logout_endpoint + '?redirect_uri=' + request.build_absolute_uri(get_settings('LOGOUT_REDIRECT_URL'))


class KeycloakOIDCLoginView(View):
    """ Login view """

    next_uri = None

    def get(self, request):
        """ Login method """
        login_endpoint = reverse('oidc_authentication_init')

        if self.next_uri:
            login_endpoint = login_endpoint + '?next=' + \
                             request.build_absolute_uri(self.next_uri)

        return HttpResponseRedirect(login_endpoint)


class KeycloakOIDCLogoutView(OIDCLogoutView):
    """ Logout view """

    def get(self, request):
        """ Logout view """
        return self.post(request)
