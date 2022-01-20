# -*- coding: utf-8 -*-
from collective.contact.core.browser.basefields import views
from collective.contact.core.browser.organization import Organization
from collective.contact.core.browser.person import Person
from collective.contact.core.browser.position import Position
from collective.contact.core.content.organization import IOrganization
from cpskin.core.interfaces import ICPSkinCoreLayer
from five import grok


grok.templatedir('templates')


class OrganizationView(Organization):

    def _update(self):
        super(OrganizationView, self)._update()
        self.groups = tuple()


class PositionView(Position):

    def _update(self):
        super(PositionView, self)._update()
        self.groups = tuple(
            [group for group in self.groups if group.__name__ != 'coordinates']
        )


class PersonView(Person):

    def _update(self):
        super(PersonView, self)._update()
        self.groups = tuple(
            [group for group in self.groups if group.__name__ != 'coordinates']
        )


class OrganizationBaseFieldsView(views.OrganizationBaseFields):
    grok.name('basefields')
    grok.context(IOrganization)
    grok.template('organization_basefields')
    grok.layer(ICPSkinCoreLayer)
