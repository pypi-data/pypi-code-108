# -*- coding: utf-8 -*-


from django.contrib import admin
from aparnik.contrib.users.admin import get_update_at, get_user_search_fields
from aparnik.contrib.basemodels.admin import BaseModelAdmin, BaseModelTabularInline

from .models import ChatSession, ChatSessionMember, ChatSessionMessage


# Register your models here.
# Inline exercise
class ChatSessionMessageInline(BaseModelTabularInline):
    model = ChatSessionMessage
    raw_id_fields = ['user', 'file_obj']
    fk_name = 'chat_session'
    exclude = []
    extra = 1

    def __init__(self, *args, **kwargs):
        Klass = ChatSessionMessageInline
        Klass_parent = BaseModelTabularInline

        super(Klass, self).__init__(*args, **kwargs)
        self.exclude = Klass_parent.exclude + self.exclude


class ChatSessionMemberInline(BaseModelTabularInline):
    model = ChatSessionMember
    raw_id_fields = ['user']
    fk_name = 'chat_session'
    exclude = []
    extra = 1

    def __init__(self, *args, **kwargs):
        Klass = ChatSessionMemberInline
        Klass_parent = BaseModelTabularInline

        super(Klass, self).__init__(*args, **kwargs)
        self.exclude = Klass_parent.exclude + self.exclude


class ChatSessionAdmin(BaseModelAdmin):
    fields = ['owner', 'cover_obj', 'title', ]
    list_display = ['uri', get_update_at,]
    inlines = [ChatSessionMemberInline, ChatSessionMessageInline]
    list_filter = []
    search_fields = get_user_search_fields('owner') + []
    exclude = []
    raw_id_fields = ['owner', 'cover_obj', ]
    dynamic_raw_id_fields = []

    def __init__(self, *args, **kwargs):
        Klass = ChatSessionAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields




admin.site.register(ChatSession, ChatSessionAdmin)
