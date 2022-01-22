# -*- coding: utf-8 -*-


from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework.permissions import (AllowAny, IsAuthenticated)
from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView, ListAPIView

from aparnik.contrib.basemodels.api.views import BaseModelSortAPIView
from .serializers import TicketListSerializer, TicketConversationListSerializer, TicketCreateSerializer, TicketConversationCreateSerializer
from ..models import Ticket, TicketConversation


class TicketSortAPIView(BaseModelSortAPIView):
    permission_classes = [AllowAny]

    """
        A view that returns the count of active users in JSON.
        """
    def __init__(self, *args, **kwargs):
        super(TicketSortAPIView, self).__init__(*args, **kwargs)
        command_dict = {

        }

        self.command_dict.update(command_dict)


class TicketListAPIView(ListAPIView):
    serializer_class = TicketListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # queryset = Product.objects.active(user=user)
        queryset = None
        if user.is_superuser:
            queryset = Ticket.objects.active(user=user)
        else:
            queryset = Ticket.objects.this_user(user=user)
        sort_api = TicketSortAPIView(request=self.request)
        queryset = sort_api.get_query_sort(queryset)
        return queryset


class TicketCreateAPIView(CreateAPIView):
    serializer_class = TicketCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user_obj=user)


class TicketConversationListAPIView(ListAPIView):
    serializer_class = TicketConversationListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        ticket = get_object_or_404(Ticket, pk=self.request.parser_context['kwargs']['ticket_id'])
        queryset = ticket.ticketconversation_set.all()
        return queryset


class TicketConversationCreateAPIView(CreateAPIView):
    serializer_class = TicketConversationCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer, *args, **kwargs):
        ticket = get_object_or_404(Ticket, pk=self.request.parser_context['kwargs']['ticket_id'])
        user = self.request.user
        files = self.request.data.get('files', None)
        if files:
            files = files.split(',')
        dict = {
            'user_obj': user,
            'files_obj': [],
            'ticket_obj': ticket,
        }
        if files:
            dict['files_obj'] = files
        serializer.save(**dict)
