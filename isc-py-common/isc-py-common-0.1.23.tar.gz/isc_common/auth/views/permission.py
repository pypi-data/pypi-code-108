from isc_common.auth.http.PermissionRequest import PermissionRequest
from isc_common.http.DSResponse import JsonResponseWithException
from isc_common.http.response import JsonResponse


@JsonResponseWithException(printing=False)
def permission_view(request):
    return JsonResponse(PermissionRequest(request).response)
