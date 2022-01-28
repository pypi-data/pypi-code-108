from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from isc_common.models.progresses import Progresses, ProgressesManager


@JsonResponseWithException()
def Progresses_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Progresses.objects.
                filter().
                get_range_rows1(
                request=request,
                function=ProgressesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Progresses_Add(request):
    return JsonResponse(DSResponseAdd(data=Progresses.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Progresses_Update(request):
    return JsonResponse(DSResponseUpdate(data=Progresses.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Progresses_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Progresses.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Progresses_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Progresses.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Progresses_Info(request):
    return JsonResponse(DSResponse(request=request, data=Progresses.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Progresses_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Progresses.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)

@JsonResponseWithException()
def Progresses_Resore(request):
    return JsonResponse(DSResponse(request=request, data=Progresses.objects.resoreFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
