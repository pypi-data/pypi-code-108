from isc_common.common.functions import get_relation_field_name
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from tracker.models.messages_theme_users_access import MessagesThemeUsersAccess, MessagesThemeUsersAccessManager


@JsonResponseWithException()
def MessagesThemeUsersAccess_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=MessagesThemeUsersAccess.objects.
                select_related(*get_relation_field_name( model=MessagesThemeUsersAccess )).
                get_range_rows1(
                request=request,
                function=MessagesThemeUsersAccessManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def MessagesThemeUsersAccess_Add(request):
    return JsonResponse(DSResponseAdd(data=MessagesThemeUsersAccess.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def MessagesThemeUsersAccess_Update(request):
    return JsonResponse(DSResponseUpdate(data=MessagesThemeUsersAccess.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def MessagesThemeUsersAccess_Remove(request):
    return JsonResponse(DSResponse(request=request, data=MessagesThemeUsersAccess.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def MessagesThemeUsersAccess_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=MessagesThemeUsersAccess.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def MessagesThemeUsersAccess_Info(request):
    return JsonResponse(DSResponse(request=request, data=MessagesThemeUsersAccess.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def MessagesThemeUsersAccess_Copy(request):
    return JsonResponse(DSResponse(request=request, data=MessagesThemeUsersAccess.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
