import json
from collections import defaultdict

from django.core import serializers as django_serializers
from django.forms import formset_factory, inlineformset_factory
from django.http import JsonResponse, HttpResponse, QueryDict
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from polymorphic.models import PolymorphicTypeInvalid
from rest_framework import viewsets, renderers
from rest_framework.decorators import renderer_classes, api_view
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response

from data.forms.forms import HardwareForm, HardwareDHT22Form, HardwareMCP3008Form, HardwareModProbeForm, \
    HardwarePiPicoForm, HardwareVEML7700Form, HardwareTypeForm, ChannelForm, HardwareConfigForm, AccessoryForm, \
    CalibrationForm, CalibrationConstantForm, HubForm, HardwareIOTypeForm, SPIIoForm, PwmIoForm, SerialIoForm, \
    I2cIoForm, DeviceFileIoForm, MCPAnalogIoForm, PiPicoACAnalogIoForm, PiPicoAnalogIoForm, PiGpioForm, HardwareIoForm, \
    HardwarePMSA0031Form,ChannelStatsForm,HardwarePiForm,HardwareAM2315Form
from data.models.models import Hardware, DHT22, MCP3008, ModProbe, PiPico, VEML7700, Accessory, Calibration, \
    CalibrationConstants, Channel, Hub, HardwareIO, ChannelStats, PMSA0031, AM2315
from data.serializers.serializers import HardwareSerializer, ChannelSerializer, AccessorySerializer, \
    CalibrationSerializer, HubSerializer, HardwareIOSerializer, ChannelStatsSerializer

SPI = 'SPI'
Serial = 'Serial'
PWM = 'PWM'
I2C = 'I2C'
DeviceFile = 'Device File'
MCPChannel = 'MCP Channel'
PiPicoAnalog = 'Pi Pico Analog'
PiPicoACAnalog = 'Pi Pico AC Analog'
PiGPIO = 'Pi GPIO'


class HardwareViewSet(viewsets.ModelViewSet):
    queryset = Hardware.objects.all()
    serializer_class = HardwareSerializer
    renderer_classes = (renderers.JSONRenderer, renderers.TemplateHTMLRenderer)

    def updateHardware(request):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "user not authenticated"}, status=400)
        if request.is_ajax and request.method == "POST":
            # get the form data
            hardware = Hardware.objects.get(pk=request.POST['initial-id'])

            form = HardwareForm(data=request.POST, instance=hardware)
            hardware_type = form.data['type']
            if hardware_type == 'DHT22':
                form = HardwareDHT22Form(data=request.POST, instance=hardware)
            if hardware_type == 'MCP3008':
                form = HardwareMCP3008Form(data=request.POST, instance=hardware)
            if hardware_type == 'ModProbe':
                form = HardwareModProbeForm(data=request.POST, instance=hardware)
            if hardware_type == 'PiPico':
                form = HardwarePiPicoForm(data=request.POST, instance=hardware)
            if hardware_type == 'Pi':
                form = HardwarePiForm(data=request.POST, instance=hardware)
            if hardware_type == 'VEML7700':
                form = HardwareVEML7700Form(data=request.POST, instance=hardware)
            if hardware_type == 'PMSA0031':
                form = HardwarePMSA0031Form(data=request.POST, instance=hardware)
            if hardware_type == 'AM2315':
                form = HardwareAM2315Form(data=request.POST, instance=hardware)
            # save the data and after fetch the object in instance
            if form.is_valid():
                instance = form.save()
                instance.user = request.user
                instance.save()
                print(str(instance))
                # serialize in new friend object in json
                ser_instance = django_serializers.serialize('json', [instance, ])
                print(str(ser_instance))
                # send to client side.
                return JsonResponse({"instance": ser_instance}, status=200)

    def getHardwareTypeForm(request):
        form = HardwareTypeForm(request.POST)
        hardware_type = form.data['type']
        if hardware_type == 'DHT22':
            form = HardwareDHT22Form(initial={'type': 'DHT22', "user":request.user})
        if hardware_type == 'MCP3008':
            form = HardwareMCP3008Form(initial={'type': 'MCP3008', "user":request.user})
        if hardware_type == 'ModProbe':
            form = HardwareModProbeForm(initial={'type': 'ModProbe', "user":request.user})
        if hardware_type == 'PiPico':
            form = HardwarePiPicoForm(initial={'type': 'PiPico', "user":request.user})
        if hardware_type == 'Pi':
            form = HardwarePiForm(initial={'type': 'Pi', "user":request.user})
        if hardware_type == 'VEML7700':
            form = HardwareVEML7700Form(initial={'type': 'VEML7700', "user":request.user})
        if hardware_type == 'PMSA0031':
            form = HardwarePMSA0031Form(initial={'type': 'PMSA0031', "user":request.user})
        if hardware_type == 'AM2315':
            form = HardwareAM2315Form(initial={'type': 'AM2315', "user":request.user})
        return HttpResponse(form.as_p())

    def getHardwareIoForm(request):
        form = HardwareIOTypeForm(request.POST)
        hardware_io_type = form.data['type']
        initial = {}
        if 'parent_hardware' in form.data.keys():
            initial['parent_hardware'] = form.data['parent_hardware']
        if 'child_hardware' in form.data.keys():
            initial['child_hardware'] = form.data['child_hardware']
        if 'child_channel' in form.data.keys():
            initial['child_channel'] = form.data['child_channel']
        if 'child_channel' in form.data.keys():
            initial['hub'] = form.data['hub']
        if 'type' in form.data.keys():
            initial['type'] = form.data['type']

        if hardware_io_type == SPI:
            form = SPIIoForm(initial=initial)
            form.type = SPI

        if hardware_io_type == PWM:
            form = PwmIoForm(initial=initial)
            form.type = PWM

        if hardware_io_type == Serial:
            form = SerialIoForm(initial=initial)
            form.type = Serial

        if hardware_io_type == I2C:
            form = I2cIoForm(initial=initial)
            form.type = I2C

        if hardware_io_type == DeviceFile:
            form = DeviceFileIoForm(initial=initial)
            form.type = DeviceFile

        if hardware_io_type == MCPChannel:
            form = MCPAnalogIoForm(initial=initial)
            form.type = MCPChannel

        if hardware_io_type == PiPicoAnalog:
            form = PiPicoAnalogIoForm(initial=initial)
            form.type = PiPicoAnalog

        if hardware_io_type == PiPicoACAnalog:
            form = PiPicoACAnalogIoForm(initial=initial)
            form.type = PiPicoACAnalog

        if hardware_io_type == PiGPIO:
            form = PiGpioForm(initial=initial)
            form.type = PiGPIO

        return HttpResponse(form.as_p())

    def list(self, request, *args, **kwargs):
        print("list")

        response = super(HardwareViewSet, self).list(request, *args, **kwargs)
        form_type = HardwareTypeForm(initial={'type': 'PiPico'})
        hardware_form = HardwarePiPicoForm(initial={'type': 'PiPico'})
        hardware = Hardware.objects.all()

        serialized_hardware = HardwareSerializer().to_json_array(hardware)
        if request.accepted_renderer.format == 'html':
            return Response({"form": hardware_form, "type_form": form_type, "hardwares": hardware},
                            template_name='hardwares.html')
            # return Response({"hardwares": hardware}, template_name='hardwares.html')
        return response

    def getChannels(self, hardware_id):
        channels = Hardware.objects.get(pk=str(hardware_id)).channel_set.all()
        serialized_channels = []
        for channel in channels:
            serialized_channels.append(ChannelSerializer(channel).data)
        # if request.accepted_renderer.format == 'html':
        print('get channels '+ str(hardware_id))
        print(str(serialized_channels))
        return JsonResponse(serialized_channels, status=200, safe=False)

    # def getChannels(self, hardware_id):
    #     channels = Hardware.objects.get(pk=str(hardware_id)).channel_set.all()
    #     for channel in channels:
    #         channel.channelstat_set.all()
    #
    #     serialized_channels = ChannelSerializer(channels,many=True).data
    #
    #     # if request.accepted_renderer.format == 'html':
    #     return JsonResponse(serialized_channels, status=200, safe=False)

    def getConfig(self, hardware_id):
        hardware_configs = Hardware.objects.get(pk=str(hardware_id)).hardwareconfig_set.all()
        config = {}
        for hardware_config in hardware_configs:
            config[hardware_config.type] = hardware_config.value
        # if request.accepted_renderer.format == 'html':
        return JsonResponse({"config": config}, status=200)

    def indexView(request):
        print("indexView")
        form = HardwareForm()
        hardware = Hardware.objects.all()
        return render(request, "hardwares.html", {"form": form, "hardware": hardware})

    SPI = 'SPI'
    Serial = 'Serial'
    PWM = 'PWM'
    I2C = 'I2C'
    DeviceFile = 'Device File'
    MCPChannel = 'MCP Channel'
    PiPicoAnalog = 'Pi Pico Analog'
    PiPicoACAnalog = 'Pi Pico AC Analog'
    PiGPIO = 'Pi GPIO'

    def postHardwareIO(request):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "user not authenticated"}, status=400)
        # request should be ajax and method should be POST.
        if request.is_ajax and request.method == "POST":
            # get the form data

            hardware_io_form = HardwareIoForm(request.POST)
            hardware_io_type = hardware_io_form.data['type']
            if hardware_io_type == SPI:
                hardware_form = SPIIoForm(request.POST)
            if hardware_io_type == Serial:
                hardware_form = SerialIoForm(request.POST)
            if hardware_io_type == PWM:
                hardware_form = PwmIoForm(request.POST)
            if hardware_io_type == I2C:
                hardware_form = I2cIoForm(request.POST)
            if hardware_io_type == DeviceFile:
                hardware_form = DeviceFileIoForm(request.POST)
            if hardware_io_type == MCPChannel:
                hardware_form = MCPAnalogIoForm(request.POST)
            if hardware_io_type == PiPicoAnalog:
                hardware_form = PiPicoAnalogIoForm(request.POST)
            if hardware_io_type == PiPicoACAnalog:
                hardware_form = PiPicoACAnalogIoForm(request.POST)
            if hardware_io_type == PiGPIO:
                hardware_form = PiGpioForm(request.POST)
            # save the data and after fetch the object in instance
            if hardware_form.is_valid():
                instance = hardware_form.save()
                instance.user = request.user;
                instance.save()
                # serialize in new friend object in json
                ser_instance = django_serializers.serialize('json', [instance, ])
                # send to client side.
                return JsonResponse({"instance": ser_instance}, status=200)
            else:
                # some form errors occured.
                return JsonResponse({"error": hardware_form.errors}, status=400)

        # some error occured
        return JsonResponse({"error": ""}, status=400)

    def postHardware(request):

        # request should be ajax and method should be POST.
        if request.is_ajax() and request.method == "POST":
            if not request.user.is_authenticated:
                return JsonResponse({"error": "user not authenticated"}, status=400)
            # get the form data
            hardware_form = HardwareForm(request.POST)
            hardware_type = request.POST['type']
            if hardware_type == 'DHT22':
                hardware_form = HardwareDHT22Form(request.POST)
            if hardware_type == 'MCP3008':
                hardware_form = HardwareMCP3008Form(request.POST)
            if hardware_type == 'ModProbe':
                hardware_form = HardwareModProbeForm(request.POST)
            if hardware_type == 'PiPico':
                hardware_form = HardwarePiPicoForm(request.POST)
            if hardware_type == 'Pi':
                hardware_form = HardwarePiForm(request.POST)
            if hardware_type == 'VEML7700':
                hardware_form = HardwareVEML7700Form(request.POST)
            if hardware_type == 'PMSA0031':
                hardware_form = HardwarePMSA0031Form(request.POST)
            if hardware_type == 'AM2315':
                hardware_form = HardwareAM2315Form(request.POST)

            # save the data and after fetch the object in instance
            if hardware_form.is_valid():
                instance = hardware_form.save()
                instance.user = request.user;
                instance.save()
                # serialize in new friend object in json
                ser_instance = django_serializers.serialize('json', [instance, ])
                # send to client side.
                return JsonResponse({"instance": ser_instance}, status=200)
            else:
                # some form errors occured.
                return JsonResponse({"error": str(hardware_form.errors)}, status=400)
        elif request.method == "POST":
            import json
            body_json = json.loads(request.body.decode('utf-8'))
            pi_pico = PiPico()
            pi_pico.id = body_json['id']
            pi_pico.type = body_json['type']
            pi_pico.hub = Hub.objects.get(pk=body_json['hub'])
            pi_pico.pi_gpio_interrupt = 1
            pi_pico.user = request.user
            pi_pico.save()
            ser_instance = django_serializers.serialize('json', [pi_pico, ])

            return JsonResponse({"instance": ser_instance}, status=200)
        # some error occured
        return JsonResponse({"error": ""}, status=400)

    def retrieve(self, request, *args, **kwargs):
        print('retrieve')
        print(str(request.path_info))
        hardware_form = HardwareForm(instance=Hardware.objects.get(**kwargs))
        hardware_type = Hardware.objects.get(**kwargs).type

        # hardware_io = HardwareIO.objects.get({'child_hardware':Hardware.objects.get(**kwargs).id})
        hardware_io_type_form = HardwareIOTypeForm(
            initial={'child_hardware': Hardware.objects.get(**kwargs), 'hub': Hardware.objects.get(**kwargs).hub})

        try:
            if hardware_type == 'DHT22':
                hardware_form = HardwareDHT22Form(instance=DHT22.objects.get(**kwargs), initial={'type': 'DHT22'})
            if hardware_type == 'MCP3008':
                hardware_form = HardwareMCP3008Form(instance=MCP3008.objects.get(**kwargs), initial={'type': 'MCP3008'})
            if hardware_type == 'ModProbe':
                hardware_form = HardwareModProbeForm(instance=ModProbe.objects.get(**kwargs),
                                                     initial={'type': 'ModProbe'})
            if hardware_type == 'PiPico':
                hardware_form = HardwarePiPicoForm(instance=PiPico.objects.get(**kwargs), initial={'type': 'PiPico'})
            if hardware_type == 'Pi':
                hardware_form = HardwarePiForm(instance=Pi.objects.get(**kwargs), initial={'type': 'Pi'})
            if hardware_type == 'VEML7700':
                hardware_form = HardwareVEML7700Form(instance=VEML7700.objects.get(**kwargs),
                                                     initial={'type': 'VEML7700'})
            if hardware_type == 'PMSA0031':
                hardware_form = HardwarePMSA0031Form(instance=PMSA0031.objects.get(**kwargs),
                                                     initial={'type': 'PMSA0031'})
            if hardware_type == 'AM2315':
                hardware_form = HardwareAM2315Form(instance=AM2315.objects.get(**kwargs),
                                                     initial={'type': 'AM2315'})
        except:
            hardware_form = HardwareForm(instance=Hardware.objects.get(**kwargs))

        channels = Hardware.objects.get(**kwargs).channel_set.all()
        hardware_configs = Hardware.objects.get(**kwargs).hardwareconfig_set.all()
        channel_form = ChannelForm(hardware_type=Hardware.objects.get(**kwargs).type,
                                   initial={'hardware': Hardware.objects.get(**kwargs)})
        hardware_config_form = HardwareConfigForm()
        if request.accepted_renderer.format == 'html':
            return Response(
                {"hardware_form": hardware_form, "channel_form": channel_form, "channels": channels,
                 "hardware_config_form": hardware_config_form,
                 "hardware_configs": hardware_configs, 'hardware_io_type_form': hardware_io_type_form},
                template_name='hardware.html')

    def postChannel(request):
        if not request.user.is_authenticated:
            return JsonResponse({"error":"user not authenticated"}, status=400)
        # request should be ajax and method should be POST.
        if request.is_ajax and request.method == "POST":
            # get the form data
            form = ChannelForm(data=request.POST)
            # save the data and after fetch the object in instance
            if form.is_valid():
                instance = form.save()
                instance.user = request.user
                instance.save()
                print(str(instance))
                # serialize in new friend object in json
                ser_instance = django_serializers.serialize('json', [instance, ])
                print(str(ser_instance))
                # send to client side.
                return JsonResponse({"instance": ser_instance}, status=200)
            else:
                # some form errors occured.
                return JsonResponse({"error": str(form.errors)}, status=400)

        # some error occured
        return JsonResponse({"error": ""}, status=400)

    def postConfig(request):
        if not request.user.is_authenticated:
            return JsonResponse({"error":"user not authenticated"}, status=400)
        # request should be ajax and method should be POST.
        if request.is_ajax and request.method == "POST":
            # get the form data
            form = HardwareConfigForm(request.POST)
            # save the data and after fetch the object in instance
            if form.is_valid():
                instance = form.save()
                instance.user = request.user
                instance.save()
                print(str(instance))
                # serialize in new friend object in json
                ser_instance = django_serializers.serialize('json', [instance, ])
                print(str(ser_instance))
                # send to client side.
                return JsonResponse({"instance": ser_instance}, status=200)
            else:
                # some form errors occured.
                return JsonResponse({"error": form.errors}, status=400)

        # some error occured
        return JsonResponse({"error": ""}, status=400)

    def deleteHardware(request):
        if not request.user.is_authenticated:
            return JsonResponse({"error":"user not authenticated"}, status=400)
        # request should be ajax and method should be POST.
        if request.is_ajax and request.method == "POST":
            # get the form data
            hardware = Hardware.objects.get(
                pk=request.POST['id'])
            if hardware.user == request.user or hardware.user is None:
                # save the data and after fetch the object in instance
                try:
                    from polymorphic.utils import reset_polymorphic_ctype
                    hardware.delete()
                except PolymorphicTypeInvalid:

                    hardware.get_real_concrete_instance_class().delete()
                return HttpResponse(render(request, 'hardwares.html'))


from data.forms.forms import DataTransform, DataTransformRoot
from data.models.models import DataTransformer
from data.serializers.serializers import DataTransformerTreeSerializer


class AccessoryViewSet(viewsets.ModelViewSet):
    queryset = Accessory.objects.all()
    serializer_class = AccessorySerializer
    renderer_classes = (renderers.JSONRenderer, renderers.TemplateHTMLRenderer)

    def list(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            form = AccessoryForm(initial={"user":request.user})
        else:
            form = AccessoryForm()
        print('list')
        response = super(AccessoryViewSet, self).list(request, *args, **kwargs)
        accessories = Accessory.objects.all()
        if request.accepted_renderer.format == 'html':
            return Response({"form": form, "accessories": accessories}, template_name='accessories.html')
        return response

    def retrieve(self, request, *args, **kwargs):
        print('retrieve')
        print(str(request.path_info))

        accessory = Accessory.objects.get(**kwargs)
        calibrations = accessory.calibration_set.all()
        accessory_form = AccessoryForm(instance=accessory)
        calibration_form = CalibrationForm(initial={'accessory': accessory})

        # datatransformerset = inlineformset_factory(DataTransformer, DataTransformer,formset=DataTransformerForm,
        #                                            fk_name='parent', form=DataTransform,extra=0)

        if accessory.has_data_transformer:
            data_transformer = accessory.datatransformer
            formset = DataTransformRoot(instance=data_transformer)
        else:
            data_transformer_root = DataTransformer.objects.create(accessory=accessory)
            data_transformer_root.save()
            formset = DataTransformRoot(instance=data_transformer_root)

        if request.accepted_renderer.format == 'html':
            return Response(
                {"accessory_form": accessory_form, "calibration_form": calibration_form, "calibrations": calibrations,
                 "data_transformer_form": formset},
                template_name='accessory.html')
        else:
            data_transformer_family = accessory.datatransformer.get_family()
            children_dict = defaultdict(list)
            for descendant in data_transformer_family:
                for child in descendant.get_children():
                    children_dict[descendant.pk].append(child)

            context = super().get_serializer_context()
            context.update({"children": children_dict})
            return super(AccessoryViewSet, self).retrieve(request, *args, **kwargs)

    def postAccessory(request):
        if not request.user.is_authenticated:
            return JsonResponse({"error":"user not authenticated"}, status=400)
        # request should be ajax and method should be POST.
        if request.is_ajax and request.method == "POST":
            # get the form data
            form = AccessoryForm(request.POST)
            # save the data and after fetch the object in instance
            if form.is_valid():
                instance = form.save()
                instance.user = request.user
                instance.save()
                print(str(instance))
                # serialize in new friend object in json
                ser_instance = django_serializers.serialize('json', [instance, ])
                print(str(ser_instance))
                # send to client side.
                return JsonResponse({"instance": ser_instance}, status=200)
            else:
                # some form errors occured.
                return JsonResponse({"error": form.errors}, status=400)

        # some error occured
        return JsonResponse({"error": ""}, status=400)

    def postDataTransformer(request, accessory_id):
        if not request.user.is_authenticated:
            return JsonResponse({"error":"user not authenticated"}, status=400)

        print(str(request.POST))
        print('post data transformer')
        # request should be ajax and method should be POST.
        data = request.POST.copy()
        for key in data.dict().keys():
            if '__prefix__' in key:
                data.pop(key)

        form = DataTransformRoot(instance=DataTransformer.objects.get(pk=request.POST['id']),
                                 data=data)


        data_transformer_root = form.save(True)
        data_transformer_root.user = request.user
        data_transformer_root.save()
        data_transformer_family = data_transformer_root.get_family()
        children_dict = defaultdict(list)
        for descendant in data_transformer_family:
            for child in descendant.get_children():
                children_dict[descendant.pk].append(child)
                child.user = request.user
                child.save()

        context = {}
        context['children'] = children_dict
        serializer = DataTransformerTreeSerializer(data_transformer_root, context=context)
        print(str(serializer.data))

        return JsonResponse({"instance": serializer.data}, status=200)

    def postCalibration(request):
        print('post calibration')

        # request should be ajax and method should be POST.
        if request.is_ajax and request.method == "POST":
            # get the form data
            form = CalibrationForm(request.POST)
            # save the data and after fetch the object in instance
            if form.is_valid():
                instance = form.save()
                print(str(instance))
                # serialize in new friend object in json
                ser_instance = django_serializers.serialize('json', [instance, ])
                print(str(ser_instance))
                # send to client side.
                return JsonResponse({"instance": ser_instance}, status=200)
            else:
                # some form errors occured.
                return JsonResponse({"error": form.errors}, status=400)

        # some error occured
        return JsonResponse({"error": ""}, status=400)

    def updateAccessory(request):
        # request should be ajax and method should be POST.
        if request.is_ajax and request.method == "PATCH" and request.user.is_authenticated():
            # get the form data
            form = AccessoryForm(instance=Accessory.objects.get(pk=QueryDict(request.body)['id']),
                                 data=QueryDict(request.body))
            # save the data and after fetch the object in instance
            if form.is_valid():
                instance = form.save()
                instance.user = request.user
                instance.save()
                print(str(instance))
                # serialize in new friend object in json
                ser_instance = django_serializers.serialize('json', [instance, ])
                print(str(ser_instance))
                # send to client side.
                return JsonResponse({"instance": ser_instance}, status=200)
            else:
                # some form errors occured.
                return JsonResponse({"error": form.errors}, status=400)

        # some error occured
        return JsonResponse({"error": ""}, status=400)

    def deleteAccessory(request):
        # request should be ajax and method should be POST.
        if request.is_ajax and request.method == "DELETE" and request.user.is_authenticated():
            # get the form data
            form = AccessoryForm(instance=Accessory.objects.get(pk=QueryDict(request.body)['id']),
                                 data=QueryDict(request.body))
            accessory = Accessory.objects.get(
                pk=QueryDict(request.body)['id'])  # save the data and after fetch the object in instance
            if accessory.user==request.user or accessory.user is None:
                accessory.delete()

            return HttpResponse(render(request, 'accessories.html'))


class CalibrationViewSet(viewsets.ModelViewSet):
    queryset = Calibration.objects.all()
    serializer_class = CalibrationSerializer
    renderer_classes = (renderers.JSONRenderer, renderers.TemplateHTMLRenderer)

    def retrieve(self, request, *args, **kwargs):
        print('retrieve')
        print(str(request.path_info))
        calibration = Calibration.objects.get(**kwargs)
        calibration_constants = calibration.calibrationconstants_set.all()
        calibration_form = CalibrationForm(instance=calibration)
        calibrationconstants_form = CalibrationConstantForm(initial={'calibration': calibration})

        calibration_constants_forms = []

        for calibration_constant in calibration_constants:
            calibration_constants_forms.append(CalibrationConstantForm(instance=calibration_constant))
        if request.accepted_renderer.format == 'html':
            return Response(
                {"calibration_form": calibration_form, "calibrationconstants_initial_form": calibrationconstants_form,
                 "calibrationconstants_forms": calibration_constants_forms,
                 "calibrations": calibration_constants, "calibration": calibration},
                template_name='calibration.html')
        else:
            return super(CalibrationViewSet, self).retrieve()

    def updateCalibration(request):
        # request should be ajax and method should be POST.
        if request.is_ajax and request.method == "UPDATE":
            # get the form data
            form = CalibrationForm(request.UPDATE)
            # save the data and after fetch the object in instance
            if form.is_valid():
                instance = form.save()
                print(str(instance))
                # serialize in new friend object in json
                ser_instance = django_serializers.serialize('json', [instance, ])
                print(str(ser_instance))
                # send to client side.
                return JsonResponse({"instance": ser_instance}, status=200)
            else:
                # some form errors occured.
                return JsonResponse({"error": form.errors}, status=400)

        # some error occured
        return JsonResponse({"error": ""}, status=400)

    def postCalibrationConstant(request):
        # request should be ajax and method should be POST.
        if request.is_ajax and request.method == "POST":
            # get the form data
            try:
                initial_calibration_constant = CalibrationConstants.objects.get(id=request.POST['id'])
                form = CalibrationConstantForm(instance=initial_calibration_constant, data=request.POST)
            except CalibrationConstants.DoesNotExist:
                form = CalibrationConstantForm(data=request.POST)

            # save the data and after fetch the object in instance
            if form.is_valid():
                instance = form.save()
                print(str(instance))
                # serialize in new friend object in json
                ser_instance = django_serializers.serialize('json', [instance, ])
                form_json = django_serializers.serialize('json', [instance, ])
                print(str(ser_instance))
                # send to client side.
                return JsonResponse({"instance": ser_instance, "form": form_json}, status=200)
            else:
                # some form errors occured.
                return JsonResponse({"error": form.errors}, status=400)

        # some error occured
        return JsonResponse({"error": ""}, status=400)


class ChannelViewSet(viewsets.ModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
    renderer_classes = (renderers.JSONRenderer, renderers.TemplateHTMLRenderer)

    def retrieve(self, request, *args, **kwargs):
        print('retrieve')
        print(str(request.path_info))
        hardware_io_type_form = HardwareIOTypeForm(
            initial={'parent_hardware': Channel.objects.get(**kwargs).hardware.id,
                     'child_channel': Channel.objects.get(**kwargs).id,
                     'hub': Channel.objects.get(**kwargs).hub.id})
        hardware_ios = Channel.objects.get(**kwargs).hardwareio_set.all()
        channel_stats = Channel.objects.get(**kwargs).channelstats_set.all()

        channel = Channel.objects.get(**kwargs)

        channel_form = ChannelForm(Channel.objects.get(**kwargs).hardware.type, instance=channel)
        if request.accepted_renderer.format == 'html':
            return Response(
                {"channel_form": channel_form, "channel": channel, 'hardware_io_type_form': hardware_io_type_form,
                 'hardware_ios': hardware_ios, 'channel_stats': channel_stats},
                template_name='channel.html')
        else:
            return super(ChannelViewSet, self).retrieve()

    def listIO(self, channel_id):
        print('list io')
        hardware_ios = Channel.objects.get(pk=channel_id).hardwareio_set.all()
        serialized_hardware_ios = HardwareIOSerializer(many=True).to_representation(hardware_ios)

        return JsonResponse(serialized_hardware_ios, status=200, safe=False)

    def updateChannel(request):
        # request should be ajax and method should be POST.
        if request.is_ajax and request.method == "PATCH" and request.user.is_authenticated():
            # get the form data
            form = ChannelForm(instance=Channel.objects.get(pk=QueryDict(request.body)['id']),
                               data=QueryDict(request.body))

            # save the data and after fetch the object in instance
            if form.is_valid():
                instance = form.save()
                instance.user = request.user
                instance.save()
                print(str(instance))
                # serialize in new friend object in json
                ser_instance = django_serializers.serialize('json', [instance, ])
                print(str(ser_instance))
                # send to client side.
                return JsonResponse({"instance": ser_instance}, status=200)
            else:
                # some form errors occured.
                return JsonResponse({"error": form.errors}, status=400)

        # some error occured
        return JsonResponse({"error": ""}, status=400)

    def deleteChannel(request):
        # request should be ajax and method should be POST.
        if request.is_ajax and request.method == "DELETE":
            # get the form data
            form = ChannelForm(instance=Channel.objects.get(pk=QueryDict(request.body)['id']),
                               data=QueryDict(request.body))
            channel = Channel.objects.get(
                pk=QueryDict(request.body)['id'])  # save the data and after fetch the object in instance
            if channel.user == request.user or channel.user is None:
                channel.delete()

            return HttpResponse(render(request, 'accessories.html'))


class HubViewSet(viewsets.ModelViewSet):
    queryset = Hub.objects.all()
    serializer_class = HubSerializer
    renderer_classes = (renderers.JSONRenderer, renderers.TemplateHTMLRenderer)
    context_object_name = 'all_hubs'

    def get_queryset(self):
        return Hub.objects.all()

    def about(self, *args, **kwargs):
        api_about = {}
        api_about['isAPI'] = True
        return JsonResponse(api_about, status=200, safe=False)

    def list(self, request, *args, **kwargs):
        print('list')
        response = super(HubViewSet, self).list(request, *args, **kwargs)
        form = HubForm()
        hubs = Hub.objects.all()
        if request.accepted_renderer.format == 'html':
            return Response({"form": form, "hubs": hubs}, template_name='hubs.html')
        return response

    @csrf_exempt
    def retrieve(self, request, *args, **kwargs):

        if request.accepted_renderer.format == 'html':
            print('retrieve')
            print(str(request.path_info))
            hub = Hub.objects.get(**kwargs)
            hub_form = HubForm(instance=hub)

            # accessories_form = AccessoryForm()
            # channel_form = ChannelForm(Hub.objects.get(**kwargs).channel_set.type, instance=channel)
            return Response(
                {"hub_form": hub_form},
                template_name='hub.html')
        else:
            hub = Hub.objects.get(**kwargs)
            hub_data = HubSerializer(instance=hub).to_representation(hub)
            return JsonResponse(hub_data, status=200)

    def postHub(request):
        # request should be ajax and method should be POST.
        if request.is_ajax() and request.method == "POST":
            # get the form data
            form = HubForm(request.POST)
            # save the data and after fetch the object in instance
            if form.is_valid():
                instance = form.save()
                print(str(instance))
                # serialize in new friend object in json
                ser_instance = django_serializers.serialize('json', [instance, ])
                print(str(ser_instance))
                # send to client side.
                return JsonResponse({"instance": ser_instance}, status=200)
            else:
                # some form errors occured.
                return JsonResponse({"error": form.errors}, status=400)
        elif request.method == "POST":
            import json
            body_json = json.loads(request.body.decode('utf-8'))
            hub = Hub()
            hub.id = body_json['id']
            hub.ip = body_json['ip']
            hub.display_name = body_json['display_name']
            hub.aid = body_json['aid']
            hub.save()
            ser_instance = django_serializers.serialize('json', [hub, ])

            return JsonResponse({"instance": ser_instance}, status=200)

        # some error occured
        return JsonResponse({"error": ""}, status=400)

    def updateHub(request):
        # request should be ajax and method should be POST.
        if request.is_ajax and request.method == "PATCH" and request.user.is_authenticated:
            # get the form data
            form = HubForm(instance=Hub.objects.get(pk=QueryDict(request.body)['id']),
                                 data=QueryDict(request.body))
            # save the data and after fetch the object in instance
            if form.is_valid():
                instance = form.save()
                instance.user = request.user
                instance.save()
                print(str(instance))
                # serialize in new friend object in json
                ser_instance = django_serializers.serialize('json', [instance, ])
                print(str(ser_instance))
                # send to client side.
                return JsonResponse({"instance": ser_instance}, status=200)
            else:
                # some form errors occured.
                return JsonResponse({"error": form.errors}, status=400)

        # some error occured
        return JsonResponse({"error": ""}, status=400)

    def deleteHub(request):
        # request should be ajax and method should be POST.
        if request.is_ajax and request.method == "DELETE" and request.user.is_authenticated:
            # get the form data
            form = HubForm(instance=Hub.objects.get(pk=QueryDict(request.body)['id']),
                                 data=QueryDict(request.body))
            hub = Hub.objects.get(
                pk=QueryDict(request.body)['id'])  # save the data and after fetch the object in instance
            if hub.user==request.user or hub.user is None:
                hub.delete()

            return HttpResponse(render(request, 'hubs.html'))


def index(request):
    context = {'title': 'HomeHub'}
    return render(request, 'home.html', context)


#


class IOViewSet(viewsets.ModelViewSet):
    queryset = HardwareIO.objects.all()
    serializer_class = HardwareIOSerializer
    renderer_classes = (renderers.JSONRenderer, renderers.TemplateHTMLRenderer)

    def retrieve(self, request, *args, **kwargs):
        print('retrieve')
        print(str(request.path_info))
        hardware_io_type = HardwareIO.objects.get(**kwargs).type
        instance = HardwareIO.objects.get(**kwargs)
        if hardware_io_type == SPI:
            hardware_form = SPIIoForm(instance=instance)
        if hardware_io_type == Serial:
            hardware_form = SerialIoForm(instance=instance)
        if hardware_io_type == PWM:
            hardware_form = PwmIoForm(instance=instance)
        if hardware_io_type == I2C:
            hardware_form = I2cIoForm(instance=instance)
        if hardware_io_type == DeviceFile:
            hardware_form = DeviceFileIoForm(instance=instance)
        if hardware_io_type == MCPChannel:
            hardware_form = MCPAnalogIoForm(instance=instance)
        if hardware_io_type == PiPicoAnalog:
            hardware_form = PiPicoAnalogIoForm(instance=instance)
        if hardware_io_type == PiPicoACAnalog:
            hardware_form = PiPicoACAnalogIoForm(instance=instance)
        if hardware_io_type == PiGPIO:
            hardware_form = PiGpioForm(instance=instance)

        if request.accepted_renderer.format == 'html':
            return Response(
                {"hardware_io_form": hardware_form},
                template_name='io.html')
        else:
            return super(IOViewSet, self).retrieve()

    def updateIO(request):
        # request should be ajax and method should be POST.

        if request.is_ajax and request.method == "PATCH" and request.user.is_authenticated():
            # get the form data
            form = HardwareIoForm(instance=Channel.objects.get(pk=QueryDict(request.body)['id']),
                                  data=QueryDict(request.body))

            # save the data and after fetch the object in instance
            if form.is_valid():
                instance = form.save()
                instance.user = request.user
                instance.save()
                print(str(instance))
                # serialize in new friend object in json
                ser_instance = django_serializers.serialize('json', [instance, ])
                print(str(ser_instance))
                # send to client side.
                return JsonResponse({"instance": ser_instance}, status=200)
            else:
                # some form errors occured.
                return JsonResponse({"error": form.errors}, status=400)

        # some error occured
        return JsonResponse({"error": ""}, status=400)

    def deleteIO(request):
        # request should be ajax and method should be POST.
        if request.is_ajax and request.method == "DELETE":
            # get the form data
            form = HardwareIoForm(instance=HardwareIO.objects.get(pk=QueryDict(request.body)['id']),
                                  data=QueryDict(request.body))
            hardware_io = HardwareIO.objects.get(
                pk=QueryDict(request.body)['id'])  # save the data and after fetch the object in instance
            if request.user == hardware_io.user or hardware_io.user is None:
                hardware_io.delete()

            return HttpResponse(render(request, 'accessories.html'))


def video_streams(request):
    return render(request, "streams.html", None)


from django.contrib.auth import login, authenticate, logout as django_logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

@api_view(('GET','POST'))
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def createUser(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('hubs-list')
    else:
        form = UserCreationForm()
    return Response({"request": request, "form": form},
                 template_name='registration/create_user.html')
    # return render(request, 'registration/create_user.html', {'form': form})

@api_view(('GET',))
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def logout(request):
    django_logout(request._request)
    return redirect('hubs-list')



@api_view(('GET',))
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def listHubHardware(request, hub_id):
    if request.user.is_authenticated:
        hardware_form = HardwarePiPicoForm(initial={'type': 'PiPico',"user": request.user, "hub": Hub.objects.get(pk=hub_id)})
    else:
        hardware_form = HardwarePiPicoForm(initial={'type': 'PiPico', "hub": Hub.objects.get(pk=hub_id)})
    form_type = HardwareTypeForm(initial={'type': 'PiPico'})
    hardware = Hub.objects.get(pk=hub_id).hardware_set.all()
    if request.accepts("text/html"):
        return Response({"form": hardware_form, "type_form": form_type, "hardwares": hardware},
                        template_name='hardwares.html')

    serialized_hardware = HardwareSerializer().to_json_array(hardware)
    return JsonResponse(serialized_hardware, status=200, safe=False)


@api_view(('GET',))
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def listHubChannels(request, hub_id):
    channels = Hub.objects.get(pk=hub_id).channel_set.all()
    serialized_channels = ChannelSerializer(many=True).to_representation(channels)
    return JsonResponse(serialized_channels, status=200, safe=False)


@api_view(('GET',))
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def listHubAccessories(request, hub_id):

    accessories = Hub.objects.get(pk=hub_id).accessory_set.all()

    if request.accepts("text/html"):
        if request.user.is_authenticated:
            form = AccessoryForm(initial={"user":request.user,"hub":Hub.objects.get(pk=hub_id)})
        else:
            form = AccessoryForm(initial={"hub":Hub.objects.get(pk=hub_id)})
        return Response({"form": form, "accessories": accessories}, template_name='accessories.html')
    serialized_accessories =[]
    for accessory in accessories:
        if accessory.datatransformer is not None:
            data_transformer_family = accessory.datatransformer.get_family()
            children_dict = defaultdict(list)
            for descendant in data_transformer_family:
                for child in descendant.get_children():
                    children_dict[descendant.pk].append(child)
            ser = AccessorySerializer(accessory)
            ser.context['children'] = children_dict
            serialized_accessories.append(ser.data)

    return JsonResponse(serialized_accessories, status=200, safe=False)


class ChannelStatsViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing the accounts
    associated with the user.
    """
    serializer_class = ChannelStatsSerializer

    # permission_classes = [IsAccountAdminOrReadOnly]

    def get_queryset(self):
        return self.request.channel.channelstats_set.all()

    def retrieve(self, request, *args, **kwargs):

        if request.accepted_renderer.format == 'html':
            print('retrieve')
            print(str(request.path_info))
            stats = ChannelStats.objects.get(**kwargs)
            stats_form = ChannelStatsForm(instance=stats)

            # accessories_form = AccessoryForm()
            # channel_form = ChannelForm(Hub.objects.get(**kwargs).channel_set.type, instance=channel)
            return Response(
                {"stats_form": stats_form},
                template_name='template_stats.html')
        else:
            stats = ChannelStats.objects.get(**kwargs)
            stats_data = ChannelStatsSerializer(instance=stats).to_representation(stats)
            return JsonResponse(stats_data, status=200)

    def create(self, request, *args, **kwargs):
            print(str(request.POST))
            try:
                stats = ChannelStats.objects.get(pk=request.POST['id'])

            except:
                stats = ChannelStats()
            stats.id = request.POST['id']
            stats.type = request.POST['type']
            stats.value = request.POST['value']
            stats.channel = Channel.objects.get(pk=request.POST['channel'])
            stats.user = stats.channel.user
            stats.save()

            stats_data = ChannelStatsSerializer(instance=stats).to_representation(stats)
            return JsonResponse(stats_data, status=200)

    def update(self, request, *args, **kwargs):
            try:
                stats = ChannelStats.objects.get(request.POST['pk'])

            except:
                stats = ChannelStats.objects.create(request.POST)
            stats.type = request.POST['type']
            stats.value = request.POST['value']
            stats.channel = request.POST['channel']
            stats.user = stats.channel.user
            stats.save()

            stats_data = ChannelStatsSerializer(instance=stats).to_representation(stats)
            return JsonResponse(stats_data, status=200)