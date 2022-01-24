# -*- coding: UTF-8 -*-
# Copyright 2011-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""Adds default data for `CoachingEnding`.

"""

from lino.api.dd import babelkw
from lino.api import rt, _


def objects():
    CoachingEnding = rt.models.coachings.CoachingEnding

    yield CoachingEnding(**babelkw('name',
                                   de="Übergabe an Kollege",
                                   fr="Transfert vers collègue",
                                   en="Transfer to colleague",))
    yield CoachingEnding(**babelkw('name',
                                   de="Einstellung des Anrechts auf SH",
                                   fr="Arret du droit à l'aide sociale",
                                   en="End of right on social aid"))
    yield CoachingEnding(**babelkw('name',
                                   de="Umzug in andere Gemeinde",
                                   fr="Déménagement vers autre commune",
                                   en="Moved to another town"))
    yield CoachingEnding(**babelkw('name',
                                   de="Hat selber Arbeit gefunden",
                                   fr="A trouvé du travail",
                                   en="Found a job"))
