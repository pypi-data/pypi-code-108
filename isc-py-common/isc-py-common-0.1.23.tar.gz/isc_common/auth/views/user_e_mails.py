from isc_common.auth.models.user_e_mails import User_e_mails, User_e_mailsManager
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse


@JsonResponseWithException()
def User_e_mails_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=User_e_mails.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=User_e_mailsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def User_e_mails_Add(request):
    return JsonResponse(DSResponseAdd(data=User_e_mails.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def User_e_mails_Update(request):
    return JsonResponse(DSResponseUpdate(data=User_e_mails.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def User_e_mails_Remove(request):
    return JsonResponse(DSResponse(request=request, data=User_e_mails.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def User_e_mails_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=User_e_mails.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def User_e_mails_Info(request):
    return JsonResponse(DSResponse(request=request, data=User_e_mails.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def User_e_mails_Copy(request):
    return JsonResponse(DSResponse(request=request, data=User_e_mails.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
