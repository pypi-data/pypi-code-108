# -*- coding: utf-8 -*-

from collective.documentviewer.settings import GlobalSettings
from collective.iconifiedcategory.utils import get_categorized_elements
from plone import api
from zope.annotation import IAnnotations


def get_annexes_to_print(container, portal_type=None, caching=True):
    ''' '''
    res = None
    if caching:
        key = "utils-get_annexes_to_print-%s-%s" % (container.UID(), portal_type)
        cache = IAnnotations(container.REQUEST)
        res = cache.get(key, None)

    if res is None:
        res = []
        portal = api.portal.get()
        global_settings = GlobalSettings(portal)
        annexes = get_categorized_elements(container,
                                           result_type='dict',
                                           portal_type=portal_type,
                                           filters={"to_print": True})
        i = 1
        for annex_infos in annexes:
            # first check if annex needs to be printed
            if not annex_infos['to_print']:
                continue
            # must have been converted successfully
            if not annex_infos['preview_status'] == 'converted':
                continue

            # every annex seems right, manage this annex build path to images
            # use unrestrictedTraverse to avoid failing if a folder is private
            # like it is the case for 'Members'
            annexObj = portal.unrestrictedTraverse(annex_infos['relative_url'])
            annex_annotations = IAnnotations(annexObj)
            data = {}
            data['title'] = annexObj.Title()
            annexUID = annexObj.UID()
            data['UID'] = annexObj.UID()
            data['number'] = i
            data['images'] = []
            data['number_of_images'] = annex_annotations['collective.documentviewer']['num_pages']
            image_format = annex_annotations['collective.documentviewer']['pdf_image_format']
            # we need to traverse to something like :
            # @@dvpdffiles/c/7/c7e2e8b5597c4dc28cf2dee9447dcf9a/large/dump_1.png
            dvpdffiles = portal.unrestrictedTraverse('@@dvpdffiles')
            filetraverser = dvpdffiles.publishTraverse(container.REQUEST, annexUID[0])
            filetraverser = dvpdffiles.publishTraverse(container.REQUEST, annexUID[1])
            filetraverser = dvpdffiles.publishTraverse(container.REQUEST, annexUID)
            large = filetraverser.publishTraverse(container.REQUEST, 'large')
            for image_number in range(data['number_of_images']):
                realImageNumber = image_number + 1
                large_image_dump = large.publishTraverse(
                    container.REQUEST, 'dump_%d.%s' % (realImageNumber, image_format))
                # depending on the fact that we are using 'Blob' or 'File' as storage_type,
                # the 'large' object is different.  Either a Blob ('Blob') or a DirectoryResource ('File')
                if global_settings.storage_type == 'Blob':
                    blob = large_image_dump.settings.blob_files[large_image_dump.filepath]
                    # if we do not check 'readers', the blob._p_blob_committed is sometimes None...
                    blob.readers
                    path = blob._p_blob_committed
                else:
                    path = large_image_dump.context.path
                data['images'].append({'number': realImageNumber,
                                       'path': path,
                                       })
            res.append(data)
            i = i + 1
        if caching:
            cache[key] = res
    return res
