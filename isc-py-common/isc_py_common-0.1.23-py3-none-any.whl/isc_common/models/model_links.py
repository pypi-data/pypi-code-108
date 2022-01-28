import logging

from django.db import connection
from django.db.models import Model

logger = logging.getLogger( __name__ )


class Model_links( Model ) :

    @classmethod
    def get_link( cls , model_id , model_code , model , model_link , model_link_fk ) :
        with connection.cursor() as cursor :
            cursor.execute( f'''select cml.id, cml.link
                                from {model} as lg
                                join {model_link} as lgl on lg.id = lgl.{model_link_fk}
                                join isc_common_links as cml on lgl.link_id = cml.id
                                where lg.id = %s
                                and lgl.code = %s''' , [ model_id , model_code ] )
            row = cursor.fetchone()
            if row is None :
                return None , None
            else :
                id , link = row
            return id , link

    @classmethod
    def update_or_create_link( cls , main_model , link_field_name , link , pk_name='id' ) :
        from isc_common.models.links import Links

        if link != '' or link is not None :
            if eval( f'main_model.{link_field_name} is None' , dict() , dict( main_model=main_model ) ) :
                res = eval( f'links.objects.create(link=link)' , dict() , dict( link=link , links=Links ) )
            else :
                res , _ = eval( f'links.objects.update_or_create(id=main_model.{link_field_name}.id, defaults=dict(link=link))' , dict() , dict( link=link , links=Links , main_model=main_model ) )

            eval( f'main_model._meta.concrete_model.objects.filter({pk_name}=main_model.{pk_name}).update({link_field_name}=res)' , dict() , dict( res=res , main_model=main_model ) )

    def __str__( self ) :
        return f'ID:{self.id}'

    def __repr__( self ) :
        return self.__str__()

    class Meta :
        verbose_name = 'Базовый класс'
        abstract = True
