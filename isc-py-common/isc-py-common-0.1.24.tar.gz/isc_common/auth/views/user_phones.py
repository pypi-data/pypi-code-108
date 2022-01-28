from isc_common.auth.models.user_phones import User_phones, User_phonesManager
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse


@JsonResponseWithException()
def User_phones_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=User_phones.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=User_phonesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def User_phones_Add(request):
    return JsonResponse(DSResponseAdd(data=User_phones.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def User_phones_Update(request):
    return JsonResponse(DSResponseUpdate(data=User_phones.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def User_phones_Remove(request):
    return JsonResponse(DSResponse(request=request, data=User_phones.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def User_phones_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=User_phones.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def User_phones_Info(request):
    return JsonResponse(DSResponse(request=request, data=User_phones.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def User_phones_Copy(request):
    return JsonResponse(DSResponse(request=request, data=User_phones.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
