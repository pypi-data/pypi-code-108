from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from refs.models.type_param import Type_param, Type_paramManager


@JsonResponseWithException()
def Type_param_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Type_param.objects.
                filter().
                get_range_rows1(
                request=request,
                function=Type_paramManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Type_param_Add(request):
    return JsonResponse(DSResponseAdd(data=Type_param.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Type_param_Update(request):
    return JsonResponse(DSResponseUpdate(data=Type_param.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Type_param_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Type_param.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Type_param_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Type_param.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Type_param_Info(request):
    return JsonResponse(DSResponse(request=request, data=Type_param.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Type_param_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Type_param.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
