from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from react.models.fragments_4_page_view import Fragments_4_page_view, Fragments_4_page_viewManager


@JsonResponseWithException()
def Fragments_4_page_view_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Fragments_4_page_view.objects.
                filter().
                get_range_rows1(
                request=request,
                function=Fragments_4_page_viewManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fragments_4_page_view_Add(request):
    return JsonResponse(DSResponseAdd(data=Fragments_4_page_view.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fragments_4_page_view_Update(request):
    return JsonResponse(DSResponseUpdate(data=Fragments_4_page_view.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fragments_4_page_view_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Fragments_4_page_view.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fragments_4_page_view_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Fragments_4_page_view.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fragments_4_page_view_Info(request):
    return JsonResponse(DSResponse(request=request, data=Fragments_4_page_view.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fragments_4_page_view_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Fragments_4_page_view.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
