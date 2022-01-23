from .import models
from rest_framework import serializers

from ..tlms_wms_public_table.serializer import ConsignorSerializer, DecMethodSerializer, WorkRouteSerializer, \
    CargoSerializer, CtnSizeSerializer, CtnTypeSerializer


class EntDirectSerializer(serializers.ModelSerializer):
    """
    委托业务
    """
    consignor = ConsignorSerializer(many=False, read_only=True)

    class Meta:
        model = models.TlmsWmsEntDirect
        fields = "__all__"


class TlmsWmsEntDirectSerializer(serializers.ModelSerializer):
    consignor = ConsignorSerializer(many=False, read_only=True)
    # dec_method = DecMethodSerializer(many=False, read_only=True)
    # work_route = WorkRouteSerializer(many=False, read_only=True)
    ctn_cargo = serializers.SerializerMethodField()

    def get_ctn_cargo(self, obj):
        entrust_ctn_cargoes = models.TlmsWmsCtnDetail.objects.filter(ent_direct_id=obj.id)
        res = TlmsWmsCtnDetailSerializer(instance=entrust_ctn_cargoes, many=True)
        return res.data

    class Meta:
        model = models.TlmsWmsEntDirect
        fields = "__all__"


class TlmsWMSEntDetailsSerializer(serializers.ModelSerializer):
    """
    委托业务货物明细
    """
    ent_direct = EntDirectSerializer(many=False, read_only=True)
    ent_direct_id = serializers.CharField(write_only=True)
    cargo = CargoSerializer(many=False, read_only=True)
    cargo_id = serializers.CharField(write_only=True)

    class Meta:
        model = models.TlmsWmsEntDetails
        fields = "__all__"


class TlmsWMSEntCtnSerializer(serializers.ModelSerializer):
    """
    委托业务箱子明细
    """
    ent_direct = EntDirectSerializer(many=False, read_only=True)
    ent_direct_id = serializers.CharField(write_only=True)
    ctn_size = CtnSizeSerializer(many=False, read_only=True)
    ctn_size_id = serializers.CharField(write_only=True)
    ctn_type = CtnTypeSerializer(many=False, read_only=True)
    ctn_type_id = serializers.CharField(write_only=True)

    class Meta:
        model = models.TlmsWmsEntCtn
        fields = "__all__"


class TlmsWmsCtnDetailSerializer(serializers.ModelSerializer):
    """
    箱子-货物关系
    """
    ent_direct_ctn = TlmsWMSEntCtnSerializer(many=False, read_only=True)
    ent_direct_ctn_id = serializers.CharField(write_only=True, allow_blank=True, required=False)
    ent_direct_detail = TlmsWMSEntDetailsSerializer(many=False, read_only=True)
    ent_direct_detail_id = serializers.CharField(write_only=True)

    class Meta:
        model = models.TlmsWmsCtnDetail
        fields = "__all__"

