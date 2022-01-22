# -*- coding: utf-8 -*-


from rest_framework import serializers

from ..models import Messaging
from aparnik.contrib.users.api.serializers import UserSummaryListSerializer


# Messaging
class MessagingListSerializer(serializers.ModelSerializer):
    source = serializers.SerializerMethodField()
    recipient = serializers.SerializerMethodField()
    channels = serializers.SerializerMethodField()
    extra_data = serializers.SerializerMethodField()

    class Meta:
        model = Messaging
        fields = [
            'source',
            'source_display_name',
            'uri',
            'recipient',
            'category',
            'action',
            'obj',
            'short_description',
            'channels',
            'is_read',
            'extra_data',
        ]

        read_only_fields = [
            'source',
            'recipient',
            'extra_data',
            'channels',
        ]

    def get_source(self, obj):
        # if obj.source:
        #     return UserSummaryListSerializer(obj.source, many=False, read_only=True, context={'request': })
        return getattr(obj.source, 'username', None)

    def get_recipient(self, obj):
        return getattr(obj.recipient, 'username', None)

    def get_channels(self, obj):
        return obj.channels

    def get_extra_data(self, obj):
        return obj.extra_data