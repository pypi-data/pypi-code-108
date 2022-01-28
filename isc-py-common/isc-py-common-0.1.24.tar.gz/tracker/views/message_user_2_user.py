from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from tracker.models.message_user_2_user import Message_user_2_user, Message_user_2_userManager


@JsonResponseWithException()
def Message_user_2_user_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Message_user_2_user.objects.
                filter().
                get_range_rows1(
                request=request,
                function=Message_user_2_userManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Message_user_2_user_Add(request):
    return JsonResponse(DSResponseAdd(data=Message_user_2_user.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Message_user_2_user_Update(request):
    return JsonResponse(DSResponseUpdate(data=Message_user_2_user.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Message_user_2_user_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Message_user_2_user.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Message_user_2_user_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Message_user_2_user.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Message_user_2_user_Info(request):
    return JsonResponse(DSResponse(request=request, data=Message_user_2_user.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Message_user_2_user_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Message_user_2_user.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
