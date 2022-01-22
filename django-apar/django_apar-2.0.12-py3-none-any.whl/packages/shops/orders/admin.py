# -*- coding: utf-8 -*-

import datetime
from django.contrib import admin
from django.utils.html import format_html
from import_export import resources, fields
from import_export.admin import ExportActionMixin
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
from aparnik.contrib.users.admin import get_update_at, get_user_search_fields
from aparnik.contrib.basemodels.admin import BaseModelAdmin, BaseModelTabularInline
from .models import Order, OrderItem
from django.utils.translation import gettext_lazy as _

# Rcegister your models here.
from ..payments.models import Payment


class OrderItemInline(BaseModelTabularInline):
    model = OrderItem
    raw_id_fields = ['product_obj']
    fk_name = 'order_obj'
    exclude = []
    extra = 1

    def __init__(self, *args, **kwargs):
        Klass = OrderItemInline
        Klass_parent = BaseModelTabularInline

        super(Klass, self).__init__(*args, **kwargs)
        self.exclude = Klass_parent.exclude + self.exclude


# class OrderItemAdmin(BaseModelAdmin):
#     list_display = ['order_obj', 'product', 'price', 'quantity']
#     raw_id_fields = ['order_obj']
#     search_fields = ['order_obj__id', 'product_obj__title']
#     fields = ['__all__']
#     inlines = [OrderItemInline]
#     list_filter = ['status', 'created_at']
#     exclude = []
#     dynamic_raw_id_fields = []
#
#     def __init__(self, *args, **kwargs):
#         Klass = OrderItemAdmin
#         Klass_parent = BaseModelAdmin
#
#         super(Klass, self).__init__(*args, **kwargs)
#         self.fields = Klass_parent.fields + self.fields
#         self.list_display = Klass_parent.list_display + self.list_display
#         self.list_filter = Klass_parent.list_filter + self.list_filter
#         self.search_fields = Klass_parent.search_fields + self.search_fields
#         self.exclude = Klass_parent.exclude + self.exclude
#         self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields
#         self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields
#
#     class Meta:
#         OrderItem

def invoice_link(obj):
    return format_html(
        '<a href="{0}" target="blank" class="button">Invoice</a>',
        obj.get_pay_uri()
    )


invoice_link.short_description = "Invoice"


class PaymentInline(admin.TabularInline):
    model = Payment
    fk_name = 'order_obj'
    show_change_link = True
    extra = 0

    def get_readonly_fields(self, request, obj=None):
        return list(set(
            [field.name for field in self.opts.local_fields] +
            [field.name for field in self.opts.local_many_to_many]
        ))

    def has_change_permission(self, request, obj=None):
        return False


class OrderResource(resources.ModelResource):
    order_code = fields.Field(attribute='order_code', column_name=_('Order code'))
    user = fields.Field(attribute='user_id', column_name=_('User ID'))
    uuid = fields.Field(attribute='uuid', column_name=_('UUID'))
    total_cost_order = fields.Field(attribute='total_cost_order', column_name=_('Total cost'))
    discount_cost = fields.Field(attribute='discount_cost', column_name=_('Discount cost'))
    total_cost = fields.Field(attribute='total_cost', column_name=_('Total payment'))
    coupon = fields.Field(attribute='coupon__code', column_name=_('Coupon code'))
    status = fields.Field(attribute='status', column_name=_('Status payment'))
    created_at = fields.Field(attribute='created_at', column_name=_('Created date'))
    update_at = fields.Field(attribute='update_at', column_name=_('Update date'))
    payment_link = fields.Field(attribute='payment_link', column_name=_('Invoice link'))

    class Meta:
        model = Order
        fields = ['user', 'uuid', 'status', 'created_at', 'update_at', 'tax_cost']
        exclud = ['address_obj', 'postal_cost_value', 'is_sync_with_websites']

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(OrderResource, self).__init__()

    def dehydrate_order_code(self, obj):
        return obj.order_code

    def dehydrate_total_cost_order(self, obj):
        return "%s" % obj.get_total_cost_order()

    def dehydrate_total_cost(self, obj):
        return "%s" % obj.get_total_cost()

    def dehydrate_discount_cost(self, obj):
        return '%s' % obj.get_discount()

    def dehydrate_payment_link(self, obj):
        return "%s" % self.request.build_absolute_uri(obj.get_pay_uri())

    # Optimization of exporting operations with related models
    def get_queryset(self, queryset=None):
        if queryset is None:
            queryset = Order.objects.all()
        return queryset.prefetch_related('coupon', 'items')

    def export(self, queryset=None):
        queryset = self.get_queryset(queryset)
        fetched_queryset= list(queryset)
        return super().export(fetched_queryset)


class OrderAdmin(ExportActionMixin, BaseModelAdmin):
    resource_class = OrderResource
    # list_display = ['id', 'first_name', 'last_name', 'email',
    #                 'address', 'postal_code', 'city', 'paid',
    #                 'created', 'updated']
    # list_filter = ['paid', 'created', 'updated']
    fields = ['user', 'status', 'address_obj', 'whom', ]
    list_display = ['user', 'coupon', 'uuid', invoice_link, 'status', 'whom', 'is_sync_with_websites', get_update_at]
    inlines = [OrderItemInline, PaymentInline]
    list_filter = ['status', 'whom', 'is_sync_with_websites', ('created_at', DateRangeFilter), ('update_at', DateTimeRangeFilter)]
    search_fields = get_user_search_fields('user') + ['coupon__code', 'uuid', 'items__product_obj__title']
    exclude = []
    raw_id_fields = ['user', 'coupon', 'address_obj']
    dynamic_raw_id_fields = []

    def get_resource_kwargs(self, request, *args, **kwargs):
        return {'request': request}

    def __init__(self, *args, **kwargs):
        Klass = OrderAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields


admin.site.register(Order, OrderAdmin)
# admin.site.register(OrderItem, OrderItemAdmin)
