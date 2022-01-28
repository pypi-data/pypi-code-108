from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from permission.models.user_permission import User_permission


@JsonResponseWithException()
def User_permission_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=User_permission.objects.
                filter().
                get_range_rows1(
                request=request,
                # function=XXX.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def User_permission_Add(request):
    return JsonResponse(DSResponseAdd(data=User_permission.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def User_permission_Update(request):
    return JsonResponse(DSResponseUpdate(data=User_permission.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def User_permission_Remove(request):
    return JsonResponse(DSResponse(request=request, data=User_permission.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def User_permission_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=User_permission.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
