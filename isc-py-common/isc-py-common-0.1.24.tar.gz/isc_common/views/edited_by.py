from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from isc_common.models.edited_by import Edited_by, Edited_byManager


@JsonResponseWithException()
def Edited_by_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Edited_by.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Edited_byManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Edited_by_Add(request):
    return JsonResponse(DSResponseAdd(data=Edited_by.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Edited_by_Update(request):
    return JsonResponse(DSResponseUpdate(data=Edited_by.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Edited_by_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Edited_by.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Edited_by_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Edited_by.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Edited_by_Info(request):
    return JsonResponse(DSResponse(request=request, data=Edited_by.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Edited_by_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Edited_by.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
