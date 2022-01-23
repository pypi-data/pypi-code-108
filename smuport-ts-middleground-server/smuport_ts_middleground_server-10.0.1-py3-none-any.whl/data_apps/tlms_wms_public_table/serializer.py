from .import models
from rest_framework import serializers


class CargoSerializer(serializers.ModelSerializer):
    image_path = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    # cargo_type = CargoTypeSerializer(read_only=True)
    # cargo_type_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = models.Cargo
        fields = "__all__"


class ConsignorSerializer(serializers.ModelSerializer):
    """
    委托公司序列化
    """
    class Meta:
        model = models.Consignor
        fields = "__all__"


class DecMethodSerializer(serializers.ModelSerializer):
    """
    申报方式
    """
    class Meta:
        model = models.DecMethod
        fields = "__all__"


class WorkRouteSerializer(serializers.ModelSerializer):
    """
    作业路线
    """
    class Meta:
        model = models.WorkRoute
        fields = "__all__"


class CtnSizeSerializer(serializers.ModelSerializer):
    """
    箱尺寸
    """
    class Meta:
        model = models.CtnSize
        fields = "__all__"


class CtnTypeSerializer(serializers.ModelSerializer):
    """
    箱类型
    """
    class Meta:
        model = models.CtnType
        fields = "__all__"


class SupplierSerializer(serializers.ModelSerializer):
    """
    供应商
    """
    class Meta:
        model = models.Supplier
        fields = "__all__"


class UnPackTypeSerializer(serializers.ModelSerializer):
    """
    装卸方式
    """
    class Meta:
        model = models.UnPackType
        fields = "__all__"


class ForkliftSerializer(serializers.ModelSerializer):
    """
    叉车车辆
    """
    class Meta:
        model = models.Forklift
        fields = "__all__"


class TransModeSerializer(serializers.ModelSerializer):
    """
    成交方式
    """
    class Meta:
        model = models.TransMode
        fields = "__all__"


class CurrencySerializer(serializers.ModelSerializer):
    """
    币制表
    """
    class Meta:
        model = models.Currency
        fields = "__all__"


class TransportModeSerializer(serializers.ModelSerializer):
    """
    运输方式
    """
    class Meta:
        model = models.TransportMode
        fields = "__all__"


class CustomsModeSerializer(serializers.ModelSerializer):
    """
    关区表
    """
    class Meta:
        model = models.CustomsMode
        fields = "__all__"


class DomesticDestinationSerializer(serializers.ModelSerializer):
    """
    境内目的地
    """
    class Meta:
        model = models.DomesticDestination
        fields = "__all__"


class CountrySerializer(serializers.ModelSerializer):
    """
    国家地区代码
    """
    class Meta:
        model = models.Country
        fields = "__all__"


class MeasureSerializer(serializers.ModelSerializer):
    """
    计量单位
    """
    class Meta:
        model = models.Measure
        fields = "__all__"


class TradeModeSerializer(serializers.ModelSerializer):
    """
    贸易方式
    """
    class Meta:
        model = models.TradeMode
        fields = "__all__"
