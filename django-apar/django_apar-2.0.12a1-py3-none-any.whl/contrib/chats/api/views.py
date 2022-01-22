"""Views for the chat app."""
from django.db.models import F
from django.http import Http404
from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.serializers import as_serializer_error
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework.views import APIView
from rest_framework import filters

from django_filters.rest_framework import DjangoFilterBackend

from .serializers import *
from ..models import ChatSessionTypeEnum


# chat session
class ChatSessionListAPIView(ListAPIView):
    serializer_class = ChatSessionListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filter_fields = ['type', ]

    def get_queryset(self):
        user = self.request.user
        queryset = ChatSession.objects.user_session(user=user).order_by('-message_created_at')
        return queryset


class ChatSessionDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = ChatSessionDetailsSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'uri'
    lookup_field = 'uri'

    def get_queryset(self):
        user = self.request.user
        queryset = ChatSession.objects.user_session(user=user)
        return queryset


class ChatSessionMarkAsReadAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    """
    A view that returns the count of active users in JSON.
    """
    def get(self, request, uri, format=None):

        status = HTTP_400_BAD_REQUEST
        content = {}
        user = request.user

        chat_session = get_object_or_404(ChatSession.objects.all(), uri=uri)

        content['count'] = ChatMessageNotification.objects.mark_as_read_chat_session(user, chat_session)

        status = HTTP_200_OK
        return Response(content, status=status)


# class ChatSessionCreateAPIView(CreateAPIView):
#     serializer_class = ChatSessionDetailsSerializer
#     permission_classes = [permissions.IsAuthenticated]
#
#     def get_queryset(self):
#         return ChatSession.objects.all()
#
#     def perform_create(self, serializer):
#         user = self.request.user
#         serializer.save(owner=user)


class ChatSessionCreateAPIView(APIView):
    """
    Create or fetch a snippet instance.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        owner = request.user
        username_mention = request.POST.get('username_mention', None)
        try:
            user = User.objects.find_by_username_mention(username_mention=username_mention)
        except:
            raise Http404
        type = request.POST.get('type', None)
        if type and int(type) == ChatSessionTypeEnum.PRIVATE:
            chat_session = ChatSession.objects.private(owner, user)
            serializer = ChatSessionDetailsSerializer(chat_session, many=False, read_only=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = ChatSessionDetailsSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                serializer.save(owner=owner)
            except Exception as e:
                raise ValidationError(as_serializer_error(e))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# chat member
class ChatSessionMemberListAPIView(ListAPIView):
    serializer_class = ChatSessionMemberListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_class = []

    def get_queryset(self):
        user = self.request.user
        uri = None
        if 'uri' in self.request.parser_context['kwargs']:
            uri = self.request.parser_context['kwargs']['uri']
        return ChatSessionMember.objects.filter(chat_session__uri=uri)


class ChatSessionMemberDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = ChatSessionMemberDetailsSerializer
    queryset = ChatSessionMember.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'id'
    lookup_field = 'id'
    # TODO: check permission for delete id


# message list
class ChatSessionMessageListAPIView(ListAPIView):
    serializer_class = ChatSessionMessageListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_class = []

    def get_queryset(self):
        user = self.request.user
        uri = None
        if 'uri' in self.request.parser_context['kwargs']:
            uri = self.request.parser_context['kwargs']['uri']
        return ChatSessionMessage.objects.filter(chat_session__uri=uri).order_by('-created_at')


class ChatSessionMessageDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = ChatSessionMessageDetailsSerializer
    queryset = ChatSessionMessage.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'id'
    lookup_field = 'id'
    # TODO: check permission for delete id


class ChatSessionMessageCreateAPIView(CreateAPIView):
    serializer_class = ChatSessionMessageDetailsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        chat_session = None
        if 'uri' in self.request.parser_context['kwargs']:
            uri = self.request.parser_context['kwargs']['uri']
            chat_session = get_object_or_404(ChatSession.objects.all(), uri=uri)
        serializer.save(user=user, chat_session=chat_session)

##
# class ChatSessionMessageView(APIView):
#     """Create/Get Chat session messages."""
#
#     permission_classes = (permissions.IsAuthenticated,)
#
#     def get(self, request, *args, **kwargs):
#         """return all messages in a chat session."""
#         uri = kwargs['uri']
#
#         chat_session = ChatSession.objects.get(uri=uri)
#         messages = [chat_session_message.to_json()
#                     for chat_session_message in chat_session.messages.all()]
#
#         return Response({
#             'id': chat_session.id, 'uri': chat_session.uri,
#             'messages': messages
#         })
#
#     def post(self, request, *args, **kwargs):
#         """create a new message in a chat session."""
#         uri = kwargs['uri']
#         message = request.data['message']
#
#         user = request.user
#         chat_session = ChatSession.objects.get(uri=uri)
#
#         chat_session_message = ChatSessionMessage.objects.create(
#             user=user, chat_session=chat_session, message=message
#         )
#
#         notif_args = {
#             'source': user,
#             'source_display_name': user.get_full_name(),
#             'category': 'chat', 'action': 'Sent',
#             'obj': chat_session_message.id,
#             'short_description': 'You a new message', 'silent': True,
#             'extra_data': {
#                 'uri': chat_session.uri,
#                 'message': chat_session_message.to_json()
#             }
#         }
#         notify.send(
#             sender=self.__class__, **notif_args, channels=['websocket']
#         )
#
#         return Response({
#             'status': 'SUCCESS', 'uri': chat_session.uri, 'message': message,
#             'user': deserialize_user(user)
#         })
