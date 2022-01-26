# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2021 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Common setting definitions
"""

from __future__ import unicode_literals, absolute_import


class Setting(object):
    """
    Base class for all setting definitions.
    """
    group = "(General)"
    namespace = None
    name = None
    data_type = str
    choices = None
    required = False


##############################
# (General)
##############################

class rattail_app_title(Setting):
    """
    Official display title for the app.
    """
    namespace = 'rattail'
    name = 'app_title'


class rattail_node_title(Setting):
    """
    Official display title for the app node.
    """
    namespace = 'rattail'
    name = 'node_title'


class rattail_production(Setting):
    """
    If set, the app is considered to be running in "production" mode, whereas
    if disabled, the app is considered to be running in development / testing /
    staging mode.
    """
    namespace = 'rattail'
    name = 'production'
    data_type = bool


class tailbone_background_color(Setting):
    """
    Background color for this app node.  If unset, default color is white.
    """
    namespace = 'tailbone'
    name = 'background_color'


class tailbone_buefy_version(Setting):
    """
    Version of the Buefy component JS library to use for "falafel"
    based themes.  The minimum should be '0.8.6' or probably even
    '0.8.13', but feel free to experiment.
    """
    namespace = 'tailbone'
    name = 'buefy_version'


class tailbone_sticky_headers(Setting):
    """
    Whether table/grid headers should be "sticky" for *ALL* grids.
    This causes the grid header to remain visible as user scrolls down
    through the row/record list; however it isn't perfect yet.  Also
    please note, it will only work with Buefy 0.8.13 or newer.
    """
    namespace = 'tailbone'
    name = 'sticky_headers'
    data_type = bool


class tailbone_vue_version(Setting):
    """
    Version of the Vue.js library to use for "falafel" (Buefy) based
    themes.  The minimum should be '2.6.10' but feel free to
    experiment.
    """
    namespace = 'tailbone'
    name = 'vue_version'


class rattail_single_store(Setting):
    """
    If set, the app should assume there is only one Store record, and that all
    purchases etc. will pertain to it.
    """
    namespace = 'rattail'
    name = 'single_store'
    data_type = bool


class rattail_demo(Setting):
    """
    If set, the app is considered to be running in "demo" mode.
    """
    namespace = 'rattail'
    name = 'demo'
    data_type = bool


class rattail_appdir(Setting):
    """
    Path to the "app" dir for the running instance.
    """
    namespace = 'rattail'
    name = 'appdir'


class rattail_workdir(Setting):
    """
    Path to the "work" dir for the running instance.
    """
    namespace = 'rattail'
    name = 'workdir'


##############################
# Customer Orders
##############################

class rattail_custorders_new_order_requires_customer(Setting):
    """
    If set, then all new orders require a proper customer account.  If
    *not* set then just a "person" will suffice.
    """
    group = "Customer Orders"
    namespace = 'rattail.custorders'
    name = 'new_order_requires_customer'
    data_type = bool

class rattail_custorders_new_orders_allow_contact_info_choice(Setting):
    """
    If set, then user can choose from contact info options, when
    creating new order.  If *not* set then they cannot choose, and
    must use whatever the batch handler provides.
    """
    group = "Customer Orders"
    namespace = 'rattail.custorders'
    name = 'new_orders.allow_contact_info_choice'
    data_type = bool

class rattail_custorders_new_orders_restrict_contact_info(Setting):
    """
    If set, then user can only choose from existing contact info options,
    for the customer/order.  If *not* set, then user is allowed to enter
    new/different contact info.
    """
    group = "Customer Orders"
    namespace = 'rattail.custorders'
    name = 'new_orders.restrict_contact_info'
    data_type = bool

class rattail_custorders_product_price_may_be_questionable(Setting):
    """
    If set, then user may indicate that the price for a given product
    is "questionable" - which normally would cause a new step in the
    workflow, for someone to update and/or confirm the price.  If
    *not* set then user cannot mark any price as questionable.
    """
    group = "Customer Orders"
    namespace = 'rattail.custorders'
    name = 'product_price_may_be_questionable'
    data_type = bool


##############################
# DataSync
##############################

class rattail_datasync_url(Setting):
    """
    URL for datasync change queue.
    """
    group = "DataSync"
    namespace = 'rattail.datasync'
    name = 'url'


class tailbone_datasync_restart(Setting):
    """
    Command used when restarting the datasync daemon.
    """
    group = "DataSync"
    namespace = 'tailbone'
    name = 'datasync.restart'


##############################
# Email
##############################

class rattail_mail_record_attempts(Setting):
    """
    If enabled, this flag will cause Email Attempts to be recorded in the
    database, for "most" attempts to send email.
    """
    group = "Email"
    namespace = 'rattail.mail'
    name = 'record_attempts'
    data_type = bool


##############################
# FileMon
##############################

class tailbone_filemon_restart(Setting):
    """
    Command used when restarting the filemon daemon.
    """
    group = "FileMon"
    namespace = 'tailbone'
    name = 'filemon.restart'


##############################
# Inventory
##############################

class tailbone_inventory_force_unit_item(Setting):
    """
    Defines which of the possible "product key" fields should be effectively
    treated as the product key.
    """
    group = "Inventory"
    namespace = 'tailbone'
    name = 'inventory.force_unit_item'
    data_type = bool


##############################
# Products
##############################

class rattail_product_key(Setting):
    """
    Defines which of the possible "product key" fields should be effectively
    treated as the product key.
    """
    group = "Products"
    namespace = 'rattail'
    name = 'product.key'
    choices = [
        'upc',
        'item_id',
        'scancode',
    ]


class rattail_product_key_title(Setting):
    """
    Defines the official "title" (display name) for the product key field.
    """
    group = "Products"
    namespace = 'rattail'
    name = 'product.key_title'


class rattail_products_mobile_quick_lookup(Setting):
    """
    If set, the mobile Products page will only allow "quick lookup" access to
    product records.  If NOT set, then the typical record listing is shown.
    """
    group = "Products"
    namespace = 'rattail'
    name = 'products.mobile.quick_lookup'
    data_type = bool


class tailbone_products_show_pod_image(Setting):
    """
    If a product has an image within the database, it will be shown when
    viewing the product details.  If this flag is set, and the product has no
    image, then the "POD" image will be shown, if available.  If not set, the
    POD image will not be used as a fallback.
    """
    group = "Products"
    namespace = 'tailbone'
    name = 'products.show_pod_image'
    data_type = bool


##############################
# Purchasing / Receiving
##############################

class rattail_batch_purchase_allow_cases(Setting):
    """
    Determines whether or not "cases" is a valid UOM for ordering, receiving etc.
    """
    group = "Purchasing / Receiving"
    namespace = 'rattail.batch'
    name = 'purchase.allow_cases'
    data_type = bool


class rattail_batch_purchase_allow_expired_credits(Setting):
    """
    Determines whether or not "expired" is a valid type for purchase credits.
    """
    group = "Purchasing / Receiving"
    namespace = 'rattail.batch'
    name = 'purchase.allow_expired_credits'
    data_type = bool


class rattail_batch_purchase_allow_receiving_from_scratch(Setting):
    """
    Determines whether or not receiving "from scratch" is allowed.  In this
    mode, the batch starts out empty and receiver must add product to it over
    time.
    """
    group = "Purchasing / Receiving"
    namespace = 'rattail.batch'
    name = 'purchase.allow_receiving_from_scratch'
    data_type = bool


class rattail_batch_purchase_allow_receiving_from_invoice(Setting):
    """
    Determines whether or not receiving "from invoice" is allowed.  In this
    mode, the user must first upload an invoice file they wish to receive
    against.
    """
    group = "Purchasing / Receiving"
    namespace = 'rattail.batch'
    name = 'purchase.allow_receiving_from_invoice'
    data_type = bool


class rattail_batch_purchase_allow_receiving_from_purchase_order(Setting):
    """
    Determines whether or not receiving "from PO" is allowed.  In this mode,
    the user must first select the purchase order (PO) they wish to receive
    against.  The batch is initially populated with order quantities from the
    PO, and user then updates (or adds) rows over time.
    """
    group = "Purchasing / Receiving"
    namespace = 'rattail.batch'
    name = 'purchase.allow_receiving_from_purchase_order'
    data_type = bool


class rattail_batch_purchase_allow_receiving_from_purchase_order_with_invoice(Setting):
    """
    Determines whether or not receiving "from PO with invoice" is
    allowed.  In this mode, the user must first select the purchase
    order (PO) they wish to receive against, as well as upload an
    invoice file.  The batch is initially populated with order
    quantities from the PO, then the invoice data is overlaid onto it.
    """
    group = "Purchasing / Receiving"
    namespace = 'rattail.batch'
    name = 'purchase.allow_receiving_from_purchase_order_with_invoice'
    data_type = bool


class rattail_batch_purchase_allow_truck_dump_receiving(Setting):
    """
    Determines whether or not "truck dump" receiving is allowed.  This is a
    rather complicated feature, where one "parent" truck dump batch is created
    for the receiver, plus several "child" batches, one for each invoice
    involved.
    """
    group = "Purchasing / Receiving"
    namespace = 'rattail.batch'
    name = 'purchase.allow_truck_dump_receiving'
    data_type = bool


class rattail_batch_purchase_mobile_images(Setting):
    """
    If set, product images will be displayed when viewing a purchasing batch row.
    """
    group = "Purchasing / Receiving"
    namespace = 'rattail.batch'
    name = 'purchase.mobile_images'
    data_type = bool


class rattail_batch_purchase_mobile_quick_receive(Setting):
    """
    If set, a "quick receive" button will be available for mobile receiving.
    """
    group = "Purchasing / Receiving"
    namespace = 'rattail.batch'
    name = 'purchase.mobile_quick_receive'
    data_type = bool


class rattail_batch_purchase_mobile_quick_receive_all(Setting):
    """
    If set, the mobile "quick receive" button will receive "all" (remaining
    quantity) for the item, instead of "one".
    """
    group = "Purchasing / Receiving"
    namespace = 'rattail.batch'
    name = 'purchase.mobile_quick_receive_all'
    data_type = bool


##############################
# Reporting
##############################

class tailbone_reporting_choosing_uses_form(Setting):
    """
    When generating a new report, if this flag is set then you will choose the
    report from a dropdown.  If the flag is not set then you will see all
    reports listed on the page and you'll click the link for one.
    """
    group = "Reporting"
    namespace = 'tailbone'
    name = 'reporting.choosing_uses_form'
    data_type = bool


##############################
# Vendors
##############################

class rattail_vendor_use_autocomplete(Setting):
    """
    If set, `vendor` fields will use the autocomplete widget; otherwise such
    fields will use a drop-down (select) widget.
    """
    group = "Vendors"
    namespace = 'rattail'
    name = 'vendor.use_autocomplete'
    data_type = bool
