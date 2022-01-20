# -*- coding: utf-8 -*-
from collective.documentgenerator.browser.generation_view import DocumentGenerationView  # noqa
from collective.documentgenerator.helper.dexterity import DXDocumentGenerationHelperView  # noqa
from collective.taxonomy.interfaces import ITaxonomy
from cpskin.core.interfaces import IFolderViewSelectedContent as IFVSC
from cpskin.core.utils import format_phone
from cpskin.core.utils import safe_utf8
from cpskin.core.utils import safe_unicode
from cpskin.locales import CPSkinMessageFactory as _
from DateTime import DateTime
from eea.facetednavigation.interfaces import IFacetedNavigable
from imio.dashboard.utils import getDashboardQueryResult
from plone import api
from plone.app.event.base import date_speller
from plone.app.event.base import dates_for_display
from plone.app.event.base import expand_events
from plone.app.layout.viewlets.common import PathBarViewlet
from plone.app.workflow.remap import remap_workflow
from plone.dexterity.interfaces import IDexterityFTI
from plone.event.interfaces import IOccurrence
from plone.resource.interfaces import IResourceDirectory
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.MailHost.interfaces import IMailHost
from zope.component import getSiteManager
from zope.component import getUtility
from zope.component import queryUtility
from zope.component.interfaces import ComponentLookupError
from zope.publisher.browser import BrowserView
from zope.ramcache.interfaces.ram import IRAMCache

import base64
import json
import logging
import zope.copy


logger = logging.getLogger('cpskin.core.browser.pages')


class FrontPage(BrowserView):

    index = ViewPageTemplateFile('templates/frontpage.pt')


class HelpPage(BrowserView):

    index = ViewPageTemplateFile('templates/helppage.pt')


class OpenData(BrowserView):
    """Get data news, events rss feed and collective.directory csv files."""

    index = ViewPageTemplateFile('templates/opendata.pt')

    def get_links(self):
        portal = api.portal.get()
        links = []
        path = '/'.join(portal.getPhysicalPath())
        portal_catalog = api.portal.get_tool('portal_catalog')
        query_dict = {}
        query_dict['path'] = {'query': path, 'depth': 2}
        query_dict['portal_type'] = ['Folder']
        query_dict['object_provides'] = IFVSC.__identifier__
        query_dict['sort_on'] = 'getObjPositionInParent'
        brains = portal_catalog(query_dict)
        for brain in brains:
            folder = brain.getObject()
            if getattr(folder, 'default_page', None):
                default_page = folder.default_page
                default_obj = folder[default_page]
                rsslink = '{0}/atom.xml'.format(default_obj.absolute_url())
                links.append(rsslink)

        query_dict = {}
        query_dict['portal_type'] = ['collective.directory.directory']
        brains = portal_catalog(query_dict)
        for brain in brains:
            directory = brain.getObject()
            catalog = api.portal.get_tool('portal_catalog')
            query_dict = {}
            query_dict['portal_type'] = 'collective.directory.card'
            query_dict['path'] = {
                'query': '/'.join(directory.getPhysicalPath()), 'depth': 3}
            size = len(catalog(query_dict))
            if size > 3:
                csvlink = '{0}/collective_directory_export_view'.format(
                    directory.absolute_url()
                )
                links.append(csvlink)

        return links


class IDocumentGenerationView(DocumentGenerationView):
    """Override the 'get_generation_context' properly so
       'get_base_generation_context' is available for sub-packages
       that want to extend the template generation context."""

    def _get_generation_context(self, helper_view, pod_template):
        result = super(IDocumentGenerationView, self)._get_generation_context(
            helper_view, pod_template)
        # if pod_template.portal_type == 'ConfigurablePODTemplate':
        if IFacetedNavigable.providedBy(self.context):
            brains = getDashboardQueryResult(self.context)
            result['brains'] = brains
            if len(brains) > 0 and brains[0].portal_type == 'Event':
                expandevents = expand_events(brains, 2)
                events = []
                for event in expandevents:
                    if IOccurrence.providedBy(event):
                        start = event.start
                        end = event.end
                        parent = zope.copy.copy(event.aq_parent.aq_base)
                        parent.start = start
                        parent.end = end
                        req = event.REQUEST
                        parent.REQUEST = req
                        parent.occurrence = True
                        parent.base_event = event.aq_parent
                        events.append(parent)
                    else:
                        events.append(event)
                result['brains'] = events
            return result


class EventGenerationHelperView(DXDocumentGenerationHelperView):

    def __init__(self, context, request):
        super(EventGenerationHelperView, self).__init__(context, request)
        if getattr(self.real_context, 'occurrence', False):
            self.dates = dates_for_display(self.real_context)
            self.real_context = self.real_context.base_event
        else:
            self.dates = dates_for_display(self.real_context)

    def is_same_month(self, start, end):
        return start.get('month') == end.get('month')

    def get_formatted_date(self):
        date_formated = u''
        event = self.real_context
        date_spel_start = date_speller(event, self.dates.get('start_iso'))
        date_spel_end = date_speller(event, self.dates.get('end_iso'))
        # day and month
        if self.dates.get('same_day'):
            date_formated = u'{0} {1} {2}'.format(
                date_spel_start.get('day'),
                date_spel_start.get('month'),
                date_spel_start.get('year'))
        elif self.is_same_month(date_spel_start, date_spel_end):
            date_formated = u'{0} au {1} {2} {3}'.format(
                date_spel_start.get('day'),
                date_spel_end.get('day'),
                date_spel_start.get('month'),
                date_spel_start.get('year'))
        else:
            date_formated += u'{0} {1} {2} au {3} {4} {5}'.format(
                date_spel_start.get('day'),
                date_spel_start.get('month'),
                date_spel_start.get('year'),
                date_spel_end.get('day'),
                date_spel_end.get('month'),
                date_spel_start.get('year'))

        # hour
        if not self.dates.get('whole_day'):
            if self.dates.get('open_end'):
                date_formated += _(u' à ')
                date_formated += u'{0}:{1}'.format(
                    date_spel_start.get('hour'),
                    date_spel_start.get('minute2'))
            else:
                date_formated += _(u' de ')
                date_formated += u'{0}:{1}'.format(
                    date_spel_start.get('hour'),
                    date_spel_start.get('minute2'))
                date_formated += _(u' à ')
                date_formated += u'{0}:{1}'.format(
                    date_spel_end.get('hour'),
                    date_spel_end.get('minute2')
                )
        return date_formated

    def get_values_in_one_line(self, values, sep=u' - '):
        results = [safe_unicode(value) for value in values if value]
        return sep.join(results)

    def get_taxonomy_values_in_one_line(self, field_names, sep, second_sep=' '):
        text = []
        for field_name in field_names:
            value = ''
            if isinstance(field_name, dict):
                (dict_text, dict_field_name) = field_name.items()[0]
                value = self.get_taxonomy_value(dict_field_name, second_sep)
                if value:
                    if self.hack_namur(field_name, value):
                        text.append('{0} {1}'.format(dict_text, value))
            else:
                value = self.get_taxonomy_value(field_name, second_sep)
                if value:
                    if self.hack_namur(field_name, value):
                        text.append(value)
        return sep.join(text)

    def hack_namur(self, field_name, value):
        """ This is developped for Namur agenda export only """
        if isinstance(field_name, dict):
            field_name = field_name.values()[0]
        if field_name.endswith('publiccible') and value == 'Tout public':
            return False
        if field_name.endswith('gratuite') and value != 'Gratuit':
            return False
            # if field_name.endswith('danslecadrede'):
            #     import ipdb; ipdb.set_trace()
        return True

    def get_taxonomy_value(self, field_name, sep=' ', end=''):
        lang = self.real_context.language
        taxonomy_ids = self.get_value(field_name)
        if not taxonomy_ids:
            return None
        if isinstance(taxonomy_ids, basestring):
            taxonomy_ids = [taxonomy_ids]
        domain = 'collective.taxonomy.{0}'.format(
            field_name.replace('taxonomy_', '').replace('_', ''))

        sm = getSiteManager()
        utility = sm.queryUtility(ITaxonomy, name=domain)
        taxonomy_list = [taxonomy_id for taxonomy_id in taxonomy_ids]
        text = []
        if len(taxonomy_list) > 0:
            for taxonomy_id in taxonomy_list:
                text.append(
                    safe_utf8(
                        utility.translate(
                            taxonomy_id,
                            context=self.real_context,
                            target_language=lang
                        )
                    )
                )
            return '{0}{1}'.format(sep.join(text), end)
        else:
            return None

    def get_relation_field(self, field_name):
        try:
            related_obj = self.get_value(field_name)
        except:
            return None
        if not related_obj:
            return None
        if isinstance(related_obj, str):
            return self.real_context
        if isinstance(related_obj, list):
            return [obj.to_object for obj in related_obj]
        return getattr(related_obj, 'to_object', None)

    def get_relation_value(self, field_name, value_name, sep=' ', end=''):
        if not getattr(self.real_context, field_name, None):
            return False
        if isinstance(value_name, list):
            result = []
            for value in value_name:
                relation_field = self.get_relation_field(field_name)
                result.append(getattr(relation_field, value, ''))
            return u'{0}{1}'.format(sep.join(result), end)
        relation_field = self.get_relation_field(field_name)
        if isinstance(relation_field, list):
            result = []
            for rel in relation_field:
                result.append(getattr(rel, value_name, ''))
            return u'{0}{1}'.format(sep.join(result), end)
        return u'{0}{1}'.format(getattr(relation_field, value_name, ''), end)

    def get_partners(self, prefix='', sep=' '):
        if not getattr(self.real_context, 'partners', None):
            return False
        partners = self.get_relation_value('partners', 'title', sep)
        text = partners
        if prefix:
            text = u'{0} {1}'.format(safe_unicode(prefix), partners)
        return text

    def display_phones(self, related_name='contact', field_name='phone'):
        obj = self.get_relation_field(related_name)
        phone = getattr(obj, field_name, None)
        result = ''
        if phone:
            if isinstance(phone, list):
                result = u' '.join([format_phone(p)['formated'] for p in phone])
            else:
                result = format_phone(phone)['formated']
        return result

    def get_info(self):
        if not getattr(self.real_context, 'contact', None):
            return False
        obj = self.get_relation_field('contact')
        info = []
        title = getattr(obj, 'title', None)
        if title:
            info.append(title)
        phone = getattr(obj, 'phone', None)
        if not phone:
            obj = self.get_relation_field('organizer')
            phone = getattr(obj, 'phone', None)
        if phone:
            if isinstance(phone, list):
                phone = u' '.join([format_phone(p)['formated'] for p in phone])
                # hack for namur
                phone = phone.replace('+32 (0) ', '0')
                info.append(phone)
            else:
                phone = format_phone(phone)['formated']
                # hack for namur
                phone = phone.replace('+32 (0) ', '0')
                info.append(phone)
        website = getattr(obj, 'website', None)
        if website:
            info.append(website)
        if len(info) >= 1:
            infomsg = _(u'Info :')
            return u'{0} {1}'.format(infomsg, ' - '.join(info))
        else:
            return ''

    def get_address(self):
        address = []
        address.append(_(u'Où ?'))
        title = self.get_relation_value('location', 'title')
        if title:
            address.append(title)
        street = self.get_relation_value('location', 'street')
        number = self.get_relation_value('location', 'number')
        if street:
            street_with_number = street
            if number:
                street_with_number = u'{0}, {1}'.format(street, str(number))
            address.append(street_with_number)
        zip_code = self.get_relation_value('location', 'zip_code')
        city = self.get_relation_value('location', 'city')
        if city and zip_code:
            address.append(u'{0} {1}'.format(zip_code, city))
        if len(address) > 1:
            return '\n'.join(address)
        else:
            return ''

    def get_image_from_text(self, field_name=None, text=None):
        if field_name:
            text = self.get_value(field_name)
        images = []
        import bs4
        soup = bs4.BeautifulSoup(text, 'html.parser')
        for img in soup.find_all('img'):
            images.append(img.get('src'))
        return images[0] if len(images) > 0 else images


class TupleErrorPage(BrowserView):
    def __call__(self):
        event_col = self.context
        queries = []
        for query in event_col.query:
            if not isinstance(query.get('v'), tuple):
                queries.append(query)
        event_col.query = queries
        return 'End of tuple error'


class TransmoExport(BrowserView):
    def __call__(self):
        objects = {}
        # get all file in custom folder
        portal_skins = api.portal.get_tool('portal_skins')
        objects['custom'] = []
        for obj_id, item in portal_skins.custom.items():
            if item.meta_type in ['Image', 'File']:
                try:
                    data = base64.b64encode(item.data)
                    objects['custom'].append({
                        'obj_id': obj_id,
                        'meta_type': item.meta_type,
                        'data': data
                    })
                except:
                    logger.info('Not able to export {0}'.format(
                        '/'.join(item.getPhysicalPath()))
                    )
            else:
                try:
                    objects['custom'].append({
                        'obj_id': obj_id,
                        'meta_type': item.meta_type,
                        'raw': item.raw
                    })
                except:
                    logger.info('Not able to export {0}'.format(
                        '/'.join(item.getPhysicalPath()))
                    )
        objects['default_skin'] = portal_skins.default_skin
        # get list of installed profile
        portal_quickinstaller = api.portal.get_tool('portal_quickinstaller')
        product_ids = [product['id'] for product in portal_quickinstaller.listInstalledProducts()]
        objects['products'] = product_ids

        portal_membership = api.portal.get_tool('portal_membership')
        list_members = portal_membership.listMembers()
        # groups
        groups = []
        for site_group in api.group.get_groups():
            group = {}
            group['id'] = site_group.getId()
            group['title'] = site_group.title
            group['description'] = site_group.description
            group['roles'] = site_group.getRoles()
            group['groups'] = site_group.getGroups()
            users = [user.id for user in api.user.get_users(groupname=group['id']) if user in list_members]  # noqa
            group['users'] = users
            groups.append(group)
        objects['groups'] = groups
        # users
        pas = api.portal.get().acl_users
        passwords = dict(pas.source_users._user_passwords)
        users = []
        for member in list_members:
            user = {}
            user['id'] = member.getId()
            user['name'] = member.getProperty('fullname', member.getUserName())
            user['email'] = member.getProperty('email', None)
            user['fullname'] = member.getProperty('fullname', None)
            login_time = member.getProperty('login_time', None)
            if login_time == DateTime('2000/01/01'):
                user['login_date'] = ''
            else:
                user['login_date'] = login_time.strftime('%d/%m/%Y')
            last_login_time = member.getProperty(
                'last_login_time',
                None
            )
            if last_login_time == DateTime('2000/01/01'):
                user['last_login_date'] = ''
            else:
                user['last_login_date'] = last_login_time.strftime('%d/%m/%Y')
            if user['login_date'] == user['last_login_date']:
                user['last_login_date'] = ''
            user['roles'] = member.getRoles()
            user['domains'] = member.getDomains()
            user['password'] = passwords.get(user['id'])
            users.append(user)
        objects['users'] = users

        # mail control panel
        mailhost = {}
        try:
            mail_host = getUtility(IMailHost)
        except ComponentLookupError:
            mail_host = getattr(api.portal.get(), 'MailHost')
        mailhost['smtp_host'] = mail_host.smtp_host
        mailhost['smtp_port'] = mail_host.smtp_port
        mailhost['smtp_userid'] = getattr(mail_host, 'smtp_userid', None)
        mailhost['smtp_uid'] = getattr(mail_host, 'smtp_uid', None)
        mailhost['smtp_pwd'] = mail_host.smtp_pwd
        mailhost['email_from_address'] = api.portal.get().email_from_address
        mailhost['email_from_name'] = api.portal.get().email_from_name
        objects['mailhost'] = mailhost

        # geo
        lat_key = 'collective.geo.settings.interfaces.IGeoSettings.latitude'
        lng_key = 'collective.geo.settings.interfaces.IGeoSettings.longitude'
        zoom_key = 'collective.geo.settings.interfaces.IGeoSettings.zoom'
        geo = {}
        geo['latitude'] = str(api.portal.get_registry_record(lat_key))
        geo['longitude'] = str(api.portal.get_registry_record(lng_key))
        geo['zoom'] = str(api.portal.get_registry_record(zoom_key))
        objects['geo'] = geo

        # portal_languages
        portal_languages = api.portal.get_tool('portal_languages')
        objects['languages'] = portal_languages.supported_langs

        # discussion
        discussion = {}
        anonymous_comments = 'plone.app.discussion.interfaces.IDiscussionSettings.anonymous_comments'  # bool
        anonymous_email_enabled = 'plone.app.discussion.interfaces.IDiscussionSettings.anonymous_email_enabled'   # bool
        captcha = 'plone.app.discussion.interfaces.IDiscussionSettings.captcha'  # choice
        edit_comment_enabled = 'plone.app.discussion.interfaces.IDiscussionSettings.edit_comment_enabled'  # bool
        globally_enabled = 'plone.app.discussion.interfaces.IDiscussionSettings.globally_enabled'  # bool
        moderation_enabled = 'plone.app.discussion.interfaces.IDiscussionSettings.moderation_enabled'  # bool
        moderator_email = 'plone.app.discussion.interfaces.IDiscussionSettings.moderator_email'  # textline
        moderator_notification_enabled = 'plone.app.discussion.interfaces.IDiscussionSettings.moderator_notification_enabled'  # bool
        show_commenter_image = 'plone.app.discussion.interfaces.IDiscussionSettings.show_commenter_image'  # bool
        user_notification_enabled = 'plone.app.discussion.interfaces.IDiscussionSettings.user_notification_enabled'  # bool
        discussion['anonymous_comments'] = str(api.portal.get_registry_record(anonymous_comments))
        discussion['anonymous_email_enabled'] = str(api.portal.get_registry_record(anonymous_email_enabled))
        discussion['captcha'] = api.portal.get_registry_record(captcha)
        discussion['edit_comment_enabled'] = str(api.portal.get_registry_record(edit_comment_enabled))
        discussion['globally_enabled'] = str(api.portal.get_registry_record(globally_enabled))
        discussion['moderation_enabled'] = str(api.portal.get_registry_record(moderation_enabled))
        discussion['moderator_email'] = str(api.portal.get_registry_record(moderator_email))
        discussion['moderator_notification_enabled'] = str(api.portal.get_registry_record(moderator_notification_enabled))
        discussion['show_commenter_image'] = str(api.portal.get_registry_record(show_commenter_image))
        discussion['user_notification_enabled'] = str(api.portal.get_registry_record(user_notification_enabled))
        objects['discussion'] = discussion

        portal_workflow = api.portal.get_tool('portal_workflow')
        objects['workflow'] = portal_workflow.getDefaultChain()[0]

        portal_resources = getUtility(IResourceDirectory, name='persistent')
        cpskin_resources_folder = portal_resources['cpskin']
        if cpskin_resources_folder:
            resources = {}
            for res in cpskin_resources_folder.listDirectory():
                resources[res] = cpskin_resources_folder[res].data
            objects['resources'] = resources

        # abonnes
        brains = api.content.find(portal_type='NewsletterTheme')
        newsletters = {}
        for brain in brains:
            obj = brain.getObject()
            path = brain.getPath()
            subscriber_brains = obj.getSubscribers()
            subscribers = []
            for subscriber_brain in subscriber_brains:
                subscriber_obj = subscriber_brain.getObject()
                subs = {}
                subs['active'] = subscriber_obj.active
                subs['email'] = subscriber_obj.email
                subs['fullname'] = subscriber_obj.fullname
                subs['format'] = subscriber_obj.format
                subscribers.append(subs)
            newsletters[path] = subscribers
        objects['newsletters'] = newsletters

        # leadimage
        portal_properties = api.portal.get_tool('portal_properties')
        cli_properties = portal_properties.get('cli_properties', None)
        if cli_properties:
            leadimage_settings = {}
            leadimage_settings['allowed_types'] = cli_properties.allowed_types
            objects['leadimage'] = leadimage_settings

        # behaviors
        portal_types = api.portal.get_tool('portal_types')
        behaviors = {}
        for portal_type in portal_types:
            fti = portal_types[portal_type]
            if IDexterityFTI.providedBy(fti):
                behaviors[portal_type] = fti.behaviors
        objects['behaviors'] = behaviors

        portal_catalog = api.portal.get_tool('portal_catalog')
        total_objects = len(portal_catalog({}))
        objects['total_objects'] = str(total_objects)
        response = self.request.response
        response.setHeader('Content-type', 'application/json')
        return json.dumps(objects)


class TeleService(BrowserView):
    index = ViewPageTemplateFile('templates/teleservice.pt')


class EmptyPathBarViewlet(PathBarViewlet):
    index = ViewPageTemplateFile('templates/empty.pt')


class CpskinHealthy(BrowserView):
    index = ViewPageTemplateFile('templates/cpskinhealthy.pt')

    def __init__(self, context, request):
        self.portal = api.portal.get()
        self.context = context
        self.request = request
        form = request.form
        if 'method' in form.keys():
            method = form['method']
            if method in dir(self):
                try:
                    self.__getattribute__(method)()
                except:
                    msg = 'You can not start method: {0}'.format(method)
            else:
                msg = 'Method "{0}" do not exists.'.format(method)

    def title(self):
        return _(u'Cpskin Healthy')

    def _redirect(self, msg=''):
        if self.request:
            if msg:
                api.portal.show_message(message=msg,
                                        request=self.request,
                                        type='info')
            url = '{0}/cpskinhealthy'.format(self.context.absolute_url())
            self.request.response.redirect(url)
        return msg

    def contacts(self):
        """Check if collective contact is installed and use cpskin workflow"""
        results = {}
        results['errors'] = []
        qi = api.portal.get_tool('portal_quickinstaller')
        product_ids = [product['id'] for product in qi.listInstalledProducts()]
        if 'collective.contact.core' in product_ids:
            results['is_installed'] = True
        else:
            results['is_installed'] = False
            return results
        workflow_id = self.get_workflow_id('organization')
        if workflow_id == 'collective_contact_core_workflow':
            results['is_cpskin_workflow'] = False
        else:
            results['is_cpskin_workflow'] = True
        return results

    def get_workflow_id(self, type_id):
        portal_workflow = api.portal.get_tool('portal_workflow')
        workflow = portal_workflow.getWorkflowsFor(type_id)
        if len(workflow) > 1:
            self._redirect('To much workflow for contacts.')
        workflow_id = workflow[0].id
        return workflow_id

    def install_contact_core(self):
        portal_setup = api.portal.get_tool('portal_setup')
        portal_setup.runAllImportStepsFromProfile(
            'collective.contact.core:default'
        )
        self._redirect('collective.contact.core installed.')

    def set_contact_worflow(self):
        portal = api.portal.get()
        workflow_id = self.get_workflow_id('organization')
        if workflow_id == 'cpskin_collective_contact_workflow':
            self._redirect('cpskin_collective_contact_workflow already set.')
        chain = ('cpskin_collective_contact_workflow',)
        types = ('held_position',
                 'organization',
                 'person',
                 'position')
        state_map = {'active': 'active',
                     'deactivated': 'deactivated'}
        remap_workflow(portal, type_ids=types, chain=chain,
                       state_map=state_map)
        util = queryUtility(IRAMCache)
        if util is not None:
            util.invalidateAll()
        self._redirect('cpskin_collective_contact_workflow set.')

    def get_site_language(self):
        return api.portal.get().language

    def is_site_language_fr(self):
        return self.get_site_language() == 'fr'

    def set_site_language(self):
        api.portal.get().language = 'fr'
