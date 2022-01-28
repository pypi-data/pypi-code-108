#      Copyright (C) 2020 <Florian Alu - Prolibre - https://prolibre.com
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU Affero General Public License as
#      published by the Free Software Foundation, either version 3 of the
#      License, or (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU Affero General Public License for more details.
#
#      You should have received a copy of the GNU Affero General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.


from django.urls import reverse
from django.utils.translation import gettext as _
from menu import Menu, MenuItem

from nobinobi_daily_follow_up.utils import has_view_dailyfollowup

Menu.add_item(
    "main",
    MenuItem(
        title=_("Daily follow-up"),
        url="/daily-follow-up/",
        icon="fa fa-chart-bar",
        children=[
            MenuItem(
                title=_("Presences of the day"),
                url=reverse("nobinobi_daily_follow_up:Presence_choice"),
                icon="fas fa-list"),
            MenuItem(
                title=_("Presences of the week"),
                url=reverse("nobinobi_daily_follow_up:presence_week_choice"),
                icon="fas fa-list"),
            MenuItem(
                title=_("Institution: Presences"),
                url=reverse("nobinobi_daily_follow_up:admin_presence_week"),
                icon="fas fa-list",
                check=lambda request: request.user.is_staff),
            MenuItem(
                title=_("Summary by child"),
                url=reverse("nobinobi_daily_follow_up:DailyFollowUp_summary_week_choice"),
                icon="fas fa-list"),
            MenuItem(
                title=_("Stroll List"),
                url=reverse("nobinobi_daily_follow_up:stroll_choice"),
                icon="fas fa-door-open"),
            MenuItem(
                title=_("Group activities"),
                url=reverse("nobinobi_daily_follow_up:group_activity_choice_view"),
                icon="fas fa-users"),
            MenuItem(
                title=_("Group notes"),
                url=reverse("nobinobi_daily_follow_up:group_daily_follow_up_choice_view"),
                icon="fas fa-users"),
            MenuItem(
                title=_("Multiday medication"),
                url=reverse("nobinobi_daily_follow_up:Multiday_Medication"),
                icon="fas fa-prescription-bottle-alt"),
            MenuItem(
                title=_("Early troubleshooting"),
                url=reverse("nobinobi_daily_follow_up:EarlyTroubleshooting_list"),
                icon="fas fa-prescription-bottle-alt"),
        ],
        check=lambda request: has_view_dailyfollowup(request)
    )
)

# Menu.add_item("main", MenuItem("Staff Only",
#                                reverse("reports.views.staff"),
#                                check=lambda request: request.user.is_staff))
#
# Menu.add_item("main", MenuItem("Superuser Only",
#                                reverse("reports.views.superuser"),
#                                check=lambda request: request.user.is_superuser))
