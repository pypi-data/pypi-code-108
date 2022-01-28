import logging

from bitfield import BitField
from django.db.models import CheckConstraint , F , Q
from isc_common import delAttr
from isc_common.bit import IsBitOn
from isc_common.fields.code_field import CodeStrictField
from isc_common.http.DSRequest import DSRequest
from isc_common.models.base_ref import BaseRefHierarcy , BaseRefManager , BaseRefQuerySet

logger = logging.getLogger( __name__ )


class Event_typesQuerySet( BaseRefQuerySet ) :
    pass


class Event_typesManager( BaseRefManager ) :

    @classmethod
    def getRecord( cls , record ) :
        res = {
            'id' : record.id ,
            'code' : record.code ,
            'name' : record.name ,
            'description' : record.description ,
            'parent_id' : record.parent.id if record.parent else None ,
            'props' : record.props._value ,
            'isEvent' : IsBitOn( record.props._value , 0 ) ,
            'compulsory_reading' : IsBitOn( record.props._value , 1 ) ,
        }
        return res

    def get_queryset( self ) :
        return Event_typesQuerySet( self.model , using=self._db )

    def updateFromRequest( self , request , removed=None , function=None ) :
        request = DSRequest( request=request )
        data = request.get_data()
        _data = data.copy()
        delAttr( _data , 'id' )
        delAttr( _data , 'isEvent' )
        delAttr( _data , 'isFolder' )
        delAttr( _data , 'compulsory_reading' )

        res = super().filter( id=data.get( 'id' ) ).update( **_data )
        return data


class Event_types( BaseRefHierarcy ) :
    code = CodeStrictField( unique=True )
    props = BitField( flags=(
        ('isEvent' , 'Является событием') ,  # 1
        ('compulsory_reading' , 'Обязательное прочтение') ,  # 2
    ) , default=0 , db_index=True )

    objects = Event_typesManager()

    def __str__( self ) :
        return f"ID:{self.id}, code: {self.code}, name: {self.name}, description: {self.description}"

    class Meta :
        verbose_name = 'Типы событий'
        constraints = [
            CheckConstraint( check=~Q( id=F( 'parent_id' ) ) , name=f'c_Event_types' ) ,
        ]
