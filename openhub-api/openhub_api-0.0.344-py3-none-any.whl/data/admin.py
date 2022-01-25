from django.contrib import admin
from data.models.models import Hub, Hardware, Channel, HardwareIO, Accessory, ChannelStats, HardwareConfig, DataTransformer, DataTransformerConstants
# Register your models here.
admin.site.register(Hub)
admin.site.register(Hardware)
admin.site.register(Channel)
admin.site.register(HardwareIO)
admin.site.register(Accessory)
admin.site.register(ChannelStats)
admin.site.register(HardwareConfig)
admin.site.register(DataTransformer)
admin.site.register(DataTransformerConstants)