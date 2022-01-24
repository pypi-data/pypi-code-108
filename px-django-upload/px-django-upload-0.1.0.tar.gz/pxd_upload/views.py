from typing import Type
from django.http import HttpRequest, JsonResponse
from django import forms
from hurry.filesize import size
from django.views.generic import View
from django.utils.translation import pgettext_lazy
from django.test import override_settings

from .conf import settings
from .forms import UploadForm
from .signals import upload_complete
from .models import Upload


# TODO: Move it elswhere.
def error(
    code: int, message: str, reason: str = None, domain: str = 'request',
    state: dict = None
) -> JsonResponse:
    message = {'message': message}

    if reason:
        message['reason'] = reason

    if domain:
        message['domain'] = domain

    if state:
        message['state'] = state

    return JsonResponse({'code': code, 'errors': [message]})


class UploadView(View):
    upload_prefix: str = ''
    size_limit: int = settings.SIZE_LIMIT
    allow_meta: bool = settings.ALLOW_META
    form_class: Type[forms.Form] = UploadForm

    def post(self, request: HttpRequest) -> JsonResponse:
        # TODO: Move content length check elsewhere:
        # CONTENT CHECK START.
        length = int(request.META.get('CONTENT_LENGTH') or 0)

        if length == 0:
            return error(411, pgettext_lazy(
                'pxd_upload', 'Request content-length header required.'
            ), reason='content_length_required')

        if length > self.size_limit:
            return error(
                413,
                pgettext_lazy('pxd_upload', 'File is larger than {size}.').format(
                    size=size(self.size_limit)
                ),
                reason='file_too_large'
            )
        # CONTENT CHECK END.

        # FIXME: That's not how it should be done, but it's kinda tricky to
        # get here easy and fast:
        # https://github.com/django/django/blob/0b79eb36915d178aef5c6a7bbce71b1e76d376d3/django/http/multipartparser.py#L186-L207
        with override_settings(DATA_UPLOAD_MAX_MEMORY_SIZE=self.size_limit):
            # TODO: Get rid of form validation in this package.
            # Should use faster method.
            form = self.form_class(
                data=request.POST, files=request.FILES,
                allow_meta=self.allow_meta,
            )

            if not form.is_valid():
                return error(
                    400, pgettext_lazy('pxd_upload', 'Invalid payload.'),
                    reason='payload_invalid', state=form.errors.get_json_data()
                )

        # TODO: Different uploaders for differrent content/mime types.
        # TODO: Different uploaders per view maybe.
        # TODO: Different validators per view. Now it's form, but i don't
        # like that.
        # TODO: Mime type gates.
        # TODO: Some access management here. It probably would be done
        # externally, but anyway.
        # TODO: Figure out how to use `self.upload_prefix` option.
        instance: Upload = form.save()
        upload_complete.send(Upload, instance=instance, file=instance.file)

        return JsonResponse({'code': 200, 'data': {'item': {
            'id': instance.id,
            'title': instance.title,
            'file': instance.file.url,
            'meta': instance.meta,
        }}})
