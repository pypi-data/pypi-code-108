from rest_framework import serializers

from data.models.models import CalibrationConstants, Calibration, Channel, Accessory, HardwareConfig, PiPico, \
    DHT22, MCP3008, ModProbe, VEML7700, Hardware, Hub, SPIIo, SerialIo, PwmIo, I2cIo, DeviceFileIo, MCPAnalogIo, \
    PiPicoAnalogIo, PiPicoACAnalogIo, PiGpio, DataTransformer,DataTransformerConstants,DataTransformerTypes,ChannelStats

class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data

class CalibrationConstantsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalibrationConstants
        fields = ['id', 'type', 'value']


class HubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hub
        fields = '__all__'


class CalibrationSerializer(serializers.ModelSerializer):
    calibration_constants = CalibrationConstantsSerializer(source='calibrationconstants_set', many=True,
                                                           read_only=False)

    class Meta:
        model = Calibration
        fields = ['id', 'type', 'calibration_constants']

class ChannelStatsSerializer(serializers.ModelSerializer):
    channel = serializers.PrimaryKeyRelatedField(read_only=True)
    model = serializers.SerializerMethodField()

    def get_model(self, instance):
        try:
            return instance.__class__.__name__
        except:
            return None
    class Meta:
        model = ChannelStats
        fields = ['id', 'channel', 'type', 'value','model']

class ChannelSerializer(serializers.ModelSerializer):
    channelstats_set = ChannelStatsSerializer(read_only=True,many=True, required=False)
    model = serializers.SerializerMethodField()


    def get_model(self, instance):
        try:
            return instance.__class__.__name__
        except:
            return None

    class Meta:
        model = Channel
        fields = ['id', 'type', 'channel_index', 'hardware','channelstats_set','model','keep_statistics']





class DataTransformerSerializer(serializers.ModelSerializer):
    children = RecursiveField(many=True)
    model = serializers.SerializerMethodField()

    def get_model(self, instance):
        try:
            return instance.__class__.__name__
        except:
            return None

    class Meta:
        model = DataTransformer
        fields = '__all__'


class HardwareConfigSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HardwareConfig
        fields = ['id', 'type', 'value']


class PiPicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PiPico
        fields = '__all__'


class DHT22Serializer(serializers.ModelSerializer):
    class Meta:
        model = DHT22
        fields = '__all__'


class MCP3008Serializer(serializers.ModelSerializer):
    class Meta:
        model = MCP3008
        fields = '__all__'


class ModProbeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModProbe
        fields = '__all__'


class VEML7700Serializer(serializers.ModelSerializer):
    class Meta:
        model = VEML7700
        fields = '__all__'


class HardwareSerializer(serializers.ModelSerializer):
    model = serializers.SerializerMethodField()

    def get_model(self, instance):
        try:
            return instance.__class__.__name__
        except:
            return None

    def to_json_array(self, obt_list):
        serialized_hardware = []
        for obj in obt_list:
            serialized_hardware.append(self.to_representation(obj))
        return serialized_hardware

    def to_representation(self, obj):
        """
        Because GalleryItem is Polymorphic
        """
        if isinstance(obj, PiPico):
            return PiPicoSerializer(obj, context=self.context).to_representation(obj)
        elif isinstance(obj, DHT22):
            return DHT22Serializer(obj, context=self.context).to_representation(obj)
        elif isinstance(obj, MCP3008):
            return MCP3008Serializer(obj, context=self.context).to_representation(obj)
        elif isinstance(obj, ModProbe):
            return ModProbeSerializer(obj, context=self.context).to_representation(obj)
        elif isinstance(obj, VEML7700):
            return VEML7700Serializer(obj, context=self.context).to_representation(obj)
        return super(HardwareSerializer, self).to_representation(obj)

    class Meta:
        model = Hardware
        fields = '__all__'


class SPIIoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SPIIo
        fields = '__all__'


class SerialIoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SerialIo
        fields = '__all__'


class PwmIoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PwmIo
        fields = '__all__'


class I2cIoSerializer(serializers.ModelSerializer):
    class Meta:
        model = I2cIo
        fields = '__all__'


class DeviceFileIoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceFileIo
        fields = '__all__'


class MCPAnalogIoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MCPAnalogIo
        fields = '__all__'


class PiPicoAnalogIoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PiPicoAnalogIo
        fields = '__all__'


class PiPicoACAnalogIoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PiPicoACAnalogIo
        fields = '__all__'


class PiGpioSerializer(serializers.ModelSerializer):
    class Meta:
        model = PiGpio
        fields = '__all__'


class HardwareIOSerializer(serializers.ModelSerializer):

    def to_json_array(self, obt_list):
        serialized_hardware = []
        for obj in obt_list:
            serialized_hardware.append(self.to_representation(obj))
        return serialized_hardware

    def to_representation(self, obj):
        """
        Because GalleryItem is Polymorphic
        """
        if isinstance(obj, SPIIo):
            return SPIIoSerializer(obj, context=self.context).to_representation(obj)
        elif isinstance(obj, SerialIo):
            return SerialIoSerializer(obj, context=self.context).to_representation(obj)
        elif isinstance(obj, PwmIo):
            return PwmIoSerializer(obj, context=self.context).to_representation(obj)
        elif isinstance(obj, I2cIo):
            return I2cIoSerializer(obj, context=self.context).to_representation(obj)
        elif isinstance(obj, DeviceFileIo):
            return DeviceFileIoSerializer(obj, context=self.context).to_representation(obj)
        elif isinstance(obj, MCPAnalogIo):
            return MCPAnalogIoSerializer(obj, context=self.context).to_representation(obj)

        elif isinstance(obj, PiPicoAnalogIo):
            return PiPicoAnalogIoSerializer(obj, context=self.context).to_representation(obj)
        elif isinstance(obj, PiPicoACAnalogIo):
            return PiPicoACAnalogIoSerializer(obj, context=self.context).to_representation(obj)
        elif isinstance(obj, PiGpio):
            return PiGpioSerializer(obj, context=self.context).to_representation(obj)

        return super(HardwareIOSerializer, self).to_representation(obj)

    class Meta:
        model = Hardware
        fields = '__all__'


class DataTransformerConstantsSerializer(serializers.ModelSerializer):
    data_transformer = serializers.PrimaryKeyRelatedField(read_only=True)
    model = serializers.SerializerMethodField()

    def get_model(self, instance):
        try:
            return instance.__class__.__name__
        except:
            return None

    class Meta:
        model = DataTransformerConstants
        fields = '__all__'

class DataTransformerTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model=DataTransformerTypes
        fields = ['type']  # add here rest of the fields from model


class DataTransformerTreeSerializer(serializers.ModelSerializer):
    data_transformer_constants = DataTransformerConstantsSerializer(read_only=True,many=True)
    channels = serializers.PrimaryKeyRelatedField(read_only=True,many=True)
    channel_stats = serializers.PrimaryKeyRelatedField(read_only=True,many=True)
    accessory = serializers.PrimaryKeyRelatedField(read_only=True)
    type = serializers.StringRelatedField(many=False)

    children = serializers.SerializerMethodField(source='get_children')
    model = serializers.SerializerMethodField()

    def get_model(self, instance):
        try:
            return instance.__class__.__name__
        except:
            return None

    class Meta:
        model=DataTransformer
        fields = '__all__'  # add here rest of the fields from model

    def get_children(self, obj):
        print(str(self.context))
        if 'children' in self.context.keys():
            children = self.context['children'].get(obj.id, [])
            serializer = DataTransformerTreeSerializer(children, many=True, context=self.context)
            return serializer.data
        else:
            return None



class AccessorySerializer(serializers.ModelSerializer):
    # channels = ChannelSerializer(source='channel_set', many=True)
    calibration = CalibrationSerializer(source='calibration_set', many=True, read_only=False)
    datatransformer = DataTransformerTreeSerializer(read_only=True)
    model = serializers.SerializerMethodField()

    def get_model(self, instance):
        try:
            return instance.__class__.__name__
        except:
            return None

    class Meta:
        model = Accessory
        fields = ['id', 'category', 'type', 'display_name', 'aid',
                  'calibration', 'channels','datatransformer','model']