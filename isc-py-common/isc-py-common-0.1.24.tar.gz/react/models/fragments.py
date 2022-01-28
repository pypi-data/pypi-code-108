import logging
from typing import List

from django.db import transaction
from django.db.models import CheckConstraint , F , Q
from isc_common import setAttr , delAttr
from isc_common.common.functions import get_dict_only_model_field
from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsBaseRefQuerySet , CommonManagetWithLookUpFieldsManager
from isc_common.models.base_ref import BaseRefHierarcy
from isc_common.models.tree_audit import TreeAuditModelManager
from react.models.fragments_item_types import Fragments_item_types

logger = logging.getLogger( __name__ )


class FragmentsQuerySet( CommonManagetWithLookUpFieldsBaseRefQuerySet ) :
    pass


class FragmentsManager( CommonManagetWithLookUpFieldsManager ) :

    def create4PageFromRequest( self , request , removed=None , propsArr=None ) :
        from react.models.page_fragments import Page_fragments

        request = DSRequest( request=request )
        data = request.get_data()
        with transaction.atomic() :
            if isinstance( data.get( 'fragments' ) , list ) and isinstance( data.get( 'page_id' ) , list ) :
                for page_id in data.get( 'page_id' ) :
                    for fragment_id in data.get( 'fragments' ) :
                        for fragment in Fragments.tree_objects.get_parents( id=fragment_id , child_id='id' , include_self=False ) :
                            Page_fragments.objects.get_or_create( page_id=page_id , fragment=fragment )

        return data

    def updateFromRequest( self , request , removed=None , function=None , propsArr: List = None ) :
        from react.models.fragment_params import Fragment_params

        request = DSRequest( request=request )
        data = request.get_data()

        data = self.check_data_for_multi_select( data=data )
        if data.get( 'mode' ) == 'move' :
            with transaction.atomic() :
                fragment = Fragments.objects.get( id=data.get( 'targetRecord' ) )

                for fragment_param in Fragment_params.objects.filter( id__in=data.get( 'dropRecords' ) ) :
                    fragment_param.fragment = fragment
                    fragment_param.save()
                return data

        _data = data.copy()

        self._remove_prop( data , removed )
        data = self._remove_prop_( data )
        if function :
            function( data )
        else :
            props = self.get_prp( data=data , propsArr=propsArr )
            cloned_data = self.clone_data( data )

            if props is not None :
                setAttr( cloned_data , 'props' , props )

            id = cloned_data.get( 'id' )
            if id is not None :
                delAttr( cloned_data , 'id' )
                parent = cloned_data.get( 'parent' )
                if isinstance( parent , int ) :
                    delAttr( cloned_data , 'parent' )
                    setAttr( cloned_data , 'parent_id' , parent )
                res = super().filter( id=id ).update( **get_dict_only_model_field( data=cloned_data , model=self.model , exclude=[ 'id' ] ) )
                # print(f'res: {res}')
            else :
                new_item = super().create( **cloned_data )
                setAttr( _data , 'id' , new_item.id )
        return _data

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
            'type_id' : record.type.id ,
            'type__name' : record.type.name ,
        }
        return res

    def get_queryset( self ) :
        return FragmentsQuerySet( self.model , using=self._db )


class Fragments( BaseRefHierarcy ) :
    type = ForeignKeyProtect( Fragments_item_types )

    objects = FragmentsManager()
    tree_objects = TreeAuditModelManager()

    def __str__( self ) :
        return f'ID:{self.id}, code: {self.code}, name: {self.name}, description: {self.description}, type: [{self.type}]'

    def __repr__( self ) :
        return self.__str__()

    class Meta :
        verbose_name = 'Структура фрагмента'
        constraints = [
            CheckConstraint( check=~Q( id=F( 'parent_id' ) ) , name=f'c_Fragments' ) ,
        ]
