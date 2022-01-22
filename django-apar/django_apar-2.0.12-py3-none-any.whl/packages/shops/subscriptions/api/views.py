from django.db.models import Q
from rest_framework.permissions import ( AllowAny, IsAuthenticated )
from rest_framework.generics import ListAPIView

from aparnik.contrib.basemodels.api.serializers import ModelListPolymorphicSerializer
from .serializers import SubscriptionOrderListSerializer
from ..models import Subscription, SubscriptionOrder


class SubscriptionListAPIView(ListAPIView):
    serializer_class = ModelListPolymorphicSerializer
    permission_classes = [IsAuthenticated]
    # filter_backends = (filters.SearchFilter,)

    def get_queryset(self, *args, **kwargs):
        if 'product_id' in self.request.query_params:
            product_id = self.request.query_params['product_id']
            return Subscription.objects.active().filter(
                Q(products__in=[product_id]) |
                Q(type=Subscription.TYPE_ALL
                  )
            ).distinct()
        return Subscription.objects.active()


class SubscriptionOrderListAPIView(ListAPIView):
    serializer_class = SubscriptionOrderListSerializer
    permission_classes = [IsAuthenticated]
    # filter_backends = (filters.SearchFilter,)

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        return SubscriptionOrder.objects.mine_history(user=user)


class SubscriptionOrderActiveListAPIView(ListAPIView):
    serializer_class = SubscriptionOrderListSerializer
    permission_classes = [IsAuthenticated]
    # filter_backends = (filters.SearchFilter,)

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        return SubscriptionOrder.objects.mine(user=user)
