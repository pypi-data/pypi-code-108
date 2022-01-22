# -*- coding: utf-8 -*-


from rest_framework import serializers

from aparnik.contrib.invitation.models import Invite
from aparnik.settings import aparnik_settings

UserSummaryListSerializer = aparnik_settings.USER_SUMMARY_LIST_SERIALIZER

# Invite
class InviteListSerializer(serializers.ModelSerializer):
    resourcetype = serializers.SerializerMethodField()
    invite = serializers.SerializerMethodField()
    # invited_by = serializers.SerializerMethodField()

    class Meta:
        model = Invite
        fields = (
            'invite',
            # 'invited_by',
            'resourcetype',
            'update_at',

        )

        read_only_fields = [
            'resourcetype',
        ]

    def get_invite(self, obj):
        return UserSummaryListSerializer(obj.invite, read_only=False, context=self.context).data

    def get_resourcetype(self, obj):
        return 'Invite'

    # def get_invited_by(self, obj):
    #     return UserDetailSerializer(obj.invited_by, read_only=False, context=self.context).data

class InviteDetailSerializer(serializers.ModelSerializer):

    invite = serializers.SerializerMethodField()
    # invited_by = serializers.SerializerMethodField()

    class Meta:
        model = Invite
        fields = (
            'invite',
            # 'invited_by',
            'update_at',
        )

        def get_invite(self, obj):
            return UserDetailSerializer(obj.invite, read_only=False, context=self.context).data

        # def get_invited_by(self, obj):
        #     return UserDetailSerializer(obj.invited_by, read_only=False, context=self.context).data
