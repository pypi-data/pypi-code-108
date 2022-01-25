# -*- coding: utf-8 -*-
import datetime
import re

from rest_framework import filters
from rest_framework import mixins, serializers, viewsets
from rest_framework import permissions
from rest_framework.response import Response

from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend

from notifications.models import UserNotification, Notification

from .serializers import UserNotificationSerializer, UserNotificationPutSerializer, \
    NotificationSerializer


class UserNotificationViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = UserNotification.objects.all()

    permission_classes = (permissions.IsAuthenticated,)

    filter_backends = (filters.SearchFilter, DjangoFilterBackend)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            serializer_class = UserNotificationPutSerializer
        else:
            serializer_class = UserNotificationSerializer
        return serializer_class

    def list(self, request):
        queryset = self.queryset.filter(
            Q(user=self.request.user) &
            (Q(next_display__isnull=True) | Q(next_display__lte=datetime.datetime.now())) &
            (Q(notification__expires__isnull=True) | Q(notification__expires__gte=datetime.datetime.now())) &
            (Q(notification__active_from__isnull=True) | Q(notification__active_from__lt=datetime.datetime.now()))
        ).exclude(answer=True).select_related('notification', 'user').order_by('timestamp', 'id')
        path = request.query_params.get('path', None)
        if path is not None:
            queryset = [
                un for un in queryset
                if re.match(un.notification.display_only_if_url_path_matches_regex, path) is not None
            ]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance.user != request.user:
            raise serializers.ValidationError('User can only change his own usernotifications')
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class NotificationViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Notification.objects.all()

    permission_classes = (permissions.IsAdminUser,)
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)

    serializer_class = NotificationSerializer

    def list(self, request):
        queryset = Notification.objects.filter()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
