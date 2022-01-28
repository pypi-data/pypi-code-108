from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from react.models.fragment_params import Fragment_params
from react.models.fragment_params_upload_image import DSResponse_Fragment_params_UploadImage
from react.models.fragment_params_view import Fragment_params_view, Fragment_params_viewManager


@JsonResponseWithException()
def Fragment_params_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Fragment_params_view.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Fragment_params_viewManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fragment_params_Add(request):
    return JsonResponse(DSResponseAdd(data=Fragment_params.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fragment_params_Update(request):
    return JsonResponse(DSResponseUpdate(data=Fragment_params.objects.updateFromRequest(request,propsArr=['use_generator']), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fragment_params_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Fragment_params.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fragment_params_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Fragment_params.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fragment_params_Info(request):
    return JsonResponse(DSResponse(request=request, data=Fragment_params.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fragment_params_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Fragment_params.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fragment_params_ImagesUpload(request):
    DSResponse_Fragment_params_UploadImage(request)
    return JsonResponse(dict(status=RPCResponseConstant.statusSuccess))
