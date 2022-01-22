# -*- coding: utf-8 -*-
from rest_framework import serializers

from aparnik.api.serializers import ModelSerializer
from aparnik.contrib.users.api.serializers import UserSummaryListSerializer
from aparnik.contrib.filefields.api.serializers import FileFieldListSerailizer
from aparnik.contrib.basemodels.api.serializers import BaseModelDetailSerializer
from ..models import Ticket, TicketConversation


class TicketListSerializer(BaseModelDetailSerializer):

    user = serializers.SerializerMethodField()
    url_conversation = serializers.SerializerMethodField()
    url_add_conversation = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(TicketListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Ticket
        fields = BaseModelDetailSerializer.Meta.fields + [
            'url_conversation',
            'url_add_conversation',
            'user',
            'title',
            'priority',
            'status',
            'uuid',
            'department',
            'created_at'
        ]

        read_only_fields = BaseModelDetailSerializer.Meta.read_only_fields + [
            'url_conversation',
            'url_add_conversation',
            'user',
        ]

    def get_url_conversation(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_conversation_uri())

    def get_url_add_conversation(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_add_conversation_uri())

    def get_user(self, obj):
        return UserSummaryListSerializer(obj.user_obj, many=False, read_only=True, context=self.context).data


class TicketCreateSerializer(TicketListSerializer):
    # model_obj_id = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = Ticket
        fields = TicketListSerializer.Meta.fields + [
            'resourcetype',
        ]
        read_only_fields = TicketListSerializer.Meta.read_only_fields + [
            'resourcetype'
        ]


class TicketConversationListSerializer(ModelSerializer):

    user = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()
    resourcetype = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(TicketConversationListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = TicketConversation
        fields = [
            'id',
            'user',
            'content',
            'files',
            'created_at',
            'resourcetype',
        ]

        read_only_fields = [
            'user',
            'files',
            'resourcetype',
        ]

    def get_user(self, obj):
        return UserSummaryListSerializer(obj.user_obj, many=False, read_only=True, context=self.context).data


    def get_files(self, obj):
        return FileFieldListSerailizer(obj.files_obj, many=True, read_only=True, context=self.context).data

    def get_resourcetype(self, obj):
        return 'TicketConversation'


class TicketConversationCreateSerializer(TicketConversationListSerializer):

    class Meta:
        model = TicketConversation
        fields = TicketConversationListSerializer.Meta.fields + [

        ]
        read_only_fields = TicketConversationListSerializer.Meta.read_only_fields + [

        ]
