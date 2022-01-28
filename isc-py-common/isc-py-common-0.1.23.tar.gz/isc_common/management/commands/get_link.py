import logging

from django.core.management import BaseCommand
from isc_common.models.model_links import Model_links
from isc_common.models.text_informations import Text_informationsManager

logger = logging.getLogger( __name__ )


class Command( BaseCommand ) :
    def handle( self , *args , **options ) :
        print( Model_links.get_link(
            model_id=14451 ,
            model_code='bg_link' ,
            model='competitions_leagues' ,
            model_link='competitions_leagues_links' ,
            model_link_fk='league_id'
        ) )

        print(
            Text_informationsManager.get_text(
                model_id=14394 ,
                model_code='contacts' ,
                model='competitions_leagues' ,
                model_text='competitions_leagues_text_informations' ,
                model_text_fk='league_id'
            )
        )
