#  Copyright (C) 2020 <Florian Alu - Prolibre - https://prolibre.com
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from django.urls import reverse
from django.utils.translation import gettext as _
from menu import Menu, MenuItem

from nobinobi_child.utils import has_view_child, has_view_staff, has_view_iotd

Menu.add_item(
    "main",
    MenuItem(
        title=_("Children"),
        url="/child/",
        icon="fa fa-child",
        children=[
            MenuItem(
                title=_("Children list"),
                url=reverse("nobinobi_child:Child_list"),
                icon="fas fa-list"),
            MenuItem(
                title=_("Child picture"),
                url=reverse("nobinobi_child:child_picture_select"),
                icon="fas fa-camera"),
            MenuItem(
                title=_("Information of the day"),
                url=reverse("nobinobi_child:InformationOfTheDay_list"),
                check=lambda request: has_view_iotd(request),
                icon="fas fa-list"),
            MenuItem(
                title=_("Absences"),
                url=reverse("nobinobi_child:Absence_list"),
                icon="fas fa-list"),
        ],
        check=lambda request: has_view_child(request)
    )
)

# staff
Menu.add_item(
    "staff",
    MenuItem(
        title=_("Staff"),
        url="/staff/",
        icon="fa fa-user",
        children=[
            MenuItem(
                title=_("Staffs list"),
                url=reverse("nobinobi_child:Staff_list"),
                icon="fas fa-list"),
        ],
        check=lambda request: has_view_staff(request)
    )
)
# Menu.add_item("main", MenuItem("Staff Only",
#                                reverse("reports.views.staff"),
#                                check=lambda request: request.user.is_staff))
#
# Menu.add_item("main", MenuItem("Superuser Only",
#                                reverse("reports.views.superuser"),
#                                check=lambda request: request.user.is_superuser))
