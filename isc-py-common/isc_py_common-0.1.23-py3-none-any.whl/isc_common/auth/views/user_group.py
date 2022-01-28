from isc_common.auth.models.usergroup import UserGroup, GroupManager
from isc_common.common import developers
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse


@JsonResponseWithException(printing=False, printing_res=False)
def UserGroup_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=UserGroup.objects.
                # exclude(code=developers).
                exclude().
                get_range_rows1(
                request=request,
                function=GroupManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException(printing=False)
def UserGroup_Add(request):
    return JsonResponse(DSResponseAdd(data=UserGroup.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def UserGroup_Update(request):
    return JsonResponse(DSResponseUpdate(data=UserGroup.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def UserGroup_Remove(request):
    return JsonResponse(DSResponse(request=request, data=UserGroup.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def UserGroup_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=UserGroup.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def UserGroup_Info(request):
    return JsonResponse(DSResponse(request=request, data=UserGroup.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)
