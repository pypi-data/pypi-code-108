from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from tracker.models.messages_importance import Messages_importanceManager, Messages_importance


@JsonResponseWithException()
def Messages_importance_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Messages_importance.objects.
                filter().
                get_range_rows1(
                request=request,
                function=Messages_importanceManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_importance_Add(request):
    return JsonResponse(DSResponseAdd(data=Messages_importance.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_importance_Update(request):
    return JsonResponse(DSResponseUpdate(data=Messages_importance.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_importance_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Messages_importance.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_importance_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Messages_importance.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_importance_Info(request):
    return JsonResponse(DSResponse(request=request, data=Messages_importance.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_importance_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Messages_importance.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
