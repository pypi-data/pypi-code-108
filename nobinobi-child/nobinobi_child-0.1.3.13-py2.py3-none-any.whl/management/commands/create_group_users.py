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

import logging

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from nobinobi_child.models import Absence, Child

GROUP_NAME = getattr(settings, "GROUP_NAME_USERS", "Users")


class Command(BaseCommand):
    help = "Creates group user and assign good permission in it."

    def handle(self, *args, **options):
        absences_type = ContentType.objects.get_for_model(Absence)
        children_type = ContentType.objects.get_for_model(Child)

        group, created = Group.objects.get_or_create(name=('%s' % GROUP_NAME))
        if created:
            logging.info('%s Group created' % GROUP_NAME)
            self.stdout.write(_("Groups {} created successfully.").format(group))
            # Code to add permission to group ???
        permissions = [
            (absences_type, "add_absence"),
            (absences_type, "change_absence"),
            (absences_type, "delete_absence"),
            (absences_type, "view_absence"),
            (children_type, "view_child"),
        ]
        # Now what - Say I want to add 'Can add project' permission to new_group?
        permission_list = []
        for content_type, perm in permissions:
            permission_list.append(
                Permission.objects.get(content_type=content_type, codename=perm))

        for permission in permission_list:
            group.permissions.add(permission)
            self.stdout.write(_("Permission {} added to {} successfully.").format(permission, group))
