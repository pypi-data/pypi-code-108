import mptt
from django.db import models
import uuid
from django.utils import timezone
import time
from polymorphic.models import PolymorphicModel
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth.models import User

class Hub(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True, blank=True)
    ip = models.URLField()
    category = models.CharField(max_length=255, null=True)
    type = models.CharField(max_length=255, null=True)
    display_name = models.CharField(max_length=255, null=True)
    aid = models.IntegerField()

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['id']),
        ]


class Hardware(PolymorphicModel):
    class Type(models.TextChoices):
        DHT22 = 'DHT22'
        MCP3008 = 'MCP3008'
        ModProbe = 'ModProbe'
        PiPico = 'PiPico'
        Pi = 'Pi'
        VEML7700 = 'VEML7700'
        PMSA0031 = 'PMSA0031'
        AM2315 = 'AM2315'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True, blank=True)

    type = models.CharField(
        max_length=10,
        choices=Type.choices,
        default=Type.PiPico,
    )

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    hub = models.ForeignKey(Hub, on_delete=models.CASCADE, null=False)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()

        return super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['id']),
        ]

class Pi(Hardware):
    def __init__(self,*args, **kwargs):
        super(Hardware,self).__init__(*args, **kwargs)

class PiPico(Hardware):
    serial_com = models.CharField(max_length=100, null=True)
    pi_gpio_interrupt = models.IntegerField()


class DHT22(Hardware):
    pin = models.IntegerField()


class MCP3008(Hardware):
    sck = models.IntegerField()
    miso = models.IntegerField()
    cs_pin = models.IntegerField()
    num_channels = models.IntegerField()


class ModProbe(Hardware):
    base_dir = models.CharField(max_length=100, null=True)
    file_name = models.CharField(max_length=100, null=True)


class VEML7700(Hardware):
    scl = models.IntegerField()
    sda = models.IntegerField()


class PMSA0031(Hardware):
    scl = models.IntegerField()
    sda = models.IntegerField()
    reset = models.IntegerField()

class AM2315(Hardware):
    scl = models.IntegerField()
    sda = models.IntegerField()

class HardwareChannelTypes(models.Model):
    hardware_type = models.CharField(
        max_length=25
    )
    channel_type = models.CharField(
        max_length=25
    )


class Channel(models.Model):
    def __str__(self):
        return self.get_name_display()

    def get_name_display(self):
        name = ''
        if self.nickname is not None and self.nickname != '':
            name = self.nickname
        else:
            if self.hardware is not None:
                name = name + self.hardware.type + ' / '
                name = name + self.type + ' / ' + str(self.channel_index) + ' / ' + str(self.id)
        return name

    class Type(models.TextChoices):
        DHT22Humidity = 'DHT22Humidity'
        DHT22Temp = 'DHT22Temp'
        MCP3008Analog = 'MCP3008Analog'
        ModProbeTemp = 'ModProbeTemp'
        PiPicoACAnalog = 'PiPicoACAnalog'
        PiPicoAnalog = 'PiPicoAnalog'
        PiPicoPump = 'PiPicoPump'
        PiPicoRelay = 'PiPicoRelay'
        VEML7700Light = 'VEML7700Light'
        VEML7700Lux = 'VEML7700Lux'
        PiRelay = 'PiRelay'
        AM2315Humidity = 'AM2315Humidity'
        AM2315Temperature = 'AM2315Temperature'
        PMSA003125 = 'PMSA003125'
        PMSA0031100 = 'PMSA0031100'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True, blank=True)
    channel_index = models.IntegerField(null=True)
    type = models.CharField(
        max_length=25
    )
    nickname = models.CharField(
        max_length=100,
        default=None,
        blank=True,
        null=True
    )
    hardware = models.ForeignKey(Hardware, on_delete=models.CASCADE, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    hub = models.ForeignKey(Hub, on_delete=models.CASCADE, null=False)
    keep_statistics = models.BooleanField(null=True, blank=True, default=False)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()

        return super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['id', 'hardware']),
        ]


class HardwareIO(PolymorphicModel):
    SPI = 'SPI'
    Serial = 'Serial'
    PWM = 'PWM'
    I2C = 'I2C'
    DeviceFile = 'Device File'
    MCPChannel = 'MCP Channel'
    PiPicoACAnalog = 'Pi Pico AC Analog'
    PiPicoAnalog = 'Pi Pico Analog'
    PiGPIO = 'Pi GPIO'
    hardware_io_types_choices = [(SPI, SPI), (Serial, Serial), (PWM, PWM), (I2C, I2C), (DeviceFile, DeviceFile),
                                 (MCPChannel, MCPChannel), (PiPicoAnalog, PiPicoAnalog),
                                 (PiPicoACAnalog, PiPicoACAnalog), (PiGPIO, PiGPIO)]

    label = models.CharField(max_length=255, null=True)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True, blank=True)

    parent_hardware = models.ForeignKey(Hardware, on_delete=models.CASCADE, blank=True, null=True,
                                        related_name="%(app_label)s_%(class)s_related",
                                        related_query_name="%(app_label)s_%(class)ss")
    child_hardware = models.ForeignKey(Hardware, on_delete=models.CASCADE, blank=True, null=True)
    child_channel = models.ForeignKey(Channel, on_delete=models.CASCADE, blank=True, null=True)
    type = models.CharField(max_length=25, choices=hardware_io_types_choices, default=PiPicoAnalog)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    hub = models.ForeignKey(Hub, on_delete=models.CASCADE, null=False)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()

        return super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['id', 'parent_hardware', 'child_channel']),
        ]


class PiPins(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    hardware_io = models.ForeignKey(HardwareIO, on_delete=models.CASCADE, blank=True, null=True)
    pin = models.IntegerField()

    class Meta:
        indexes = [
            models.Index(fields=['hardware_io']),
        ]


class SPIIo(HardwareIO):
    sck = models.IntegerField()
    miso = models.IntegerField()
    mosi = models.IntegerField()


class SerialIo(HardwareIO):
    port = models.CharField(max_length=100)


class PwmIo(HardwareIO):
    en = models.IntegerField()
    duty_max = models.IntegerField()
    duty_min = models.IntegerField()
    freq = models.IntegerField()


class I2cIo(HardwareIO):
    scl = models.IntegerField()
    sda = models.IntegerField()


class DeviceFileIo(HardwareIO):
    base_dir = models.CharField(max_length=100, null=True)
    device_file = models.CharField(max_length=100, null=True)


class MCPAnalogIo(HardwareIO):
    channel_index = models.IntegerField()


class PiPicoAnalogIo(HardwareIO):
    pin = models.IntegerField()


class PiPicoACAnalogIo(HardwareIO):
    pin = models.IntegerField()


class PiGpio(HardwareIO):
    pin = models.IntegerField()


class Accessory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True, blank=True)

    hub = models.ForeignKey(Hub, on_delete=models.CASCADE, null=False)

    category = models.CharField(max_length=255, null=True)
    type = models.CharField(max_length=255, null=True)
    display_name = models.CharField(max_length=255, null=True)
    aid = models.IntegerField()
    channels = models.ManyToManyField(Channel)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super().save(*args, **kwargs)

    @property
    def has_data_transformer(self):
        return self.datatransformer_set.count() > 0

    @property
    def datatransformer(self):
        try:
            return self.datatransformer_set.first().get_root()
        except:
            print('datatransformer error sorta')
        return self.datatransformer_set.first()


    class Meta:
        indexes = [
            models.Index(fields=['id']),
        ]


class HardwareConfig(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True, blank=True)
    type = models.CharField(max_length=255, null=True)
    value = models.CharField(max_length=255, null=True)
    hardware = models.ForeignKey(Hardware, on_delete=models.CASCADE, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()

        return super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['id', 'hardware']),
        ]


class ChannelStats(models.Model):
    def get_name_display(self):
        name = self.channel.get_name_display() + ' / ' + self.type
        return name

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True, blank=True)

    channel = models.ForeignKey(Channel,on_delete=models.CASCADE,blank=True, null=True, default=None)

    MIN = 'MIN'
    MAX = 'MAX'
    stats_choices = ((MIN, MIN), (MAX, MAX))
    type = models.CharField(max_length=25, choices=stats_choices, default=MIN)
    value = models.FloatField(null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()

        return super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['id']),
        ]


class DataTransformerTypes(models.Model):
    def get_name_display(self):
        return self.type

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    type = models.CharField(
        max_length=15, blank=True, null=True, default=None
    )

    def __str__(self):
        return str(self.type)

class DataTransformer(MPTTModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True, blank=True)

    accessory = models.ForeignKey(
        Accessory,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    channels = models.ManyToManyField(Channel, blank=True, null=True)
    channel_stats = models.ManyToManyField(ChannelStats,blank=True, null=True)

    type = models.ForeignKey(DataTransformerTypes,on_delete=models.DO_NOTHING,blank=True, null=True, default=None)

    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    updated_at = models.DateTimeField(blank=True,auto_now=True)
    created_at = models.DateTimeField(blank=True,auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()

        return super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['id', 'accessory']),
        ]

    class MPTTMeta:
        order_insertion_by = ['id']


class DataTransformerConstants(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,blank=True,null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True, blank=True)

    data_transformer = models.ForeignKey(DataTransformer, related_name='data_transformer_constants', on_delete=models.CASCADE, blank=False, null=False)
    index = models.IntegerField(blank=True, null=True, default=None)
    value = models.FloatField(blank=False,null=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()

        return super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['id', 'data_transformer']),
        ]


class Calibration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    type = models.CharField(max_length=255, null=True)
    accessory = models.ForeignKey(Accessory, on_delete=models.CASCADE, blank=True, null=True, default=None)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()

        return super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['id'])
        ]


class CalibrationConstants(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    type = models.CharField(max_length=255, null=True)
    value = models.CharField(max_length=255, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    calibration = models.ForeignKey(Calibration, on_delete=models.CASCADE, blank=True, null=False)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()

        return super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['id']),
        ]


class Category(models.Model):
    name = models.CharField(max_length=255, null=True)
    enum = models.IntegerField(null=True)


class AccessoryType(models.Model):
    type = models.CharField(max_length=255, null=True)
