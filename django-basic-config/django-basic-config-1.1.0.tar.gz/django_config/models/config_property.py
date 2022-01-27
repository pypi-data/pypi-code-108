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

# django_config imports
from django_config.models import Abstract_Config_Property

class Config_Property( Abstract_Config_Property ):

    #---------------------------------------------------------------------------
    # django model fields
    #---------------------------------------------------------------------------

    #application = models.CharField( max_length = 255 )
    #property_group = models.CharField( max_length = 255, blank = True, null = True )
    #property_name = models.CharField( max_length = 255 )
    #property_value = models.TextField( blank = True, null = True )
    #property_type = models.CharField( max_length = 255, blank = True, null = True, choices = TYPE_CHOICES, default = TYPE_DEFAULT )
    #create_date = models.DateTimeField( auto_now_add = True )
    #last_update = models.DateTimeField( auto_now = True )


    #----------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------


    def __init__( self, *args, **kwargs ):

        # call parent __init()__ first.
        super().__init__( *args, **kwargs )

    #-- END method __init__() --#


#= END Config_Property Model =========================================#
