# -*- coding: utf-8 -*-
# from cpskin.core.utils import get_address_from_obj
from cpskin.citizen.utils import execute_under_unrestricted_user
from cpskin.core.utils import has_lat_lng
from cpskin.core.utils import set_coord
from plone import api
from plone.app.imagecropping import PAI_STORAGE_KEY
from plone.app.imagecropping.interfaces import IImageCroppingUtils
from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest
import logging
import transaction

logger = logging.getLogger('cpskin.core')


def set_lat_lng(obj, event):
    """Set lat and lng when a organization is created"""
    if has_lat_lng(obj):
        return
    request = obj.REQUEST
    set_coord(obj, request)


def apply_crops_after_modify(obj, event):
    """
    Bug fixed here : cropped images scales on a content are lost after a
                     modification of this content (#14901).
    This is already fixed in Plone 5 but not in Plone 4 :
        https://github.com/collective/plone.app.imagecropping/issues/21
    To fix this, we need to re-generate all the crops of an object just after
    it's modification.

    We also need to handle fieldnames conflicting with :
      other field name + _ + scale name
      (ex : 'image_banner' field and 'image' field with 'banner' scale)
    """
    crops = IAnnotations(obj).get(PAI_STORAGE_KEY)
    if not crops:
        return
    croputils = IImageCroppingUtils(obj)
    request = getRequest()
    cropper = getMultiAdapter((obj, request), name='crop-image')
    for fieldname in croputils.image_field_names():
        for crop_key in crops:
            if crop_key.startswith(fieldname) and len(crop_key) > len(fieldname):
                if crop_key[len(fieldname)] != "_":
                    continue
                scalename = crop_key[len(fieldname) + 1:]
                try:
                    cropper._crop(fieldname, scalename, crops[crop_key])
                except KeyError:
                    # Handles special cases with field / scales collisions
                    continue


def checkMinisites(event):
    minisite_root = event.minisite
    footer_doc = getattr(minisite_root, 'footer-mini-site', None)
    if footer_doc:
        logger.info('Found footer-mini-site doc for {0}'.format(
            minisite_root.absolute_url(),
        ))
        return
    footer_doc = execute_under_unrestricted_user(
        api.portal.get(),
        api.content.create,
        'admin',
        type='Document',
        id='footer-mini-site',
        title='Footer',
        container=minisite_root
    )
    logger.info('Created footer-mini-site doc for {0}'.format(
        minisite_root.absolute_url(),
    ))
    transaction.commit()
