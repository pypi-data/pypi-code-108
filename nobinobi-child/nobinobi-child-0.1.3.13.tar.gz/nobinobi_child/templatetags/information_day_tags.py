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

# Here, register is a django.template.Library instance, as before
from django import template
from django.utils import timezone

from nobinobi_child.models import InformationOfTheDay

register = template.Library()


@register.inclusion_tag('nobinobi_child/includes/show_iotd.html', takes_context=True)
def show_iotd(context, count=100):
    # get iotd
    if context.request.user:
        iotds = InformationOfTheDay.objects.filter(start_date__lte=timezone.now(), end_date__gte=timezone.now(),
                                                   classrooms__allowed_login=context.request.user)
    else:
        iotds = []
    return {
        "iotds": iotds[:count],
    }
