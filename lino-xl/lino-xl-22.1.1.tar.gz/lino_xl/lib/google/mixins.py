# -*- coding: UTF-8 -*-
# Copyright 2008-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import logging
from django.db import models
# from lino_xl.lib.contacts.models import Partner as oldPartner
# from lino_xl.lib.contacts.models import *
# from lino.modlib.users.models import *

logger = logging.getLogger(__name__)

from lino.api import dd, rt, _

if dd.is_installed('google'):
    try:
        from googleapiclient.errors import HttpError
    except ImportError:
        HttpError = None


# if not dd.is_installed('google'):
#
#     class GoogleCalendarSynchronized:
#         pass
#     class GoogleCalendarEventSynchronized:
#         pass
#     class GooglePeopleSynchronized:
#         pass


class GoogleSynchronized(dd.Model):
    class Meta:
        abstract = True

    if dd.is_installed('google'):

        google_id = dd.CharField(max_length=200, verbose_name=_('Google resource ID'), blank=True)

        # synchronize_google = SynchronizeGoogle()

        def do_synchronize_with_google(self):
            return True


class GoogleCalendarSynchronized(GoogleSynchronized):

    class Meta:
        abstract = True

    if dd.is_installed('google'):

        time_zone = dd.CharField(max_length=50, default='UTC')

        def save(self, *args, **kw):
            res = super(GoogleCalendarSynchronized, self).save(*args, **kw)
            if self.do_synchronize_with_google():
                if self.google_id:
                    print("use google api to update the calendar")
                else:
                    print("use google api to create the calendar")
            return res


class GoogleCalendarEventSynchronized(GoogleSynchronized):

    class Meta:
        abstract = True

    if dd.is_installed('google'):

        google_calendar = dd.ForeignKey('cal.Calendar', blank=True, null=True)
        status = dd.CharField(max_length=20, blank=True, null=True)
        location = dd.CharField(max_length=200, blank=True, null=True)

        def save(self, *args, **kw):
            res = super(GoogleCalendarEventSynchronized, self).save(*args, **kw)
            if self.do_synchronize_with_google():
                if self.google_id:
                    print("use google api to update the calendar entry")
                else:
                    print("use google api to create the calendar entry")
            return res


class GooglePeopleSynchronized(GoogleSynchronized):
    class Meta:
        abstract = True

    if dd.is_installed('google'):

        def save(self, *args, **kw):
            if self.do_synchronize_with_google():
                if not self.google_resourceName and self.name:
                    body = {'names': [{'displayName': self.name, "givenName": self.last_name, "familyName": self.first_name}]}
                    if self.email:
                        body['emailAddresses'] = [{'value': self.email, 'type': 'work'}]
                    if dd.is_installed('phones'):
                        body.update(
                            {'PhoneNumber': [{'value': self.phone, 'type': 'main'}, {'value': self.gsm, 'type': 'mobile'}]})
                    try:
                        results = service.people().createContact(body=body).execute()
                        if results and results.get('resourceName', False):
                            self.google_resourceName = results.get('resourceName', False)
                            self.google_contactID = results.get('resourceName', False).split('/')[1]
                    except HttpError as e:
                        print(e.content)
                elif self.google_resourceName:
                    try:
                        contactToUpdate = service.people().get(resourceName=self.google_resourceName,
                                                               personFields='names,emailAddresses').execute()
                        contactToUpdate['names'] = [
                            {'displayName': self.name, "givenName": self.last_name,
                             "familyName": self.first_name}]
                        service.people().updateContact(resourceName=self.google_resourceName,
                                                       updatePersonFields='names,emailAddresses',
                                                       body=contactToUpdate).execute()
                    except HttpError as e:
                        print(e.content)
            res = super(GooglePeople, self).save(*args, **kw)
            return res
