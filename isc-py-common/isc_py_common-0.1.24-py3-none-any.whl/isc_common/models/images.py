import logging

from crypto.models.crypto_file import Crypto_file , CryptoManager , CryptoQuerySet
from isc_common.fields.code_field import CodeField
from isc_common.models.audit import Manager

logger = logging.getLogger( __name__ )


class ImagesQuerySet( CryptoQuerySet ) :
    pass


class ImagesManager( CryptoManager ) :

    @classmethod
    def getRecord( cls , record ) :
        res = {
            'id' : record.id ,
            'editing' : record.editing ,
            'deliting' : record.deliting ,
        }
        return res

    def get_queryset( self ) :
        return ImagesQuerySet( self.model , using=self._db )


class Images( Crypto_file ) :
    file_name = CodeField()
    objects = ImagesManager()
    objects1 = Manager()

    def __str__( self ) :
        return f'ID:{self.id} size: {self.size} real_name: {self.real_name}, attfale: {str( self.attfile )}'

    def __repr__( self ) :
        return self.__str__()

    class Meta :
        verbose_name = 'Разные картинки '
        unique_together = (('file_name' , 'size' ,) , ('real_name' , 'size' ,))
