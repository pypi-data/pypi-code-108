from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from twits.models.chat_user_user_theme import Chat_user_user_theme, Chat_user_user_themeManager


@JsonResponseWithException()
def Chat_user_user_theme_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Chat_user_user_theme.objects.
                filter().
                get_range_rows1(
                request=request,
                function=Chat_user_user_themeManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Chat_user_user_theme_Add(request):
    return JsonResponse(DSResponseAdd(data=Chat_user_user_theme.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Chat_user_user_theme_Update(request):
    return JsonResponse(DSResponseUpdate(data=Chat_user_user_theme.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Chat_user_user_theme_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Chat_user_user_theme.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Chat_user_user_theme_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Chat_user_user_theme.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Chat_user_user_theme_Info(request):
    return JsonResponse(DSResponse(request=request, data=Chat_user_user_theme.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Chat_user_user_theme_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Chat_user_user_theme.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
