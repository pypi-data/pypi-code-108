from django.urls import reverse
from rest_framework import serializers

from aparnik.packages.shops.products.api.serializers import ProductListSerializer, ProductDetailSerializer
from ..models import Subscription, SubscriptionOrder


class SubscriptionListSerializer(ProductListSerializer):

    class Meta:
        model = Subscription
        fields = ProductListSerializer.Meta.fields + [
            'type',
            'duration',
            'description',
        ]


class SubscriptionDetailSerializer(SubscriptionListSerializer, ProductDetailSerializer):

    class Meta:
        model = Subscription
        fields = SubscriptionListSerializer.Meta.fields + ProductDetailSerializer.Meta.fields + [

        ]


# Subscription order
class SubscriptionOrderListSerializer(serializers.ModelSerializer):
    subscription = serializers.SerializerMethodField()

    class Meta:
        model = SubscriptionOrder
        fields = [
            'pk',
            'subscription',
            'expire_at',
            'created_at',
            'update_at',
        ]

    def get_subscription(self, obj):
        return SubscriptionListSerializer(
            obj.subscription_obj,
            many=False,
            read_only=True,
            context=self.context
        ).data
