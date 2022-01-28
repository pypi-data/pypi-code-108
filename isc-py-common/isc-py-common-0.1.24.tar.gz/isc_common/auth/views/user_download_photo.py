import os
import urllib.request

from django.http import HttpResponse

from isc_common.auth.models.user import User
from isc_common.common.UploadItem import UploadItem
from isc_common.http.DSResponse import JsonResponseWithException


@JsonResponseWithException()
def user_download_photo(request):
    id = request.GET.get('id')
    obj = User.objects.get(id=id)
    item = UploadItem(stored_file_name=os.path.basename(obj.attfile.path), key=obj.key)
    if obj.key:
        path_decrypt = item.decrypt()
    else:
        path_decrypt = item.full_path

    with open(path_decrypt, 'rb') as fh:
        response = HttpResponse(fh.read(), content_type=obj.mime_type)
        response['Content-Disposition'] = f'attachment; filename="{urllib.request.quote(obj.real_name)}"'
        response['Content-Length'] = str(os.stat(path_decrypt).st_size)
        fh.close()
        if obj.key:
            os.remove(path_decrypt)
        return response
