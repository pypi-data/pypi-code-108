from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from isc_common.models.e_mails import E_mails, E_mailsManager


@JsonResponseWithException()
def E_mails_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=E_mails.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=E_mailsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def E_mails_Add(request):
    return JsonResponse(DSResponseAdd(data=E_mails.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def E_mails_Update(request):
    return JsonResponse(DSResponseUpdate(data=E_mails.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def E_mails_Remove(request):
    return JsonResponse(DSResponse(request=request, data=E_mails.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def E_mails_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=E_mails.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def E_mails_Info(request):
    return JsonResponse(DSResponse(request=request, data=E_mails.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def E_mails_Copy(request):
    return JsonResponse(DSResponse(request=request, data=E_mails.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
