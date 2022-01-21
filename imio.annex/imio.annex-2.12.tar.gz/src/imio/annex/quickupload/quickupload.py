# -*- coding: utf-8 -*-
"""
imio.annex
----------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from AccessControl import Unauthorized
from Acquisition import aq_inner
from collective.iconifiedcategory.utils import validateFileIsPDF
from collective.quickupload import logger
from collective.quickupload.browser.quick_upload import get_content_type
from collective.quickupload.browser.quick_upload import getDataFromAllRequests
from collective.quickupload.browser.quick_upload import QuickUploadFile
from collective.quickupload.browser.quick_upload import QuickUploadInit
from collective.quickupload.browser.quick_upload import QuickUploadView
from collective.quickupload.browser.uploadcapable import get_id_from_filename
from collective.quickupload.browser.uploadcapable import INameChooser
from collective.quickupload.browser.uploadcapable import MissingExtension
from collective.quickupload.browser.uploadcapable import QuickUploadCapableFileFactory
from collective.quickupload.browser.uploadcapable import upload_lock
from collective.quickupload.interfaces import IQuickUploadFileFactory
from collective.quickupload.interfaces import IQuickUploadFileSetter
from collective.quickupload.interfaces import IQuickUploadFileUpdater
from imio.annex.content.annex import IAnnex
from imio.annex.quickupload import utils
from plone.i18n.normalizer.interfaces import IUserPreferredFileNameNormalizer
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import base_hasattr
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ZODB.POSException import ConflictError
from z3c.form.validator import Data
from zope.event import notify
from zope.lifecycleevent import ObjectAddedEvent

import json
import pkg_resources
import urllib


try:
    pkg_resources.get_distribution('plone.uuid')
    from plone.uuid.interfaces import IUUID
    HAS_UUID = True
except pkg_resources.DistributionNotFound:
    HAS_UUID = False


class QuickUploadPortletView(QuickUploadView):
    template = ViewPageTemplateFile("templates/quick_upload.pt")

    @property
    def typeupload(self):
        context = aq_inner(self.context)
        config = context.restrictedTraverse('@@quick_upload_init')
        config.uploader_id = self.uploader_id
        return config.upload_settings().get('typeupload')

    @property
    def is_iconified_categorized(self):
        return utils.is_iconified_categorized(self.typeupload)

    def script_content(self):
        result = super(QuickUploadPortletView, self).script_content()
        return u"""
{0}
jQuery('a#copy_categories').click(PloneQuickUpload.extendCategories);
        """.format(result)


class QuickUploadFileInit(QuickUploadInit):

    def upload_settings(self):
        # if not in @@finder_upload (adding an image in CKeditor for example)
        # make sure we do not have a mediaupload in the SESSION or it is used
        # to determinate media format (image) and it keeps media if adding an image
        # using CKeditor then adding an annex
        if self.request.get('PUBLISHED').__name__ == 'quick_upload':
            session = self.request.get('SESSION', '')
            for session_key in ('mediaupload', 'typeupload'):
                if session_key in session.keys():
                    del session[session_key]
        return super(QuickUploadFileInit, self).upload_settings()


class QuickUploadFileView(QuickUploadFile):

    def _manage_extra_parameters(self, request, f):
        """Manage extra parameters, particularly content_category."""
        # Extra parameters
        content_category = getDataFromAllRequests(request, 'content_category') or ''
        # Add an extra parameter
        if f['success'] and content_category:
            obj = f['success']
            obj.content_category = content_category
            if IAnnex.providedBy(obj) and obj.file.contentType != 'application/pdf':
                data = Data([], [], [])
                data.__context__ = obj
                data.content_category = content_category
                validateFileIsPDF(data)
            # elements using content_category are initialized in the object created event
            notify(ObjectAddedEvent(obj))

    def quick_upload_file(self):
        """Copied from collective.quickupload"""
        context = aq_inner(self.context)
        request = self.request
        response = request.RESPONSE

        response.setHeader('Expires', 'Sat, 1 Jan 2000 00:00:00 GMT')
        response.setHeader('Cache-control', 'no-cache')
        # application/json is not supported by old IEs but text/html fails in
        # every browser with plone.protect 3.0.11
        response.setHeader('Content-Type', 'application/json; charset=utf-8')
        # disable diazo themes and csrf protection
        request.response.setHeader('X-Theme-Disabled', 'True')

        if request.HTTP_X_REQUESTED_WITH:
            # using ajax upload
            file_name = urllib.unquote(request.HTTP_X_FILE_NAME)
            upload_with = "XHR"
            try:
                file = request.BODYFILE
                file_data = file.read()
                file.seek(0)
            except AttributeError:
                # in case of cancel during xhr upload
                logger.error("Upload of %s has been aborted", file_name)
                # not really useful here since the upload block
                # is removed by "cancel" action, but
                # could be useful if someone change the js behavior
                return json.dumps({u'error': u'emptyError'})
            except:
                logger.error(
                    "Error when trying to read the file %s in request",
                    file_name
                )
                return json.dumps({u'error': u'serverError'})
        else:
            # using classic form post method (MSIE<=8)
            file = request.get("qqfile", None)
            file_data = file.read()
            file.seek(0)
            filename = getattr(file, 'filename', '')
            file_name = filename.split("\\")[-1]
            try:
                file_name = file_name.decode('utf-8')
            except UnicodeDecodeError:
                pass

            file_name = IUserPreferredFileNameNormalizer(
                self.request
            ).normalize(file_name)
            upload_with = "CLASSIC FORM POST"
            # we must test the file size in this case (no client test)
            if not self._check_file_size(file):
                logger.info("Test file size: the file %s is too big, upload "
                            "rejected" % filename)
                return json.dumps({u'error': u'sizeError'})

        # overwrite file
        try:
            newid = get_id_from_filename(
                file_name, context, unique=self.qup_prefs.object_unique_id)
        except MissingExtension:
            return json.dumps({u'error': u'missingExtension'})

        if (newid in context or file_name in context) and \
                not self.qup_prefs.object_unique_id:
            updated_object = context.get(newid, False) or context[file_name]
            mtool = getToolByName(context, 'portal_membership')
            override_setting = self.qup_prefs.object_override
            if override_setting and\
                    mtool.checkPermission(ModifyPortalContent, updated_object):
                can_overwrite = True
            else:
                can_overwrite = False

            if not can_overwrite:
                logger.debug(
                    "The file id for %s already exists, upload rejected"
                    % file_name
                )
                return json.dumps({u'error': u'serverErrorAlreadyExists'})

            overwritten_file = updated_object
        else:
            overwritten_file = None

        content_type = get_content_type(context, file_data, file_name)

        portal_type = getDataFromAllRequests(request, 'typeupload') or ''
        title = getDataFromAllRequests(request, 'title') or ''
        description = getDataFromAllRequests(request, 'description') or ''
        if not title.strip() and self.qup_prefs.id_as_title:
            title = newid

        if not portal_type:
            ctr = getToolByName(context, 'content_type_registry')
            portal_type = ctr.findTypeName(
                file_name.lower(), content_type, ''
            ) or 'File'

        if file_data:
            if overwritten_file is not None:
                updater = IQuickUploadFileUpdater(context)
                logger.info(
                    "reuploading %s file with %s: title=%s, description=%s, "
                    "content_type=%s"
                    % (overwritten_file.absolute_url(), upload_with, title,
                       description, content_type))
                try:
                    self.request.set('defer_categorized_content_created_event', True)
                    f = updater(overwritten_file, file_name, title,
                                description, content_type, file_data)
                    self.request.set('defer_categorized_content_created_event', False)
                    # manage extra parameters
                    self._manage_extra_parameters(request, f)
                except ConflictError:
                    # Allow Zope to retry up to three times, and if that still
                    # fails, handle ConflictErrors on client side if necessary
                    raise
                except Exception as e:
                    logger.error(
                        "Error updating %s file: %s", file_name, str(e)
                    )
                    return json.dumps({u'error': u'serverError'})

            else:
                factory = IQuickUploadFileFactory(context)
                logger.info(
                    "uploading file with %s: filename=%s, title=%s, "
                    "description=%s, content_type=%s, portal_type=%s"
                    % (upload_with, file_name, title,
                       description, content_type, portal_type))
                try:
                    self.request.set('defer_categorized_content_created_event', True)
                    f = factory(file_name, title, description, content_type,
                                file_data, portal_type)
                    self.request.set('defer_categorized_content_created_event', False)
                    # manage extra parameters
                    self._manage_extra_parameters(request, f)
                except ConflictError:
                    # Allow Zope to retry up to three times, and if that still
                    # fails, handle ConflictErrors on client side if necessary
                    raise
                except Exception as e:
                    logger.error(
                        "Error creating %s file: %s", file_name, str(e)
                    )
                    return json.dumps({u'error': u'serverError'})

            if f['success'] is not None:
                o = f['success']
                logger.info("file url: %s" % o.absolute_url())
                if HAS_UUID:
                    uid = IUUID(o)
                else:
                    uid = o.UID()

                msg = {
                    u'success': True,
                    u'uid': uid,
                    u'name': o.getId(),
                    u'title': o.pretty_title_or_id()
                }
            else:
                msg = {u'error': f['error']}
        else:
            msg = {u'error': u'emptyError'}

        return json.dumps(msg)


class ImioAnnexQuickUploadCapableFileFactory(QuickUploadCapableFileFactory):

    def __call__(self, filename, title, description, content_type, data,
                 portal_type):
        context = aq_inner(self.context)
        error = ''
        result = {}
        result['success'] = None
        newid = get_id_from_filename(filename, context)
        chooser = INameChooser(context)
        newid = chooser.chooseName(newid, context)
        # consolidation because it's different upon Plone versions
        if not title:
            # try to split filenames because we don't want
            # big titles without spaces
            title = filename.rsplit('.', 1)[0]\
                .replace('_', ' ')\
                .replace('-', ' ')

        if newid in context:
            # only here for flashupload method since a check_id is done
            # in standard uploader - see also XXX in quick_upload.py
            raise NameError('Object id %s already exists' % newid)
        else:
            upload_lock.acquire()
            try:
                # XXX begin change by imio.annex
                # this will lead to annex without a content_category because
                # this annex is created by a separated XHR request
                # transaction.begin()
                # XXX end change by imio.annex
                try:
                    context.invokeFactory(type_name=portal_type, id=newid,
                                          title=title, description=description)
                except Unauthorized:
                    error = u'serverErrorNoPermission'
                except ValueError:
                    error = u'serverErrorDisallowedType'
                except Exception as e:
                    error = u'serverError'
                    logger.exception(e)

                if error:
                    if error == u'serverError':
                        logger.info(
                            "An error happens with setId from filename, "
                            "the file has been created with a bad id, "
                            "can't find %s", newid)
                else:
                    obj = getattr(context, newid)
                    if obj:
                        error = IQuickUploadFileSetter(obj).set(
                            data, filename, content_type
                        )
                        # XXX begin change by imio.annex
                        if base_hasattr(obj, 'processForm'):
                            # Archetypes
                            obj._at_rename_after_creation = False
                            obj.processForm()
                            del obj._at_rename_after_creation
                        else:
                            # Dexterity
                            if obj.REQUEST.get('defer_update_categorized_elements', False):
                                notify(ObjectAddedEvent(obj))
                        # XXX end change by imio.annex

                # XXX begin change by imio.annex
                # TODO : rollback if there has been an error
                # transaction.commit()
                # XXX end change by imio.annex
            finally:
                upload_lock.release()

        result['error'] = error
        if not error:
            result['success'] = obj

        return result
