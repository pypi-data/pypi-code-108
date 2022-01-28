from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from twits.models.chat_user_user import Chat_user_user
from twits.models.chat_user_user_view import Chat_user_userView, Chat_user_userViewManager


@JsonResponseWithException()
def Chat_user_user_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Chat_user_userView.objects.
                filter().
                get_range_rows1(
                request=request,
                function=Chat_user_userViewManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Chat_user_user_Add(request):
    return JsonResponse(DSResponseAdd(data=Chat_user_user.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Chat_user_user_Update(request):
    return JsonResponse(DSResponseUpdate(data=Chat_user_user.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Chat_user_user_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Chat_user_user.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Chat_user_user_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Chat_user_user.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Chat_user_user_Info(request):
    return JsonResponse(DSResponse(request=request, data=Chat_user_userView.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Chat_user_user_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Chat_user_user.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
