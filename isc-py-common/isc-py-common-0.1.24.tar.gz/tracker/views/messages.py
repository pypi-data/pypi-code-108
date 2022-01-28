from isc_common.common.functions import get_relation_field_name
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException, JsonWSResponseWithException, JsonWSPostResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from tracker.models.messages import Messages, MessagesManager
from tracker.views.message_confirm_reading import DSResponse__Messages_Confirm_reading
from tracker.views.message_download_file import message_download_file
from tracker.views.messages_upload1_file import DSResponse__Messages_UploadFile1
from tracker.views.messages_upload_file import DSResponse__Messages_UploadFile


@JsonResponseWithException(printing=False)
def Messages_Fetch(request):
    response = DSResponse(
        request=request,
        data=Messages.objects.
            select_related(*get_relation_field_name( model=Messages )).
            get_range_rows1(
            request=request,
            function=MessagesManager.getRecord
        ),
        status=RPCResponseConstant.statusSuccess).response
    return JsonResponse(response)


@JsonResponseWithException(printing=False)
def Messages_Fetch4Chat(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Messages.objects.
                get_range_rows1(
                request=request,
                function=MessagesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_Add(request):
    return JsonResponse(DSResponseAdd(data=Messages.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_Add_Auto_Error(request):
    return JsonResponse(DSResponseAdd(data=Messages.objects.createAutoErrorFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_Update(request):
    return JsonResponse(DSResponseUpdate(data=Messages.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Messages.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Messages.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException(printing=False)
def Messages_Info(request):
    return JsonResponse(DSResponse(request=request, data=Messages.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonWSResponseWithException()
def Messages_UploadFile(request):
    return JsonResponse(DSResponse__Messages_UploadFile(request).response)


@JsonWSResponseWithException()
def Messages_UploadFile1(request):
    response = DSResponse__Messages_UploadFile1(request).response
    return JsonResponse(response)


@JsonWSPostResponseWithException()
def Messages_Confirm_reading(request):
    return JsonResponse(DSResponse__Messages_Confirm_reading(request).response)


@JsonWSResponseWithException(printing=False)
def Message_DownloadFile(request, id):
    return message_download_file(request, id)
