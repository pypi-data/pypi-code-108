import logging

from django.contrib.postgres.fields import ArrayField
from django.db.models import BigIntegerField

from isc_common.auth.models.user import User
from isc_common.fields.code_field import CodeField
from isc_common.fields.name_field import NameField
from isc_common.models.audit import AuditManager , AuditQuerySet

logger = logging.getLogger( __name__ )


class UserViewQuerySet( AuditQuerySet ) :
    pass


class UserViewManager( AuditManager ) :

    @classmethod
    def getRecord( cls , **kwargs ) :
        record = kwargs.get( 'record' )
        res = {
            'deliting' : record.deliting ,
            'description' : record.description ,
            'e_mails' : '<br>'.join( record.e_mails ) ,
            'editing' : record.editing ,
            'first_name' : record.first_name ,
            'id' : record.id ,
            'last_login' : record.last_login ,
            'last_name' : record.last_name ,
            'lastmodified' : record.lastmodified ,
            'middle_name' : record.middle_name ,
            'password' : record.password ,
            'phones' : '<br>'.join( record.phones ) ,
            'username' : record.username ,
        }
        return res

    def get_queryset( self ) :
        return UserViewQuerySet( self.model , using=self._db )


class UserView( User ) :
    e_mail_ids = ArrayField( BigIntegerField() , null=True , blank=True , )
    e_mails = ArrayField( CodeField() , null=True , blank=True , )
    full_user_name = NameField()
    phone_ids = ArrayField( BigIntegerField() , null=True , blank=True , )
    phones = ArrayField( CodeField() , null=True , blank=True , )
    short_user_name = NameField()

    objects = UserViewManager()

    class Meta :
        verbose_name = 'Пользователь'
        managed = False
        db_table = 'isc_common_user_view'
