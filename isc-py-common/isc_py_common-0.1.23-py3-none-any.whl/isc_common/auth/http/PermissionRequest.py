from isc_common.auth.models.user import User
from isc_common.auth.models.usergroup import UserGroup
from isc_common.http.DSRequest import DSRequest
from isc_common.http.RPCResponse import RPCResponseConstant


class PermissionRequest( DSRequest ) :
    def __init__( self , request ) :
        from permission.models.user_permission import User_permission
        from permission.models.widgets_trees import Widgets_trees

        DSRequest.__init__( self , request )
        data = self.get_data()
        table = data.get( 'table' , None )
        id = data.get( 'id' , None )
        id_widget = data.get( 'id_widget' , None )

        if table :
            if id is not None and id_widget :
                structure = dict()
                if table == 'widgets_trees' :
                    structure = Widgets_trees.objects.get_or_create( id_widget=id_widget )[ 0 ].structure

                if table == 'user' :
                    user = User.objects.get( id=id )
                    widget = Widgets_trees.objects.get_or_create( id_widget=id_widget )[ 0 ]

                    structure = User_permission.objects.get_or_create( user=user , widget=widget )[ 0 ].permission

                if table == 'user_group' :
                    usergroup = UserGroup.objects.get( id=id )
                    widget = Widgets_trees.objects.get_or_create( id_widget=id_widget )[ 0 ]

                self.response = dict( response=dict( status=RPCResponseConstant.statusSuccess ) , data=structure )
        else :
            raise Exception( f"Check table: {table},  id: {id}" )
