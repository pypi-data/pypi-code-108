# -*- coding: UTF-8 -*-
# Copyright 2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from django.conf import settings
from haystack.management.commands.build_solr_schema import Command as BaseCommand

class Command(BaseCommand):
    schema_template_loc = "search/schema.xml"
    solrcfg_template_loc = "search/solrconfig.xml"

    def build_context(self, using):
        openexchangerates_app_id = getattr(settings, 'HAYSTACK_CURRENCY_FIELD_OPENEXCHANGERATES_APP_ID', None)
        context = super().build_context(using)
        if openexchangerates_app_id is None:
            context.update(CURRENCY_CONFIG='defaultCurrency="USD" currencyConfig="currency.xml"')
        else:
            context.update(CURRENCY_CONFIG='providerClass="solr.OpenExchangeRatesOrgProvider" refreshInterval="60" ratesFileLocation="http://www.openexchangerates.org/api/latest.json?app_id=' + openexchangerates_app_id + '"')
        return context


    def build_template(self, using, template_filename):
        if 'schema.xml' in template_filename:
            template_filename = self.schema_template_loc
        elif 'solrconfig.xml' in template_filename:
            template_filename = self.solrcfg_template_loc
        t = super().build_template(using, template_filename)
        return t
