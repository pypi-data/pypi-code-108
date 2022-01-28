from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from isc_common.models.phones import Phones, PhonesManager


@JsonResponseWithException()
def Phones_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Phones.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=PhonesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Phones_Add(request):
    return JsonResponse(DSResponseAdd(data=Phones.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Phones_Update(request):
    return JsonResponse(DSResponseUpdate(data=Phones.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Phones_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Phones.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Phones_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Phones.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Phones_Info(request):
    return JsonResponse(DSResponse(request=request, data=Phones.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Phones_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Phones.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
