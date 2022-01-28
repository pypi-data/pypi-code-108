from clndr.models.day import Day, DayManager
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse


@JsonResponseWithException()
def Day_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Day.objects.
                filter().
                get_range_rows1(
                request=request,
                function=DayManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Day_Add(request):
    return JsonResponse(DSResponseAdd(data=Day.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Day_Update(request):
    return JsonResponse(DSResponseUpdate(data=Day.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Day_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Day.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Day_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Day.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Day_Info(request):
    return JsonResponse(DSResponse(request=request, data=Day.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Day_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Day.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
