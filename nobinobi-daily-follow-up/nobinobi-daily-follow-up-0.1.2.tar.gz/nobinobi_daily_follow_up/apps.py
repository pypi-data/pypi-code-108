# -*- coding: utf-8

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

from django.apps import AppConfig
from django.db.models.signals import post_delete, pre_save, post_migrate, post_save


class NobinobiDailyFollowUpConfig(AppConfig):
    name = 'nobinobi_daily_follow_up'

    def ready(self):
        import nobinobi_daily_follow_up.signals as signals
        from nobinobi_daily_follow_up.models import Meal, Medication, DailyFollowUp, GiveMedication
        post_delete.connect(signals.auto_delete_image_on_delete, sender=Meal)
        pre_save.connect(signals.auto_delete_image_on_change, sender=Meal)
        post_delete.connect(signals.auto_delete_attachment_on_delete, sender=Medication)
        pre_save.connect(signals.auto_delete_attachment_on_change, sender=Medication)
        post_migrate.connect(signals.create_group_nobinobi_daily_follow_up, sender=self)
        post_migrate.connect(signals.create_group_admin_nobinobi_daily_follow_up, sender=self)
        post_save.connect(signals.medication_on_daily_follow_up, sender=DailyFollowUp)
        post_delete.connect(signals.delete_notification_after_delete_givemedication, sender=GiveMedication)
        post_save.connect(signals.create_notification_after_save_givemedication, sender=GiveMedication)
        post_save.connect(signals.create_troubleshooting_in_daily_follow_up, sender=DailyFollowUp)
