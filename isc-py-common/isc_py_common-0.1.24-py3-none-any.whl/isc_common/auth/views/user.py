from isc_common.auth.models.user import User , UserManager
from isc_common.auth.models.user_view import UserView , UserViewManager
from isc_common.http.DSRequest import DSRequest
from isc_common.http.DSResponse import DSResponseUpdate , DSResponseAdd , DSResponse , JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse


@JsonResponseWithException( printing=False )
def User_Fetch( request ) :
    _request = DSRequest( request )
    return JsonResponse(
        DSResponse(
            request=request ,
            data=UserView.objects.
                exclude( id=0 ).
                distinct().
                get_range_rows11(
                request=request ,
                function=UserManager.getRecord
            ) ,
            status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException( printing=False )
def User_FetchExclBots( request ) :
    return JsonResponse(
        DSResponse(
            request=request ,
            data=UserView.objects.
                exclude( props=User.props.bot ).
                exclude( id=0 ).
                distinct().
                get_range_rows11(
                request=request ,
                function=UserManager.getRecord
            ) ,
            status=RPCResponseConstant.statusSuccess ).response ) @ JsonResponseWithException( printing=False )


def User_Fetch_User_DS4( request ) :
    return JsonResponse(
        DSResponse(
            request=request ,
            data=UserView.objects.
                exclude( props=User.props.bot ).
                exclude( id=0 ).
                distinct().
                get_range_rows1(
                request=request ,
                function=UserViewManager.getRecord
            ) ,
            status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def User_Add( request ) :
    return JsonResponse( DSResponseAdd( data=User.objects.createFromRequest( request=request ) , status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException( printing=False )
def User_Update( request ) :
    return JsonResponse( DSResponseUpdate( data=User.objects.updateFromRequest( request ) , status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def User_Remove( request ) :
    return JsonResponse( DSResponse( request=request , data=User.objects.deleteFromRequest( request=request ) , status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def User_Lookup( request ) :
    return JsonResponse( DSResponse( request=request , data=User.objects.lookupFromRequest( request=request ) , status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def User_Info( request ) :
    return JsonResponse( DSResponse( request=request , data=User.objects.get_queryset().get_info( request=request ) , status=RPCResponseConstant.statusSuccess ).response )
