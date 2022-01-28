import logging

from bitfield import BitField
from django.db.models import CheckConstraint , F , Q
from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsManager , CommonManagetWithLookUpFieldsBaseRefQuerySet
from isc_common.models.base_ref import BaseRefHierarcy
from isc_common.models.tree_audit import TreeAuditModelManager
from react.models.page_level_types import Page_level_types

logger = logging.getLogger( __name__ )


class PagesQuerySet( CommonManagetWithLookUpFieldsBaseRefQuerySet ) :
    pass


class PagesManager( CommonManagetWithLookUpFieldsManager ) :
    def generateFromRequest( self , request ) :
        from react.models.generators import TypeScriptGenerator

        request = DSRequest( request=request )
        data = request.get_data()

        TypeScriptGenerator().generate( data=data , user=request.user )

        return data

    @classmethod
    def props( cls ) :
        return BitField( flags=(
            ('application' , 'Приложение') ,  # 1
        ) , default=0 , db_index=True )

    @classmethod
    def getRecord( cls , record ) :
        res = {
            'code' : record.code ,
            'deliting' : record.deliting ,
            'description' : record.description ,
            'editing' : record.editing ,
            'id' : record.id ,
            'name' : record.name ,
            'parent_id' : record.parent.id if record.parent else None ,
            'type__name' : record.type.name ,
            'type_id' : record.type.id ,
        }
        return res

    def get_queryset( self ) :
        return PagesQuerySet( self.model , using=self._db )


class Pages( BaseRefHierarcy ) :
    type = ForeignKeyProtect( Page_level_types )
    props = PagesManager.props()

    objects = PagesManager()
    tree_objects = TreeAuditModelManager()

    def __str__( self ) :
        return f'ID:{self.id}, code: {self.code}, name: {self.name}, description: {self.description}, type: [{self.type}]'

    def __repr__( self ) :
        return self.__str__()

    class Meta :
        verbose_name = 'Структура страницы'
        constraints = [
            CheckConstraint( check=~Q( id=F( 'parent_id' ) ) , name=f'c_Pages' ) ,
        ]
