# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2021 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Tailbone Web API - Master View (v2)
"""

from __future__ import unicode_literals, absolute_import

from pyramid.response import FileResponse
from cornice import resource, Service

from tailbone.api import APIMasterView


class APIMasterView2(APIMasterView):
    """
    Base class for data model REST API views.
    """
    listable = True
    creatable = True
    viewable = True
    editable = True
    deletable = True
    supports_autocomplete = False
    supports_download = False
    supports_rawbytes = False

    @classmethod
    def establish_method(cls, method_name):
        """
        Establish the given HTTP method for this Cornice Resource.

        Cornice will auto-register any class methods for a resource, if they
        are named according to what it expects (i.e. 'get', 'collection_get'
        etc.).  Tailbone API tries to make things automagical for the sake of
        e.g. Poser logic, but in this case if we predefine all of these methods
        and then some subclass view wants to *not* allow one, it's not clear
        how to "undefine" it per se.  Or at least, the more straightforward
        thing (I think) is to not define such a method in the first place, if
        it was not wanted.

        Enter ``establish_method()``, which is what finally "defines" each
        resource method according to what the subclass has declared via its
        various attributes (:attr:`creatable`, :attr:`deletable` etc.).

        Note that you will not likely have any need to use this
        ``establish_method()`` yourself!  But we describe its purpose here, for
        clarity.
        """
        def method(self):
            internal_method = getattr(self, '_{}'.format(method_name))
            return internal_method()

        setattr(cls, method_name, method)

    def _delete(self):
        """
        View to handle DELETE action for an existing record/object.
        """
        obj = self.get_object()
        self.delete_object(obj)

    def delete_object(self, obj):
        """
        Delete the object, or mark it as deleted, or whatever you need to do.
        """
        # flush immediately to force any pending integrity errors etc.
        self.Session.delete(obj)
        self.Session.flush()

    ##############################
    # download
    ##############################

    def download(self):
        """
        GET view allowing for download of a single file, which is attached to a
        given record.
        """
        obj = self.get_object()

        filename = self.request.GET.get('filename', None)
        if not filename:
            raise self.notfound()
        path = self.download_path(obj, filename)

        response = self.file_response(path)
        return response

    def download_path(self, obj, filename):
        """
        Should return absolute path on disk, for the given object and filename.
        Result will be used to return a file response to client.
        """
        raise NotImplementedError

    def rawbytes(self):
        """
        GET view allowing for direct access to the raw bytes of a file, which
        is attached to a given record.  Basically the same as 'download' except
        this does not come as an attachment.
        """
        obj = self.get_object()

        filename = self.request.GET.get('filename', None)
        if not filename:
            raise self.notfound()
        path = self.download_path(obj, filename)

        response = self.file_response(path, attachment=False)
        return response

    @classmethod
    def defaults(cls, config):
        cls._defaults(config)

    @classmethod
    def _defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        permission_prefix = cls.get_permission_prefix()
        collection_url_prefix = cls.get_collection_url_prefix()
        object_url_prefix = cls.get_object_url_prefix()

        # first, the primary resource API

        # list/search
        if cls.listable:
            cls.establish_method('collection_get')
            resource.add_view(cls.collection_get, permission='{}.list'.format(permission_prefix))

        # create
        if cls.creatable:
            cls.establish_method('collection_post')
            if hasattr(cls, 'permission_to_create'):
                permission = cls.permission_to_create
            else:
                permission = '{}.create'.format(permission_prefix)
            resource.add_view(cls.collection_post, permission=permission)

        # view
        if cls.viewable:
            cls.establish_method('get')
            resource.add_view(cls.get, permission='{}.view'.format(permission_prefix))

        # edit
        if cls.editable:
            cls.establish_method('post')
            resource.add_view(cls.post, permission='{}.edit'.format(permission_prefix))

        # delete
        if cls.deletable:
            cls.establish_method('delete')
            resource.add_view(cls.delete, permission='{}.delete'.format(permission_prefix))

        # register primary resource API via cornice
        object_resource = resource.add_resource(
            cls,
            collection_path=collection_url_prefix,
            # TODO: probably should allow for other (composite?) key fields
            path='{}/{{uuid}}'.format(object_url_prefix))
        config.add_cornice_resource(object_resource)

        # now for some more "custom" things, which are still somewhat generic

        # autocomplete
        if cls.supports_autocomplete:
            autocomplete = Service(name='{}.autocomplete'.format(route_prefix),
                                   path='{}/autocomplete'.format(collection_url_prefix))
            autocomplete.add_view('GET', 'autocomplete', klass=cls,
                                  permission='{}.list'.format(permission_prefix))
            config.add_cornice_service(autocomplete)

        # download
        if cls.supports_download:
            download = Service(name='{}.download'.format(route_prefix),
                               # TODO: probably should allow for other (composite?) key fields
                               path='{}/{{uuid}}/download'.format(object_url_prefix))
            download.add_view('GET', 'download', klass=cls,
                              permission='{}.download'.format(permission_prefix))
            config.add_cornice_service(download)

        # rawbytes
        if cls.supports_rawbytes:
            rawbytes = Service(name='{}.rawbytes'.format(route_prefix),
                               # TODO: probably should allow for other (composite?) key fields
                               path='{}/{{uuid}}/rawbytes'.format(object_url_prefix))
            rawbytes.add_view('GET', 'rawbytes', klass=cls,
                              permission='{}.download'.format(permission_prefix))
            config.add_cornice_service(rawbytes)
