import logging

from django.db.models import CheckConstraint , F , Q
from django.db.models import SmallIntegerField , CharField
from isc_common.fields.code_field import CodeField
from isc_common.models.base_ref import BaseRefHierarcy , BaseRefManager , BaseRefQuerySet

logger = logging.getLogger( __name__ )


class Image_typesQuerySet( BaseRefQuerySet ) :
    def create( self , **kwargs ) :
        if kwargs.get( 'keyimage' ) == 'clothes' :
            raise Exception( f'Try write: {kwargs.get( "keyimage" )}' )
        return super().create( **kwargs )


class Image_typesManager( BaseRefManager ) :

    @classmethod
    def getRecord( cls , record ) :
        res = {
            'code' : record.code ,
            'deliting' : record.deliting ,
            'description' : record.description ,
            'editing' : record.editing ,
            'id' : record.id ,
            'name' : record.name ,
            'parent' : record.parent.id if record.parent else None ,
        }
        return res

    def get_queryset( self ) :
        return Image_typesQuerySet( self.model , using=self._db )


class Image_types( BaseRefHierarcy ) :
    code = CodeField( db_index=True )
    keyimage = CharField( max_length=255 , null=True , blank=True )
    height = SmallIntegerField( null=True , blank=True )
    width = SmallIntegerField( null=True , blank=True )

    objects = Image_typesManager()

    def __str__( self ) :
        return f'ID:{self.id} code: {self.code} name: {self.name} height: {self.height} width: {self.width} keyimage: {self.keyimage}'

    def __repr__( self ) :
        return self.__str__()

    class Meta :
        verbose_name = 'Image types'
        unique_together = (('code' , 'keyimage') ,)
        constraints = [
            CheckConstraint( check=~Q( id=F( 'parent_id' ) ) , name=f'c_Event' ) ,
        ]
