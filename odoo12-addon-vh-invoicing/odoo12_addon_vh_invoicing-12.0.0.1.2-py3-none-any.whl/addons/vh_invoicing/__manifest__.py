# -*- coding: utf-8 -*-
{
  'name': "vertical-habitatge-invoicing",

  'summary': """
    Invoicing process for habitatge.""",

  'author': "Coopdevs",
  'website': "https://gitlab.com/coopdevs/vertical-habitatge",

  # Categories can be used to filter modules in modules listing
  # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
  # for the full list
  'category': 'vertical-habitatge',
  'version': '12.0.0.1.2',

  # any module necessary for this one to work correctly
  'depends': ['base','account','account_payment_order','contract','vh'],

  # always loaded
  'data': [
    'security/ir.model.access.csv',
    'data/vh_ir_sequence.xml',
    'data/vh_account_journal.xml',
    'views/vh_account_journal.xml',
    'views/vh_config_settings.xml',
    'views/vh_invoicing_menu_root_config.xml',
    'views/vh_contract.xml',
    'views/vh_invoicing_order.xml',
    'views/vh_invoicing_order_item.xml',
    'views/vh_invoicing_order_item_email.xml',
    'views/vh_invoicing_contact_group.xml',
    'views/vh_invoice.xml',
    'views/vh_payment_order.xml',
    'views/vh_product.xml'
  ],
}
