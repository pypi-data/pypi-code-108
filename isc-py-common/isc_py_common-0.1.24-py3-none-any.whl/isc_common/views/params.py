from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from isc_common.models.params import Params, ParamsManager


@JsonResponseWithException()
def Params_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Params.objects.
                filter().
                get_range_rows1(
                request=request,
                function=ParamsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Params_Add(request):
    return JsonResponse(DSResponseAdd(data=Params.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException(printing=False)
def Params_Update(request):
    return JsonResponse(DSResponseUpdate(data=Params.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException(printing=False)
def Params_Update1(request):
    return JsonResponse(DSResponseUpdate(data=Params.objects.update1FromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Params_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Params.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Params_Remove1(request):
    return JsonResponse(DSResponse(request=request, data=Params.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Params_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Params.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Params_Info(request):
    return JsonResponse(DSResponse(request=request, data=Params.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Params_Get(request):
    return JsonResponse(DSResponse(request=request, data=Params.objects.get_queryset().get_params(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Params_GetKeyValue(request):
    return JsonResponse(DSResponse(request=request, data=Params.objects.get_queryset().get_params_key(request=request), status=RPCResponseConstant.statusSuccess).response)
