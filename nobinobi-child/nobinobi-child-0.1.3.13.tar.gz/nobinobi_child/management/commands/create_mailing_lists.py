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

# from config.wsgi import logger
import os

from django.conf import settings
from django.core.handlers.base import logger
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.utils.translation import gettext as _

from nobinobi_child.models import Child, Classroom, AgeGroup, ChildToContact
import csv

def write_csv_from_children(children, date, type):
    type = str(type)
    mailing_file = os.path.join(getattr(settings, "MEDIA_ROOT"), "mailing/mailing_lists_{}_{}.csv".format(type, date))
    os.makedirs(os.path.dirname(mailing_file), exist_ok=True)
    with open(mailing_file, mode='w', encoding="UTF8") as csv_file:
        fieldnames = ['email', 'first_name', 'last_name']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for child in children:
            ctc_parents = ChildToContact.objects.filter(child=child)
            for ctc_contact in ctc_parents:
                contact = ctc_contact.contact
                if contact.email and contact.first_name and contact.last_name:
                    writer.writerow(
                        {'email': contact.email, 'first_name': contact.first_name, 'last_name': contact.last_name})


class Command(BaseCommand):
    help = _("Command for create a mailing lists of parents.")

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '--all',
            type=str,
            help=_(
                "--all all for all child")
        )
        parser.add_argument(
            '--classroom',
            type=str,
            help=_(
                "--classroom classroom_name for child in this classroom.")
        )
        parser.add_argument(
            '--age-group',
            type=str,
            help=_(
                "--age-group age_group_name for child in this age group.")
        )

    def handle(self, *args, **options):
        logger.info(_("*** Launch of create a mailing lists of parents task. ***"))
        self.stdout.write(self.style.SUCCESS(_("*** Launch of create a mailing lists of parents task. ***")))
        all = options['all']
        classroom = options['classroom']
        age_group = options['age_group']
        date = timezone.localdate()
        if all == "all":
            children = Child.objects.filter(status__exact=Child.STATUS.in_progress)
            self.stdout.write(self.style.SUCCESS(_("*** Options : all ***")))
            # create the csv
            write_csv_from_children(children, date, all)

        if classroom:
            try:
                classroom = Classroom.objects.get(name__iexact=classroom)
            except Classroom.DoesNotExist:
                try:
                    classroom = Classroom.objects.get(slug__icontains=classroom)
                except Classroom.DoesNotExist:
                    raise CommandError('Classroom "%s" does not exist' % classroom)

            self.stdout.write(self.style.SUCCESS(_("*** Options : Classroom ***")))
            children = Child.objects.filter(status__exact=Child.STATUS.in_progress, classroom=classroom)
            write_csv_from_children(children, date, classroom)

        if age_group:
            try:
                age_group = AgeGroup.objects.get(name__iexact=age_group)
            except AgeGroup.DoesNotExist:
                try:
                    age_group = AgeGroup.objects.get(slug__icontains=age_group)
                except AgeGroup.DoesNotExist:
                    raise CommandError(_('Age group "{}" does not exist').format(age_group))

            self.stdout.write(self.style.SUCCESS(_("*** Options : Age group ***")))
            children = Child.objects.filter(status__exact=Child.STATUS.in_progress,
                                            age_group=age_group)
            write_csv_from_children(children, date, age_group)

        if not all and not age_group and not classroom:
            raise CommandError(_('No option selected'))

        self.stdout.write(self.style.SUCCESS(_("*** End of create a mailing lists of parents task. ***")))
        logger.info(_("*** End of create a mailing lists of parents task.. ***"))
