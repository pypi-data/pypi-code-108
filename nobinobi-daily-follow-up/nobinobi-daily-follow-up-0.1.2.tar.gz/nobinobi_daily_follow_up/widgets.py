# -*- coding: utf-8 -*-

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
#

from crispy_forms.layout import Field


class InlineCheckboxesImage(Field):
    """
    Layout object for rendering checkboxes inline::

    InlineCheckboxes('field_name')
    """
    template = "nobinobi_daily_follow_up/layout/checkboxselectmultiple_inline_image.html"
    TEMPLATE_PACK = "bootstrap4"

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, **kwargs):
        return super(InlineCheckboxesImage, self).render(
            form, form_style, context, template_pack=template_pack,
            extra_context={'inline_class': 'inline'}
        )


class InlineRadiosImage(Field):
    """
    Layout object for rendering radiobuttons inline::

        InlineRadios('field_name')
    """
    template = "nobinobi_daily_follow_up/layout/radioselect_inline_image.html"
    TEMPLATE_PACK = "bootstrap4"

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, **kwargs):
        return super(InlineRadiosImage, self).render(
            form, form_style, context, template_pack=template_pack,
            extra_context={'inline_class': 'inline'}
        )
