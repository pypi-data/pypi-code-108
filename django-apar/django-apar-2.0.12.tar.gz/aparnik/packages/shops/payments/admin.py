# -*- coding: utf-8 -*-
from django.contrib import admin

from aparnik.contrib.basemodels.admin import BaseModelAdmin
from aparnik.contrib.users.admin import get_user_search_fields, get_update_at
from .models import Payment, PaymentBank


# Register your models here.
class BankInline(admin.TabularInline):
    fields = ['get_bank_status', 'get_bank_type', 'get_bank_reference_number', 'get_bank_tracking_code', 'get_bank_date', 'get_bank_data', ]
    readonly_fields = ['get_bank_status', 'get_bank_type', 'get_bank_date', 'get_bank_data', 'get_bank_reference_number', 'get_bank_tracking_code', ]
    model = PaymentBank
    extra = 1

    def get_bank_status(self, obj):
        return obj.bank_record.status

    def get_bank_type(self, obj):
        return obj.bank_record.bank_type

    def get_bank_date(self, obj):
        return get_update_at(obj.bank_record)

    def get_bank_data(self, obj):
        return obj.bank_record.extra_information

    def get_bank_reference_number(self, obj):
        return obj.bank_record.reference_number

    def get_bank_tracking_code(self, obj):
        return obj.bank_record.tracking_code

    get_bank_status.short_description = 'status'


class PaymentAdmin(BaseModelAdmin):
    list_display = ['bank_reference', 'uuid', 'user', 'method', 'status', 'order_obj', 'call_back_url', 'created_at',
                    'update_at']
    list_filter = ['status', 'created_at']
    search_fields = get_user_search_fields('user') + ['uuid']
    # change_list_template = 'admin/change_list_payment.html'
    raw_id_fields = ['order_obj']
    fields = []
    exclude = []
    dynamic_raw_id_fields = []
    inlines = [BankInline]

    def __init__(self, *args, **kwargs):
        Klass = PaymentAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields

    class Meta:
        Payment

    def changelist_view(self, request, extra_context=None):
        response = super(PaymentAdmin, self).changelist_view(request, extra_context=extra_context, )
        try:
            qs = response.context_data['cl'].queryset
            qs1 = Payment.objects.values('created_at', 'status')
            # qs2 = payment.objects.values('id', 'coupon__value', 'coupon__type', )

        except (AttributeError, KeyError):
            return response
        response.context_data["date_status"] = qs1

        return response

    def change_view(self, request, object_id, form_url='', extra_context=None):
        ''' customize edit form '''
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        extra_context['show_save'] = False
        extra_context['show_save_and_add_another'] = False  # this not works if has_add_permision is True
        return super(PaymentAdmin, self).change_view(request, object_id, extra_context=extra_context)


class PaymentBankAdmin(BaseModelAdmin):
    list_display = ['payment', 'bank_record', 'created_at', 'update_at']
    list_filter = ['payment__status', 'bank_record__status', 'bank_record__bank_type', 'created_at']
    search_fields = []
    readonly_fields = []
    # change_list_template = 'admin/change_list_payment.html'
    raw_id_fields = ['payment', 'bank_record']
    fields = []
    exclude = []
    dynamic_raw_id_fields = []
    save_as = False

    def __init__(self, *args, **kwargs):
        Klass = PaymentBankAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields

    def change_view(self, request, object_id, form_url='', extra_context=None):
        ''' customize edit form '''
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        extra_context['show_save'] = False
        extra_context['show_save_and_add_another'] = False  # this not works if has_add_permision is True
        return super(PaymentBankAdmin, self).change_view(request, object_id, extra_context=extra_context)


admin.site.register(Payment, PaymentAdmin)
admin.site.register(PaymentBank, PaymentBankAdmin)
