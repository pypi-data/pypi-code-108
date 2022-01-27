import base64
import io
import mimetypes
import magic
from io import BytesIO
from django.utils.module_loading import import_string
from django.conf import settings
from django.http import Http404, FileResponse
from .redis.client import RedisWrapper
from django.views import View
from wsgiref.util import FileWrapper


class AbstractDownloadDocumentView(View):
    http_method_names = ('get',)

    def get(self, request, *args, **kwargs):
        token = kwargs.get('token')
        if not token:
            raise Http404

        properties = RedisWrapper.get_dict(token)
        base_class = import_string(settings.HTG_URL_SETTINGS.get('HTG_WRAPPER_CLASS'))

        if not properties or not base_class:
            raise Http404

        instance = base_class(**properties)
        doc_identifier = instance.get_doc_identifier()

        # get document base64 string from Redis
        document_string = RedisWrapper.get(doc_identifier)
        if document_string:
            return self._get_file(document_string)

        # get document base64 string from API request
        fetcher_class = import_string(settings.HTG_URL_SETTINGS.get('DOC_WRAPPER_CLASS'))
        if not fetcher_class:
            raise Http404
        document_string = fetcher_class.fetch_document_from_sap(**properties)
        if document_string:
            RedisWrapper.set(doc_identifier, document_string)
            instance.update_ttl(token)
            return self._get_file(document_string)

        raise Http404

    @staticmethod
    def _get_file(document_string):
        buffer = BytesIO()
        buffer.write(base64.b64decode(document_string))
        buffer.seek(io.SEEK_SET)

        mime_type = magic.from_buffer(buffer.getvalue(), True)
        extension = mimetypes.guess_extension(mime_type)

        buffer.seek(io.SEEK_SET)

        return FileResponse(
            FileWrapper(buffer),
            as_attachment=True,
            filename=f'document{extension}',
            content_type=mime_type
        )
