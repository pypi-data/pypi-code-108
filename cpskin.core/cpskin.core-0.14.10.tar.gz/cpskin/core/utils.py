# -*- coding: utf-8 -*-
from Acquisition import aq_base
from collective.contact.core.browser.address import get_address
from collective.geo.behaviour.interfaces import ICoordinates
from collective.geo.mapwidget.interfaces import IGeoCoder
from geopy import geocoders
from geopy.exc import GeocoderQueryError
from plone import api
from plone.app.imagecropping import PAI_STORAGE_KEY
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled
from plone.dexterity.interfaces import IDexterityFTI
from plone.namedfile.file import NamedBlobImage
from Products.CMFCore.interfaces import ISiteRoot
from zope.annotation.interfaces import IAnnotations
from zope.component import queryUtility
from zope.interface import implements

import logging
import os
import phonenumbers


logger = logging.getLogger('cpskin.core.utils')


def safe_utf8(s):
    """Transform unicode to utf8"""
    if isinstance(s, unicode):
        s = s.encode('utf8')
    return s


def safe_unicode(s):
    """Decode from utf8"""
    if isinstance(s, str):
        s = s.decode('utf8')
    return s


def publish_content(content):
    """Publish an object and hide it for cpskin."""
    wftool = api.portal.get_tool('portal_workflow')
    if wftool.getInfoFor(content, 'review_state') != 'published':
        actions = [a.get('id') for a in wftool.listActions(object=content)]
        if api.content.get_state(obj=content) != 'published_and_hidden':
            # we need to handle both workflows
            if 'publish_and_hide' in actions:
                wftool.doActionFor(content, 'publish_and_hide')
            elif 'publish' in actions:
                wftool.doActionFor(content, 'publish')


def set_exclude_from_nav(obj):
    # dexterity with exludefromnav behavior
    obj.exclude_from_nav = True


def add_keyword(obj, tag_id='hiddenTags', tag_value=[]):
    """Add a keyword to a object."""
    old_value = getattr(obj, tag_id)
    if not old_value:
        values = tag_value
    else:
        values = old_value + tag_value
    setattr(obj, tag_id, values)
    obj.reindexObject()


def has_behavior(type_name, behavior_name):
    """Check if a behavior is on portal_type"""
    fti = queryUtility(IDexterityFTI, name=type_name)
    if not fti:
        return
    behaviors = list(fti.behaviors)
    if behavior_name not in behaviors:
        return False
    else:
        return True


def add_behavior(type_name, behavior_name):
    """Add a behavior to a type"""
    fti = queryUtility(IDexterityFTI, name=type_name)
    if not fti:
        return
    behaviors = list(fti.behaviors)
    if behavior_name not in behaviors:
        behaviors.append(behavior_name)
        fti._updateProperty('behaviors', tuple(behaviors))


def remove_behavior(type_name, behavior_name):
    """Add a behavior to a type"""
    fti = queryUtility(IDexterityFTI, name=type_name)
    if not fti:
        return
    behaviors = list(fti.behaviors)
    if behavior_name in behaviors:
        behaviors.remove(behavior_name)
        fti._updateProperty('behaviors', tuple(behaviors))


def add_leadimage_from_file(container, file_name,
                            folder_name='data', image_field='image'):
    """Add leadimage from a file from a folder"""
    if not container:
        container = api.portal.get()
    data_path = os.path.join(os.path.dirname(__file__), folder_name)
    file_path = os.path.join(data_path, file_name)
    if not getattr(aq_base(container), file_name, False):
        namedblobimage = NamedBlobImage(
            data=open(file_path, 'r').read(),
            filename=unicode(file_name)
        )
        image_container = container
        if not INavigationRoot.providedBy(container) and \
                not ISiteRoot.providedBy(container):
            image_container = container.aq_parent

        image = api.content.create(type='Image',
                                   title=file_name,
                                   image=namedblobimage,
                                   container=image_container)
        image.setTitle(file_name)
        image.reindexObject()
        setattr(container, image_field, namedblobimage)


def has_crop(obj, fieldname, scale):
    crops = IAnnotations(obj).get(PAI_STORAGE_KEY)
    if not crops:
        return False
    return '{0:s}_{1:s}'.format(fieldname, scale) in crops


def image_scale(obj, css_class, default_scale, generate_tag=True, with_uid=True):
    images = obj.restrictedTraverse('@@images')
    if obj.portal_type in ['organization', 'person']:
        if getattr(images, 'logo', False):
            image_field_id = 'logo'
            image = images.scale(image_field_id, scale=default_scale)
        else:
            image = None
    else:
        image_field_id = 'image'
        image = images.scale(image_field_id, scale=default_scale)
    if not image:
        return False
    if not generate_tag:
        return image
    if not with_uid:
        image_path = '{0}/@@images/{1}/{2}'.format(
            obj.absolute_url(),
            image_field_id,
            default_scale)
        image.url = image_path
        return image
    return image.tag(css_class=css_class) if image.tag() else ''


# --------------- Address ---------------

def get_lat_lng_from_address(address):
    """Return tuple with status and geocoder object
       0: error, 1: success, 2: not found, 3: unexpected error
    """
    geocoder = geocoders.Nominatim(
        user_agent='{0}-cpskinapp'.format(api.portal.get().id),
        timeout=10,
    )
    geocode = geocoder.geocode(safe_utf8(address))
    return (1, geocode)


def get_address_from_obj(obj):
    # Event
    loc = getattr(obj, 'location', '')
    if loc:
        return obj.location
    # old card
    if obj.portal_type == 'collective.directory.card':
        street = get_field(obj, 'address')
        zip_code = get_field(obj, 'zip_code')
        city = get_field(obj, 'city')
        address = '{0} {1} {2}'.format(
            street, zip_code, city
        )
        return address

    # collective.contact.core
    dict_address = get_address(obj)
    street = safe_utf8(dict_address.get('street'))
    number = safe_utf8(dict_address.get('number'))
    zip_code = safe_utf8(dict_address.get('zip_code'))
    city = safe_utf8(dict_address.get('city'))
    if street and city:
        address = '{0} {1} {2} {3}'.format(
            number, street, zip_code, city
        )
    else:
        return ''
    return address


def get_field(obj, field_name):
    value = getattr(obj, field_name, '')
    if isinstance(value, int):
        return str(value).encode('utf8')
    if value:
        return value.encode('utf8')
    return ''


def has_lat_lng(obj):
    try:
        if ICoordinates(obj).coordinates:
            return True
    except:  # noqa
        return False
    return False


def set_coord(obj, request):
    if not has_behavior(obj.portal_type, ICoordinates.__identifier__):
        return
    address = get_address_from_obj(obj)
    if address:
        status, geocode = get_lat_lng_from_address(address)
        if status in [0, 2, 3]:
            # 0: stop if limit is 'OVER_QUERY_LIMIT'
            # 2: not found
            # 3: unexpected error
            api.portal.show_message(message=geocode, request=request)
            logger.info(geocode)
        else:
            if geocode and geocode.longitude and geocode.latitude:
                coord = u'POINT({0} {1})'.format(
                    geocode.longitude, geocode.latitude)
                ICoordinates(obj).coordinates = coord
                obj.reindexObject(
                    idxs=['zgeo_geometry', 'collective_geo_styles'])
                path = '/'.join(obj.getPhysicalPath())
                message = 'lat lng of {0} updated'.format(path)
                logger.info(message)
                return message
    else:
        message = 'No address for {0}'.format(
            obj.absolute_url(),
        )
        api.portal.show_message(message=message, request=request)
        logger.info(message)


def format_phone(value):
    try:
        number = phonenumbers.parse(value, 'BE')
    except phonenumbers.NumberParseException:
        return {'raw': value, 'formated': value}
    formated_value = phonenumbers.format_number(
        number,
        phonenumbers.PhoneNumberFormat.INTERNATIONAL,
    )
    country_code = str(number.country_code)
    country_code_with_plus = '+{0}'.format(country_code)
    return {
        'raw': formated_value,
        'formated': formated_value.replace(
            country_code_with_plus,
            '{0} (0)'.format(country_code_with_plus),
        ),
    }


def set_plonecustom_last():
    portal_css = api.portal.get_tool('portal_css')
    resources = list(portal_css.resources)
    custom_id = 'ploneCustom.css'
    if custom_id in [res.getId() for res in resources]:
        portal_css.moveResource(custom_id, len(resources))


def is_plone_app_multilingual_installed(request):
    return IPloneAppMultilingualInstalled.providedBy(request)


def get_geocoder():
    return GeoCoderUtility()


class GeoCoderUtility(object):
    """Override collective.geo.mapwidget to use Nominatim instead of google
    """
    implements(IGeoCoder)

    def retrieve(self, address=None, google_api=None, language=None):
        self.geocoder = geocoders.Nominatim(user_agent='cpskinapp')

        if not address:
            raise GeocoderQueryError
        return self.geocoder.geocode(address, exactly_one=False,
                                     language=language)
