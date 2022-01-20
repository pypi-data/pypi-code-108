# -*- coding: utf-8

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

from django.apps import AppConfig
from django.db.models.signals import post_migrate


class NobinobiChildConfig(AppConfig):
    name = 'nobinobi_child'

    def ready(self):
        from nobinobi_child.signals import create_group_nobinobi_child, create_group_admin_nobinobi_child
        post_migrate.connect(create_group_nobinobi_child, sender=self)
        post_migrate.connect(create_group_admin_nobinobi_child, sender=self)
