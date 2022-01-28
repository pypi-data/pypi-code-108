from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from twits.models.chat_users import Chat_users
from twits.models.chat_users_view import Chat_usersView, Chat_usersViewManager


@JsonResponseWithException()
def Chat_users_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Chat_usersView.objects.
                filter().
                get_range_rows1(
                request=request,
                function=Chat_usersViewManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Chat_users_Add(request):
    return JsonResponse(DSResponseAdd(data=Chat_users.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Chat_users_Update(request):
    return JsonResponse(DSResponseUpdate(data=Chat_users.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Chat_users_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Chat_users.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Chat_users_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Chat_users.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Chat_users_Info(request):
    return JsonResponse(DSResponse(request=request, data=Chat_users.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Chat_users_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Chat_users.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
