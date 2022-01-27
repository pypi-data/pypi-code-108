from django.conf import settings
from django.http.response import JsonResponse
from django.utils import translation

from babel import Locale

from pfx.pfxcore.decorator import rest_api, rest_view

from .rest_views import BaseRestView


def get_locales():
    return [
        dict(
            pk=code,
            name=Locale.parse(translation.to_locale(code)).get_display_name())
        for code, __ in settings.LANGUAGES]


@rest_view("/locales")
class LocaleRestView(BaseRestView):
    @rest_api('/languages', public=True)
    def locales(self):
        locales = get_locales()
        return JsonResponse({
            'items': locales, 'meta': {'count': len(locales)}})
