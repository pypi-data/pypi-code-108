from .utils import SettingsReader
import logging
l = logging.getLogger(__name__)



class AppSettings(SettingsReader):
    myconf = ['adminname','adminpass','customtemplatesrc']
    customtemplatesrc = '/tmp'


__allsettings={}

def initAppSettings(prefix,classname):
  newclass = type(classname  , (SettingsReader,),{})
  __allsettings [classname  ] = newclass 
