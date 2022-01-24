# -*- coding: UTF-8 -*-
# Copyright 2016-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.api import dd, _
from lino.modlib.system.choicelists import ObservedEvent
from lino_xl.lib.tickets.choicelists import T00, T24, combine

from .roles import VotesStaff


class VoteStates(dd.Workflow):
    required_roles = dd.login_required(VotesStaff)
    # verbose_name = _("Vote state")
    verbose_name_plural = _("Vote states")
    # item_class = VoteState
    # max_length = 3
    # todo_states = []

add = VoteStates.add_item
# print("20210908 installed", dd.is_installed("votes"))
# print("20210908 use_candidatures",  dd.plugins.votes.use_candidatures)
if dd.is_installed("votes") and dd.plugins.votes.use_candidatures:
    # add('10', _("Watching"), _("Interest"), 'watching')
    # add('20', _("Candidate"), _("Offer"), 'candidate', show_in_todo=True)
    # add('30', _("Assigned"), _("Job to do"), 'assigned', show_in_todo=True)
    # add('40', _("Done"), _("Job done"), 'done')
    # add('50', _("Rated"), _("Job rated"), 'rated')
    # add('60', _("Cancelled"), _("Cancelled offer"), 'cancelled')  # Absage
    add('00', _("Author"), 'author')
    add('05', _("Invited"), 'invited')
    add('10', _("Watching"), 'watching')
    # add('15', _("Pro"), 'pro')
    # add('16', _("Con"), 'con')
    add('20', _("Candidate"), 'candidate', show_in_todo=True)
    add('30', _("Assigned"), 'assigned', show_in_todo=True)
    add('40', _("Done"), 'done')
    add('50', _("Rated"), 'rated')
    add('60', _("Cancelled"), 'cancelled')  # Absage
else:
    add('10', _("Watching"), 'watching')
    add('20', _("Silenced"), 'silenced')



class Ratings(dd.ChoiceList):
    verbose_name = _("Rating")
    verbose_name_plural = _("Ratings")


add = Ratings.add_item
add('10', _("Very good"))
add('20', _("Good"))
add('30', _("Satisfying"))
add('40', _("Deficient"))
add('50', _("Insufficient"))
add('90', _("Unratable"))


class VoteEvents(dd.ChoiceList):
    verbose_name = _("Observed event")
    verbose_name_plural = _("Observed events")


class VoteEventCreated(ObservedEvent):
    text = _("Created")

    def add_filter(self, qs, pv):
        if pv.start_date:
            qs = qs.filter(created__gte=combine(pv.start_date, T00))
        if pv.end_date:
            qs = qs.filter(created__lte=combine(pv.end_date, T24))
        return qs

VoteEvents.add_item_instance(VoteEventCreated('created'))
