# Copyright 2012-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import re
from os.path import join, dirname

from django.conf import settings
from lino.api import dd, _
from lino_xl.lib.vat.mixins import VatDeclaration
from lino.modlib.printing.actions import WriteXmlAction

from .choicelists import DeclarationFields

DEMO_JOURNAL_NAME = "VAT"

# print("20170711a {}".format(DeclarationFields.get_list_items()))


class WriteIntracomStatement(WriteXmlAction):

    # Originally copied from lino_xl.lib.finan.actions.WritePaymentsInitiation.
    # The get_printable_context() method is currently duplicated. We might write
    # a common base class WriteVoucherXmlAction.

    label = _("Intracom statement")
    tplname = "intracom_statement"
    xsd_file = join(dirname(__file__), 'XSD', 'NewICO-in_v0_9.xsd')

    def get_printable_context(self, bm, elem, ar):
        context = super(
            WriteIntracomStatement, self).get_printable_context(
                bm, elem, ar)
        sc = settings.SITE.site_config.site_company
        if not sc:
            raise Warning(_("You must specify a site owner"))
        context.update(site_config=settings.SITE.site_config)
        clients_list = list(elem.intracom_statement_iterator())
        total_amount = sum([p.total_base for p in clients_list])
        context.update(total_amount=total_amount)
        context.update(clients_list=clients_list)
        if sc.vat_id:
            # raise Warning(_("Site owner has no national ID"))
            # if not sc.vat_id.startswith("BE-"):
            #     raise Warning(_("Site owner has invalid ID {}").format(
            #         sc.vat_id))
            # our_id = sc.vat_id[3:]
            our_id = re.sub('[^0-9]', '', sc.vat_id[3:])
            context.update(our_name=str(sc))
            context.update(our_id=our_id)
            context.update(our_issuer='KBO-BCE')
        # raise Exception(str(context))
        return context


class Declaration(VatDeclaration):

    fields_list = DeclarationFields

    class Meta:
        app_label = 'bevat'
        verbose_name = _("Belgian VAT declaration")
        verbose_name_plural = _("Belgian VAT declarations")

    write_intracom_statement = WriteIntracomStatement()

    @dd.displayfield(_("Print"))
    def print_actions(self, ar):
        if ar is None:
            return ''
        elems = []
        elems.append(ar.instance_action_button(self.write_intracom_statement))
        return E.p(*join_elems(elems, sep=", "))


for fld in DeclarationFields.get_list_items():
    dd.inject_field('bevat.Declaration', fld.name, fld.get_model_field())
