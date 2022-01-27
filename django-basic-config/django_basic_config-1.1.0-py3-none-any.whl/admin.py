from __future__ import unicode_literals

'''
Copyright 2013 Jonathan Morgan

This file is part of https://github.com/jonathanmorgan/django_config.

django_config is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

django_config is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with https://github.com/jonathanmorgan/django_config. If not, see http://www.gnu.org/licenses/.
'''

# import django_config class.
from django_config.models import Config_Property

# import django admin stuff
from django.contrib import admin

# import django db models.
from django import forms
from django.db import models

# start with default admin screens - comment out as we make fancier additions
#    below.
# admin.site.register( Config_Property )

# get fancier

#===============================================================================
# Javascript includes.
#===============================================================================

#default_js = ( '/js/ckeditor/ckeditor.js', '/js/ckeditor/adapters/jquery.js', '/js/ckeditor_config.js' )
default_js = ( '/js/ckeditor_config.js', )

#===============================================================================
# Admin classes
#===============================================================================


#-------------------------------------------------------------------------------
# Issue admin definition
#-------------------------------------------------------------------------------

class Config_PropertyAdmin( admin.ModelAdmin ):

    fieldsets = [
        ( None,
            {
                'fields' : [ 'application', 'property_group', 'property_name', 'property_type', 'property_value', ]
            }
        ),
    ]

    list_display = ( 'id', 'application', 'property_group', 'property_name', 'property_type', 'property_value', )
    list_display_links = ( 'id', 'property_name', )
    list_filter = [ 'application', 'property_group', 'property_type' ]
    search_fields = [ 'application', 'property_group', 'property_name', 'property_value', 'property_type' ]
    # date_hierarchy = 'status_date'
    # actions = [ toggle_published_flag ]
    ordering = [ '-last_update' ]

    # formfield_overrides = { models.TextField: { 'widget' : forms.Textarea( attrs = { 'class' : 'vLargeTextField' } ) }, }

#-- END IssueAdmin admin class --#

admin.site.register( Config_Property, Config_PropertyAdmin )
