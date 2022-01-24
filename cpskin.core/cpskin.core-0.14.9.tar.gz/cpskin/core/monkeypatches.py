# -*- coding: utf-8 -*-
from datetime import datetime
from plone import api
from plone.formwidget.datetime.z3cform.widget import DatetimeWidget
from plone.formwidget.datetime.z3cform.widget import DateWidget
from Products.CMFCore.utils import getToolByName
from Products.PluginIndexes.KeywordIndex.KeywordIndex import KeywordIndex


def related2brains(self, related):
    """Return a list of brains based on a list of relations. Will filter
    relations if the user has no permission to access the content.

    :param related: related items
    :type related: list of relations
    :return: list of catalog brains
    """
    catalog = getToolByName(self.context, 'portal_catalog')
    brains = []
    for r in related:
        path = r.to_path
        if not path:
            # See #18546 for broken related items
            continue
        # the query will return an empty list if the user has no
        # permission to see the target object
        brains.extend(catalog(path=dict(query=path, depth=0)))
    return brains


def afterMemberAdd(self, member, id, password, properties):
    """
    Called by portal_registration.addMember() after a member
    has been added successfully
    """
    # if this is an auto registration, not an administrator action
    groups_tool = api.portal.get_tool('portal_groups')
    group_id = 'citizens'
    if group_id not in groups_tool.getGroupIds():
        groups_tool.addGroup(group_id)
    if api.user.is_anonymous():
        api.group.add_user(groupname=group_id, user=member)


def keyword_apply_index(self, request, resultset=None):
    indexes = ('standardTags', 'iamTags', 'isearchTags', 'hiddenTags')
    for key in [k for k in indexes if k in request and self.id == k]:
        request_key = request.get(key, {})
        if hasattr(request_key, 'query'):
            query_value = request_key.get('query')
            if isinstance(query_value, unicode):
                request[key]['query'] = query_value.encode('utf8')
        elif getattr(request_key, 'get', None):
            query_value = request_key.get('query')
            if isinstance(query_value, (list, tuple)):
                values = []
                for value in query_value:
                    if isinstance(value, unicode):
                        values.append(value.encode('utf8'))
                    else:
                        values.append(value)
                request[key]['query'] = values
        else:
            if isinstance(request_key, unicode):
                request[key] = request_key.encode('utf8')
        if isinstance(request.get(key), dict):
            if request.get(key).get('query') is None:
                request[key]['query'] = []
            elif isinstance(request[key]['query'], unicode):
                request[key]['query'] = request[key]['query'].encode('utf8')
    return super(KeywordIndex, self)._apply_index(request, resultset)


def date_widget_years(self):
    try:
        current = int(self.year)
    except:
        current = -1

    value = datetime.now().year
    now = int(value)
    before = now + self.years_range[0]
    after  = now + self.years_range[1]
    year_range = range(*(before, after))
    return [{'value': x,
             'name': x,
             'selected': x == current}
            for x in year_range]


def date_widget_update(self):
    now = datetime.now()
    min_value = -10
    max_value = 10
    if self.field.min:
        min_value = self.field.min.year - now.year
    if self.field.max:
        max_value = self.field.max.year - now.year + 1
    self.years_range = (min_value, max_value)
    super(DateWidget, self).update()


def datetime_widget_update(self):
    now = datetime.now()
    min_value = -10
    max_value = 10
    if self.field.min:
        min_value = self.field.min.year - now.year
    if self.field.max:
        max_value = self.field.max.year - now.year + 1
    self.years_range = (min_value, max_value)
    super(DatetimeWidget, self).update()
