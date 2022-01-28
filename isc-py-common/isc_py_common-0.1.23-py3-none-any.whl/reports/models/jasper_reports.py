import logging

from django.db.models import CheckConstraint , F , Q
from django.db.models import PositiveIntegerField
from django.forms import model_to_dict
from isc_common.fields.code_field import CodeStrictField
from isc_common.http.DSRequest import DSRequest
from isc_common.models.base_ref import BaseRefHierarcy , BaseRefManager , BaseRefQuerySet
from django.db.models import CheckConstraint , F , Q

logger = logging.getLogger( __name__ )


class Jasper_reportsQuerySet( BaseRefQuerySet ) :
    pass


def get_reports( request ) :
    from reports.models.jasper_reports_users import Jasper_reports_users

    request = DSRequest( request=request )
    jasper_reports = [ dict(
        report=model_to_dict( item.report ) ,
        editor_identifier=item.editor_identifier ,
    ) for item in Jasper_reports_users.objects.filter( user=request.user ) ]
    return jasper_reports


class Jasper_reportsManager( BaseRefManager ) :

    @classmethod
    def getRecord( cls , record ) :
        res = {
            'id' : record.id ,
            'code' : record.code ,
            'name' : record.name ,
            'path' : record.path ,
            'description' : record.description ,
            'username' : record.username ,
            'password' : record.password ,
            'report_id' : record.report_id ,
            'host' : record.host ,
            'port' : record.port ,
            'parent' : record.parent.id if record.parent else None
        }
        return res

    def get_queryset( self ) :
        return Jasper_reportsQuerySet( self.model , using=self._db )


class Jasper_reports( BaseRefHierarcy ) :
    path = CodeStrictField( default='/jasperserver/rest_v2/reports/' )
    report_id = CodeStrictField( null=True , blank=False )
    username = CodeStrictField( default='printer' )
    password = CodeStrictField( default='printer' )
    host = CodeStrictField()
    port = PositiveIntegerField()

    objects = Jasper_reportsManager()

    def __str__( self ) :
        return f"ID:{self.id}, code: {self.code}, name: {self.name}, path: {self.path}, description: {self.description}"

    class Meta :
        verbose_name = 'Отчеты'
        constraints = [
            CheckConstraint( check=~Q( id=F( 'parent_id' ) ) , name=f'c_Jasper_reports' ) ,
        ]
