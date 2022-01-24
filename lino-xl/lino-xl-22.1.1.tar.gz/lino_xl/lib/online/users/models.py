# -*- coding: UTF-8 -*-
# Copyright 2015-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.api import dd, rt, _

contacts = dd.resolve_app('contacts')
Person = contacts.Person

from lino.modlib.users.models import *

from .choicelists import UserStates



#
#class User(User, Phonable, AddressLocation):
class User(User, Person):

    """
    Adds the following database fields to the User model.

    .. attribute:: callme_mode

        Whether other users can see my contact data.

    .. attribute:: user_state

        The registration state of this user.

    """

    workflow_state_field = 'user_state'

    class Meta(User.Meta):
        app_label = 'users'
        abstract = dd.is_abstract_model(__name__, 'User')

    callme_mode = models.BooleanField(
        _('Others may contact me'), default=True)

    user_state = UserStates.field(default=UserStates.as_callable('new'))

    # partner = dd.DummyField()

    # def get_person(self):
    #     return self

    def get_detail_action(self, ar):
        a = super(User, self).get_detail_action(ar)
        if a is not None:
            return a
        if self.callme_mode:
            a = rt.models.users.OtherUsers.detail_action
        if a is not None and a.get_view_permission(ar.get_user().user_type):
            return a

    @dd.htmlbox(_("About me"))
    def about_me(self, ar):
        return self.remarks

    @classmethod
    def get_simple_parameters(cls):
        s = list(super(User, cls).get_simple_parameters())
        s.append('user_state')
        return s

    # def get_default_table(self, ar):
    #     tbl = super(User, self).get_default_table(ar)
    #     return rt.models.users.OtherUsers

    # def __str__(self):
    #     s = self.get_full_name()
    #     if self.callme_mode:
    #         if self.tel:
    #             s += " ({})".format(self.tel)
    #     return s


dd.update_field('users.User', 'remarks', verbose_name=_("About me"))
