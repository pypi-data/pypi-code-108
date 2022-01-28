from isc_common.auth.http.get_permission_request import GetPermissionRequest
from isc_common.http.DSResponse import JsonResponseWithException
from isc_common.http.response import JsonResponse


@JsonResponseWithException(printing=False)
def get_permission_view(request):
    return JsonResponse(GetPermissionRequest(request).response)
