import rest_framework
from graphene_django.views import GraphQLView
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings


class DRFAuthenticatedGraphQLView(GraphQLView):
    def parse_body(self, request):
        if isinstance(request, rest_framework.request.Request):
            return request.data
        return super(DRFAuthenticatedGraphQLView, self).parse_body(request)

    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super(DRFAuthenticatedGraphQLView, cls).as_view(*args, **kwargs)
        view = authentication_classes(api_settings.DEFAULT_AUTHENTICATION_CLASSES)(view)

        # it's not possible to use stricter permissions e.g Django Model permissions
        # because the GraphQL view cannot be associatded with one queryset
        view = permission_classes((IsAuthenticated,))(view)

        view = api_view(["GET", "POST"])(view)
        return view
