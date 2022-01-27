from __future__ import unicode_literals

'''
Copyright 2013-present (2016) Jonathan Morgan

This file is part of https://github.com/jonathanmorgan/django_config.

django_config is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

django_config is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with https://github.com/jonathanmorgan/django_config. If not, see http://www.gnu.org/licenses/.
'''

import six

from django.db import models
import django.utils.encoding

# python_utilities
from python_utilities.lists.list_helper import ListHelper

class Config_Property( models.Model ):

    '''
    Config_Properties creates a table for configuration settings where each row
    has the following fields:
    - application
    - property_name
    - property_value
    - property_type
    
    It also provides methods for interacting with configuration properties, such
       that you can set a default as part of the call, and so deal with the
       property not yet having been set. 
    '''

    #---------------------------------------------------------------------------
    # Constants-ish
    #---------------------------------------------------------------------------

    APPLICATION_CORE = "core" # Application you can use for site-wide settings.
    APPLICATION_DEFAULT = APPLICATION_CORE
    
    # property types
    TYPE_NONE = None
    TYPE_STRING = "string"
    TYPE_INT = "int"
    TYPE_DECIMAL = "decimal"
    TYPE_BOOLEAN = "boolean"
    TYPE_DEFAULT = TYPE_NONE
    
    TYPE_CHOICES = (
        ( TYPE_NONE, 'None' ),
        ( TYPE_STRING, 'String' ),
        ( TYPE_INT, 'Integer' ),
        ( TYPE_DECIMAL, 'Decimal' ),
        ( TYPE_BOOLEAN, 'Boolean' )
    )

    #---------------------------------------------------------------------------
    # django model fields
    #---------------------------------------------------------------------------

    application = models.CharField( max_length = 255 )
    property_name = models.CharField( max_length = 255 )
    property_value = models.TextField( blank = True, null = True )
    property_type = models.CharField( max_length = 255, blank = True, null = True, choices = TYPE_CHOICES, default = TYPE_DEFAULT )
    create_date = models.DateTimeField( auto_now_add = True )
    last_update = models.DateTimeField( auto_now = True )


    #----------------------------------------------------------------------
    # class methods
    #----------------------------------------------------------------------


    @classmethod
    def get_property_boolean_value( cls, application_IN, property_name_IN, default_IN = False, *args, **kwargs ):
        
        # return reference
        value_OUT = None
        
        # declare variables
        prop_value = None
        
        # get property
        prop_value = cls.get_property_value( application_IN, property_name_IN, default_IN )

        # convert to boolean if not None.
        if ( ( prop_value ) and ( prop_value != None ) ):
            
            # Not none - see if it is a known value for True.
            if ( ( prop_value == True )
                or ( ( isinstance( prop_value, six.integer_types ) == True ) and ( prop_value == 1 ) )
                or ( ( isinstance( prop_value, six.string_types ) == True ) and ( prop_value.lower() == "true" ) ) ):
            
                # true.
                value_OUT = True
                
            else:
            
                # false.  Or unknown. Which is false.
                value_OUT = False

            #-- END check to see if true or false. --#
            
        else:
            
            # None - convert default to int.
            value_OUT = default_IN
            
        #-- END check to make sure we don't try to convert None to int. --#       
        
        return value_OUT
        
    #-- END method get_property_boolean_value() --#


    @classmethod
    def get_property_int_value( cls, application_IN, property_name_IN, default_IN = 0, *args, **kwargs ):
        
        # return reference
        value_OUT = None
        
        # declare variables
        prop_value = None
        
        # get property
        prop_value = cls.get_property_value( application_IN, property_name_IN, default_IN )

        # convert to int if not None.
        if ( ( prop_value ) and ( prop_value != None ) ):
            
            # Not none - convert to int.
            value_OUT = int( prop_value )
            
        else:
            
            # None - convert default to int.
            value_OUT = int( default_IN )
            
        #-- END check to make sure we don't try to convert None to int. --#       
        
        return value_OUT
        
    #-- END method get_property_int_value() --#


    @classmethod
    def get_property_list_value( cls, application_IN, property_name_IN, default_IN = None, delimiter_IN = ",", *args, **kwargs ):
        
        # return reference
        value_OUT = None
        
        # declare variables
        prop_value = None
        
        # get property
        prop_value = cls.get_property_value( application_IN, property_name_IN, default_IN )

        # convert to int if not None.
        if ( prop_value != None ):
            
            # Not none - convert to int.
            value_OUT = ListHelper.get_value_as_list( prop_value, delimiter_IN )
            
        else:
            
            # None - empty list.
            value_OUT = []
            
        #-- END check to make sure we don't try to convert None to list. --#       
        
        return value_OUT
        
    #-- END method get_property_list_value() --#


    @classmethod
    def get_property_value( cls, application_IN, property_name_IN, default_IN = None, *args, **kwargs ):
        
        # return reference
        value_OUT = None
        
        # declare variables
        prop_qs = None
        prop_value = None
        
        # make sure we have an application
        if ( ( application_IN ) and ( application_IN != "" ) ):

            # make sure we have a property name
            if ( ( property_name_IN ) and ( property_name_IN != "" ) ):
                
                # got one.  look for associated attributes with that name.
                
                # get QuerySet of attributes for this Object.
                prop_qs = cls.objects.all()
                
                # filter based on application and property name passed in.
                prop_qs = prop_qs.filter( application = application_IN )
                prop_qs = prop_qs.filter( property_name = property_name_IN )
                
                # anything in it?
                if ( ( prop_qs is not None ) and ( prop_qs.count() > 0 ) ):
                    
                    # got at least one attribute.  For now, grab first one.
                    prop_value = prop_qs[ 0 ]
                    
                    # return value in that instance
                    value_OUT = prop_value.property_value
                    
                else:
                    
                    # no attribute for that name.  If default, return it.
                    if ( default_IN != None ):
                        
                        value_OUT = default_IN
                        
                    #-- END check to see if default --#
                    
                #-- END check to see if any matching attributes. --#
            
            else:
                
                # no name - return None.
                value_OUT = None
                
            #-- END check to see if name. --#

        else:
            
            # no application - return None.
            value_OUT = None
            
        #-- END check to see if application. --#
        
        return value_OUT
        
    #-- END method get_property_value() --#


    @classmethod
    def set_property_value( cls, application_IN, property_name_IN, value_IN, *args, **kwargs ):
        
        # return reference
        success_OUT = False
        
        # declare variables
        prop_qs = None
        prop_value = None
        
        # make sure we have an application
        if ( ( application_IN ) and ( application_IN != "" ) ):

            # make sure we have a property name
            if ( ( property_name_IN ) and ( property_name_IN != "" ) ):
                
                # got one.  look for associated attributes with that name.
                
                # get QuerySet of properties.
                prop_qs = cls.objects.all()
                
                # filter based on application and name passed in.
                prop_qs = prop_qs.filter( application = application_IN )
                prop_qs = prop_qs.filter( property_name = property_name_IN )
                
                # anything in it?
                if ( ( prop_qs is not None ) and ( prop_qs.count() > 0 ) ):
                    
                    # got at least one property.  For now, grab first one.
                    prop_value = prop_qs[ 0 ]
                    
                else:
                    
                    # no property for that application/name.  Make a new one.
                    prop_value = cls()
                    
                    # set values
                    prop_value.application = application_IN
                    prop_value.property_name = property_name_IN
                    
                #-- END check to see if any matching properties. --#
                
                # property retrieved/made.  Set value and save.
                prop_value.property_value = value_IN
                prop_value.save()
                success_OUT = True
            
            else:
                
                # no name - not success.
                success_OUT = False
                
            #-- END check to see if name. --#
        
        else:
            
            # no application - not success.
            success_OUT = False
            
        #-- END check to see if we have an application --#
        
        return success_OUT
        
    #-- END method set_property_value() --#

    
    #----------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------


    def __str__( self ):
        
        # return reference
        string_OUT = ''
        prefix = ""
        
        if ( self.id is not None ):
        
            string_OUT = str( self.id )
            prefix = " - "
            
        #-- END check for ID --#
        
        if ( self.application ):

            string_OUT += prefix + "application: " + self.application
            prefix = "; "
            
        #-- END check for application --#
            
        if ( self.property_name ):

            string_OUT += prefix + "prop name: " + self.property_name
            prefix = "; "
            
        #-- END check for property_name field --#

        if ( self.property_value ):

            string_OUT += prefix + "prop value: " + self.property_value
            prefix = "; "
            
        #-- END check for property_value field --#

        return string_OUT
        
    #-- END __str__() method --#
        

#= END Config_Property Model ==============================================