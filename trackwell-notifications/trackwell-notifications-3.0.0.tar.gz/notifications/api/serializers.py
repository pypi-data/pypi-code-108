# -*- coding: utf-8 -*-
from rest_framework import serializers

from notifications.models import Notification, UserNotification


from django.contrib.auth import get_user_model
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', )


class NotificationSerializer(serializers.HyperlinkedModelSerializer):
    regex = serializers.CharField(source='display_only_if_url_path_matches_regex')
    class Meta:
        model = Notification
        fields = ('name', 'message', 'snooze_time', 'snooze_lock', 'look', 'image', 'regex',)


class UserNotificationSerializer(serializers.HyperlinkedModelSerializer):
    notification = NotificationSerializer()
    user = UserSerializer()

    class Meta:
        model = UserNotification
        fields = ('id', 'notification', 'user', 'seen', 'answer')


class UserNotificationPutSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = UserNotification
        fields = ('answer', 'answer_string')
