import logging

from django.db.models import Model
from isc_common import setAttr , delAttr
from isc_common.bit import TurnBitOn , TurnBitOff
from isc_common.fields.code_field import CodeStrictField
from isc_common.fields.description_field import DescriptionField
from isc_common.fields.name_field import NameField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.models.audit import AuditModel , AuditManager , AuditQuerySet

logger = logging.getLogger( __name__ )


class BaseRefQuerySet( AuditQuerySet ) :

    def filter( self , *args , **kwargs ) :
        # if self.alive_only:
        #     setAttr(kwargs, 'deleted_at__isnull', True)

        key = [ key for key in kwargs.keys() if key == 'full_name' ]
        if len( key ) == 0 :
            return super().filter( *args , **kwargs )
        else :
            full_name = kwargs.get( 'full_name' )
            if full_name is not None :
                res = self.get_full_name_id( None , full_name[ 1 : ] )
                delAttr( kwargs , 'full_name' )
                setAttr( kwargs , 'pk' , res.pk )
            else :
                setAttr( kwargs , 'pk' , 0 )
            return super().filter( *args , **kwargs )

    def get_full_name_id( self , parent_id , name ) :
        end = False
        if name.find( '/' ) != -1 :
            _name = name[ :name.find( '/' ) ]
        else :
            end = True
            _name = name

        if parent_id :
            res = super().get( parent_id=parent_id , name=_name )
        else :
            res = super().get( parent__isnull=True , name=_name )

        if end :
            return res
        else :
            return self.get_full_name_id( res.id , name[ name.find( '/' ) + 1 : ] )

    def get( self , *args , **kwargs ) :
        key = [ key for key in kwargs.keys() if key == 'full_name' ]
        if len( key ) == 0 :
            res = super().get( *args , **kwargs )
        else :
            full_name = kwargs.get( 'full_name' )
            if full_name is None :
                full_name = ''
            res = self.get_full_name_id( None , full_name[ 1 : ] )

        return res

    def update( self , **kwargs ) :
        if kwargs.get( 'code' ) is None and kwargs.get( 'name' ) is not None :
            setAttr( kwargs , 'code' , AuditModel.translit( kwargs.get( 'name' ) ) )
        res = super().update( **kwargs )
        return res

    def create( self , **kwargs ) :
        if kwargs.get( 'code' ) is None and kwargs.get( 'name' ) is not None :
            setAttr( kwargs , 'code' , AuditModel.translit( kwargs.get( 'name' ) ) )
        res = super().create( **kwargs )
        return res


class BaseRefHierarcyQuerySet( BaseRefQuerySet ) :

    def filter( self , *args , **kwargs ) :
        # if self.alive_only:
        #     setAttr(kwargs, 'deleted_at__isnull', True)

        key = [ key for key in kwargs.keys() if key == 'full_name' ]
        if len( key ) == 0 :
            return super().filter( *args , **kwargs )
        else :
            full_name = kwargs.get( 'full_name' )
            if full_name is not None :
                res = self.get_full_name_id( None , full_name[ 1 : ] )
                delAttr( kwargs , 'full_name' )
                setAttr( kwargs , 'pk' , res.pk )
            else :
                setAttr( kwargs , 'pk' , 0 )
            return super().filter( *args , **kwargs )

    def get_full_name_id( self , parent_id , name ) :
        end = False
        if name.find( '/' ) != -1 :
            _name = name[ :name.find( '/' ) ]
        else :
            end = True
            _name = name

        if parent_id :
            res = super().get( parent_id=parent_id , name=_name )
        else :
            res = super().get( parent__isnull=True , name=_name )

        if end :
            return res
        else :
            return self.get_full_name_id( res.id , name[ name.find( '/' ) + 1 : ] )

    def get( self , *args , **kwargs ) :
        key = [ key for key in kwargs.keys() if key == 'full_name' ]
        if len( key ) == 0 :
            res = super().get( *args , **kwargs )
        else :
            full_name = kwargs.get( 'full_name' )
            if full_name is None :
                full_name = ''
            res = self.get_full_name_id( None , full_name[ 1 : ] )

        return res

    def update( self , **kwargs ) :
        if kwargs.get( 'code' ) is None and kwargs.get( 'name' ) is not None :
            setAttr( kwargs , 'code' , AuditModel.translit( kwargs.get( 'name' ) ) )
        res = super().update( **kwargs )
        return res

    def create( self , **kwargs ) :
        if kwargs.get( 'code' ) is None and kwargs.get( 'name' ) is not None :
            setAttr( kwargs , 'code' , AuditModel.translit( kwargs.get( 'name' ) ) )
        res = super().create( **kwargs )
        return res


class BaseRefManager( AuditManager ) :
    def get_queryset( self ) :
        if self.alive_only :
            return BaseRefQuerySet( model=self.model , alive_only=self.alive_only ).filter( deleted_at=None )
        return BaseRefQuerySet( model=self.model , alive_only=False )


class BaseRefHierarcyManager( AuditManager ) :
    def get_queryset( self ) :
        if self.alive_only :
            return BaseRefHierarcyQuerySet( model=self.model , alive_only=self.alive_only ).filter( deleted_at=None )
        return BaseRefHierarcyQuerySet( model=self.model , alive_only=False )


class StatusBaseRefManager( BaseRefManager ) :
    def createFromRequest( self , request ) :
        request = DSRequest( request=request )
        data = request.get_data()
        _data = data.copy()

        disabled = _data.get( 'disabled' )
        props = _data.get( 'props' , 0 )

        delAttr( _data , 'disabled' )
        props = TurnBitOn( props , 0 ) if disabled else TurnBitOff( props , 0 )
        setAttr( _data , 'props' , props )

        super().create( **_data )
        setAttr( data , 'props' , props )
        return data

    def updateFromRequest( self , request , removed=None , function=None ) :
        request = DSRequest( request=request )
        data = request.get_data()
        _data = data.copy()

        _data = self.delete_underscore_element( data=_data )
        disabled = _data.get( 'disabled' )
        props = _data.get( 'props' , 0 )

        delAttr( _data , 'disabled' )
        delAttr( _data , 'id' )
        props = TurnBitOn( props , 0 ) if disabled else TurnBitOff( props , 0 )
        setAttr( _data , 'props' , props )
        setAttr( data , 'props' , props )

        super().filter( id=data.get( 'id' ) ).update( **_data )
        return data


class BaseRef( AuditModel ) :
    code = CodeStrictField( unique=True )
    name = NameField()
    description = DescriptionField()

    def save( self , *args , **kwargs ) :
        if self.code is None :
            self.code = AuditModel.translit( self.name )
        super().save( *args , **kwargs )

    class Meta :
        abstract = True


class BaseHierarcy( Model ) :
    code = None
    name = None

    parent = ForeignKeyProtect( "self" , null=True , blank=True )

    def get_parent_name( self , parent , name ) :
        if not self.name :
            raise Exception( 'Name not Exists' )

        if not parent :
            return name

        item = parent
        name = f'/{item.name}{name}'
        if item.parent :
            parent = self.get_parent_name( item.parent , name )
            return parent
        return name

    def get_root( self , parent ) :

        if not parent :
            return self

        if parent.parent :
            return self.get_parent_name( parent.parent )
        return parent

    @property
    def full_name( self ) :
        if not self.name :
            if self.code :
                self.name = self.code
            else :
                raise Exception( 'Name and Code not Exists' )

        name = f'/{self.name}'
        return self.get_parent_name( self.parent , name )

    @property
    def full_name_id( self ) :
        if not self.code :
            return None

        return self.objects.get( full_name=self.full_name )

    @property
    def root( self ) :
        return self.get_root( self.parent )

    objects = BaseRefManager()
    all_objects = BaseRefManager( alive_only=False )

    class Meta :
        abstract = True


class Hierarcy( AuditModel , BaseHierarcy ) :
    class Meta :
        abstract = True


class BaseRefHierarcy( Hierarcy ) :
    code = CodeStrictField( db_index=True )
    name = NameField()
    description = DescriptionField()

    def __str__( self ) :
        return f'code: {self.code}, name: {self.name}, description: {self.description}'

    def save( self , *args , **kwargs ) :
        if self.code is None :
            self.code = AuditModel.translit( self.name )
        super().save( *args , **kwargs )

    class Meta :
        abstract = True
