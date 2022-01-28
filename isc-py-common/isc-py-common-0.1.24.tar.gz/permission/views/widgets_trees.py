from isc_common.http.DSResponse import DSResponseUpdate , DSResponseAdd , DSResponse , JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from permission.models.widgets_trees import Widgets_trees , Widgets_treesManager


@JsonResponseWithException( printing=False )
def Widgets_trees_Fetch( request ) :
    return JsonResponse(
        DSResponse(
            request=request ,
            data=Widgets_trees.objects.
                filter().
                get_range_rows1(
                request=request ,
                function=Widgets_treesManager.getRecord
            ) ,
            status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def Widgets_trees_Add( request ) :
    return JsonResponse( DSResponseAdd( data=Widgets_trees.objects.createFromRequest( request=request ) , status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def Widgets_trees_Update( request ) :
    return JsonResponse( DSResponseUpdate( data=Widgets_trees.objects.updateFromRequest( request ) , status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException( printing=False )
def Widgets_trees_Remove( request ) :
    return JsonResponse( DSResponse( request=request , data=Widgets_trees.objects.deleteFromRequest( request=request ) , status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def Widgets_trees_Lookup( request ) :
    return JsonResponse( DSResponse( request=request , data=Widgets_trees.objects.lookupFromRequest( request=request ) , status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def Widgets_trees_Info( request ) :
    return JsonResponse( DSResponse( request=request , data=Widgets_trees.objects.get_queryset().get_info( request=request ) , status=RPCResponseConstant.statusSuccess ).response )
