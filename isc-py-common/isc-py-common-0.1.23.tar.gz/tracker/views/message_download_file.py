import os
import urllib.request

from django.conf import settings
from django.http import HttpResponse

from isc_common.common.UploadItem import UploadItem
from tracker.models.messages_files import Messages_files


def message_download_file(request, id):
    obj = Messages_files.objects.get(id=id)
    if os.path.exists(obj.attfile.name):
        path = obj.attfile.path
    else:
        path = obj.attfile.name
        file_name = path.split(os.sep)[-1]
        path = f'{settings.FILES_STORE}{os.sep}{file_name}'
        if not os.path.exists(path):
            raise Exception(f'Path: {path} not exists.')

    item = UploadItem(stored_file_name=os.path.basename(path), key=obj.key)
    if obj.key:
        path_decrypt = item.decrypt()
    else:
        path_decrypt = item.full_path

    with open(path_decrypt, 'rb') as fh:
        response = HttpResponse(fh.read(), content_type=obj.mime_type)
        # response['Content-Disposition'] = f'attachment; filename="{urllib.request.quote(obj.real_name.encode("utf-8"))}"'
        response['Content-Disposition'] = f'attachment; filename="{urllib.request.quote(obj.real_name)}"'
        response['Content-Length'] = str(os.stat(path_decrypt).st_size)
        fh.close()
        if obj.key:
            os.remove(path_decrypt)
        return response
