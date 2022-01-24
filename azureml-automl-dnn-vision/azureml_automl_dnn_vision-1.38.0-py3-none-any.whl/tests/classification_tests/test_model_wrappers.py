import os
import pytest
import torch
import torchvision.transforms.functional as functional

from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionValidationException,\
    AutoMLVisionSystemException
from azureml.automl.dnn.vision.classification.models.classification_model_wrappers import ModelFactory, \
    Resnet18Wrapper, Resnet34Wrapper, Resnet50Wrapper, Resnet101Wrapper, Resnet152Wrapper, \
    Mobilenetv2Wrapper, SeresnextWrapper, ResNest50Wrapper, ResNest101Wrapper
from azureml.automl.dnn.vision.classification.models.classification_model_wrappers import ViTB16R224Wrapper, \
    ViTS16R224Wrapper, ViTL16R224Wrapper
from azureml.automl.dnn.vision.classification.common.constants import ModelNames, ModelLiterals, \
    ModelParameters, base_training_settings_defaults
from azureml.automl.dnn.vision.common.constants import SettingsLiterals
from azureml.automl.dnn.vision.common.utils import get_model_layer_info
from PIL import Image

from ..common.utils import check_exported_onnx_model


@pytest.mark.usefixtures('new_clean_dir')
class TestModelWrappers:
    def _load_batch_of_pil(self, test_data_image_list):
        raise NotImplementedError

    def test_wrappers(self):
        # right now only initialization and making sure that the model is working
        model_wapper_args = dict(num_classes=20, valid_resize_size=256, valid_crop_size=224, train_crop_size=224)
        Resnet18Wrapper(**model_wapper_args)
        Resnet34Wrapper(**model_wapper_args)
        Resnet50Wrapper(**model_wapper_args)
        Resnet101Wrapper(**model_wapper_args)
        Resnet152Wrapper(**model_wapper_args)
        Mobilenetv2Wrapper(**model_wapper_args)
        SeresnextWrapper(**model_wapper_args)
        ResNest50Wrapper(**model_wapper_args)
        ResNest101Wrapper(**model_wapper_args)
        ViTB16R224Wrapper(**model_wapper_args)
        ViTS16R224Wrapper(**model_wapper_args)
        ViTL16R224Wrapper(**model_wapper_args)

        assert True

    def test_all_models_have_model_layer_info(self):
        model_factory = ModelFactory()
        for model_name in model_factory._models_dict.keys():
            # Should not raise an error if we defined the model layer info.
            get_model_layer_info(model_name)

        with pytest.raises(AutoMLVisionSystemException):
            get_model_layer_info("nonexistent_model")

    def test_wrappers_export_onnx(self, root_dir):
        # right now only initialization and making sure that the model is working
        model_wapper_args = dict(num_classes=20, valid_resize_size=256, valid_crop_size=224, train_crop_size=224)
        device = base_training_settings_defaults[SettingsLiterals.DEVICE]
        image = Image.open(os.path.join(root_dir, 'car.jpg')).convert('RGB')
        image_tensor = functional.to_tensor(image).unsqueeze(0).to(device=device)
        resized_image = torch.nn.functional.interpolate(image_tensor, size=(224, 224),
                                                        mode='bilinear', align_corners=False)

        def get_model_output(wrapper, input, device):
            return wrapper._get_model_output(input)

        res18 = Resnet18Wrapper(**model_wapper_args)
        res18_file = 'Resnet18Wrapper.onnx'
        res18.export_onnx_model(file_path=res18_file, device=device)
        check_exported_onnx_model(res18_file, res18, resized_image, device, get_model_output)

        res34 = Resnet34Wrapper(num_classes=20, valid_resize_size=96, valid_crop_size=64, train_crop_size=96)
        res34_file = 'Resnet34Wrapper.onnx'
        res34.export_onnx_model(file_path=res34_file, device=device)
        mininum_resized_image = torch.nn.functional.interpolate(image_tensor, size=(64, 64),
                                                                mode='bilinear', align_corners=False)
        check_exported_onnx_model(res34_file, res34, mininum_resized_image, device, get_model_output)

        # pass none-default values for input image size
        res50 = Resnet50Wrapper(num_classes=20, valid_resize_size=256 + 32, valid_crop_size=224 + 32,
                                train_crop_size=224)
        res50_file = 'Resnet50Wrapper.onnx'
        res50.export_onnx_model(file_path=res50_file, device=device)
        bigger_resized_image = torch.nn.functional.interpolate(image_tensor, size=(224 + 32, 224 + 32),
                                                               mode='bilinear', align_corners=False)
        check_exported_onnx_model(res50_file, res50, bigger_resized_image, device, get_model_output)

        res101 = Resnet101Wrapper(num_classes=10, valid_resize_size=256 - 32, valid_crop_size=224 - 32,
                                  train_crop_size=224)
        res101_file = 'Resnet101Wrapper.onnx'
        res101.export_onnx_model(file_path=res101_file, device=device)
        smaller_resized_image = torch.nn.functional.interpolate(image_tensor, size=(224 - 32, 224 - 32),
                                                                mode='bilinear', align_corners=False)
        check_exported_onnx_model(res101_file, res101, smaller_resized_image, device, get_model_output)

        res152 = Resnet152Wrapper(num_classes=5, valid_resize_size=256 - 32, valid_crop_size=224 - 32,
                                  train_crop_size=224)
        res152_file = 'Resnet152Wrapper.onnx'
        res152.export_onnx_model(file_path=res152_file, device=device)
        smaller_resized_image = torch.nn.functional.interpolate(image_tensor, size=(224 - 32, 224 - 32),
                                                                mode='bilinear', align_corners=False)
        check_exported_onnx_model(res152_file, res152, smaller_resized_image, device, get_model_output)

        mv2 = Mobilenetv2Wrapper(num_classes=20, valid_resize_size=256 - 32, valid_crop_size=224 - 32,
                                 train_crop_size=224)
        mv2_file = 'Mobilenetv2Wrapper.onnx'
        mv2.export_onnx_model(file_path=mv2_file, device=device)
        smaller_resized_image = torch.nn.functional.interpolate(image_tensor, size=(224 - 32, 224 - 32),
                                                                mode='bilinear', align_corners=False)
        check_exported_onnx_model(mv2_file, mv2, smaller_resized_image, device, get_model_output)

        # make sure that seresnext only takes the default even if we pass none-default value
        sn = SeresnextWrapper(num_classes=20, valid_resize_size=256 + 32, valid_crop_size=224 + 32,
                              train_crop_size=224)
        sn_file = 'SeresnextWrapper.onnx'
        sn.export_onnx_model(file_path=sn_file, device=device)
        check_exported_onnx_model(sn_file, sn, resized_image, device, get_model_output)

        # export onnx w/ normalization
        snn_file = 'SeresnextWrapperNorm.onnx'
        sn.export_onnx_model(file_path=snn_file, device=device, enable_norm=True)
        check_exported_onnx_model(snn_file, sn, resized_image, device, get_model_output, is_norm=True)

        # pass non-default values for input image size
        resnest50 = ResNest50Wrapper(num_classes=20, valid_resize_size=256 - 32, valid_crop_size=224 - 32,
                                     train_crop_size=224)
        resnest50_file = 'Resnest50Wrapper.onnx'
        resnest50.export_onnx_model(file_path=resnest50_file, device=device)
        check_exported_onnx_model(resnest50_file, resnest50, smaller_resized_image, device, get_model_output)

        # pass non-default values for input image size
        resnest101 = ResNest101Wrapper(num_classes=20, valid_resize_size=256 + 32, valid_crop_size=224 + 32,
                                       train_crop_size=224)
        resnest101_file = 'Resnest101Wrapper.onnx'
        resnest101.export_onnx_model(file_path=resnest101_file, device=device)
        check_exported_onnx_model(resnest101_file, resnest101, bigger_resized_image, device, get_model_output)

        # pass non-default values for input image size
        vitb16r224 = ViTB16R224Wrapper(num_classes=20, valid_resize_size=256 + 32, valid_crop_size=224 + 32,
                                       train_crop_size=224)
        vitb16r224_file = 'ViTB16R224Wrapper.onnx'
        vitb16r224.export_onnx_model(file_path=vitb16r224_file, device=device)
        check_exported_onnx_model(vitb16r224_file, vitb16r224, bigger_resized_image, device, get_model_output)

        # pass non-default values for input image size
        vits16r224 = ViTS16R224Wrapper(num_classes=20, valid_resize_size=256 + 32, valid_crop_size=224 + 32,
                                       train_crop_size=224)
        vits16r224_file = 'ViTS16R224Wrapper.onnx'
        vits16r224.export_onnx_model(file_path=vits16r224_file, device=device)
        check_exported_onnx_model(vits16r224_file, vits16r224, bigger_resized_image, device, get_model_output)

        # pass non-default values for input image size
        vitl16r224 = ViTL16R224Wrapper(num_classes=20, valid_resize_size=256 + 32, valid_crop_size=224 + 32,
                                       train_crop_size=224)
        vitl16r224_file = 'ViTL16R224Wrapper.onnx'
        vitl16r224.export_onnx_model(file_path=vitl16r224_file, device=device)
        check_exported_onnx_model(vitl16r224_file, vitl16r224, bigger_resized_image, device, get_model_output)

        assert True

    def test_model_factory(self):
        model_factory = ModelFactory()
        # resnet18
        model_wrapper = model_factory.get_model_wrapper(model_name=ModelNames.RESNET18, num_classes=5,
                                                        multilabel=True, device='cpu', distributed=False, rank=0,
                                                        settings={ModelLiterals.VALID_RESIZE_SIZE: 256,
                                                                  ModelLiterals.VALID_CROP_SIZE: 224,
                                                                  ModelLiterals.TRAIN_CROP_SIZE: 224})
        assert model_wrapper.valid_resize_size == 256 and model_wrapper.valid_crop_size == 224
        assert model_wrapper.train_crop_size == 224
        # resnet34
        model_wrapper = model_factory.get_model_wrapper(model_name=ModelNames.RESNET34, num_classes=5,
                                                        multilabel=True, device='cpu', distributed=False, rank=0,
                                                        settings={ModelLiterals.VALID_RESIZE_SIZE: 96,
                                                                  ModelLiterals.VALID_CROP_SIZE: 64})
        assert model_wrapper.valid_resize_size == 96 and model_wrapper.valid_crop_size == 64
        # resnet50
        model_wrapper = model_factory.get_model_wrapper(ModelNames.RESNET50, 5, True, 'cpu', False, 0,
                                                        {ModelLiterals.VALID_RESIZE_SIZE: 256 + 32,
                                                         ModelLiterals.VALID_CROP_SIZE: 224 + 32})
        assert model_wrapper.valid_resize_size == 256 + 32 and model_wrapper.valid_crop_size == 224 + 32
        # resnet101
        model_wrapper = model_factory.get_model_wrapper(ModelNames.RESNET101, 5, True, 'cpu', False, 0,
                                                        {ModelLiterals.VALID_RESIZE_SIZE: 256 - 32,
                                                         ModelLiterals.VALID_CROP_SIZE: 224 - 32})
        assert model_wrapper.valid_resize_size == 256 - 32 and model_wrapper.valid_crop_size == 224 - 32
        # resnet152
        model_wrapper = model_factory.get_model_wrapper(ModelNames.RESNET152, 5, True, 'cpu', False, 0,
                                                        {ModelLiterals.VALID_RESIZE_SIZE: 256 - 64,
                                                         ModelLiterals.VALID_CROP_SIZE: 224 - 64})
        assert model_wrapper.valid_resize_size == 256 - 64 and model_wrapper.valid_crop_size == 224 - 64
        # mobilenetv2
        model_wrapper = model_factory.get_model_wrapper(ModelNames.MOBILENETV2, 5, True, 'cpu', False, 0)
        assert model_wrapper.valid_resize_size == ModelParameters.DEFAULT_VALID_RESIZE_SIZE
        assert model_wrapper.valid_crop_size == ModelParameters.DEFAULT_VALID_CROP_SIZE
        # seresnext
        # (unlike other models) seresnext only takes the fixed default values for input image size.
        # Thus, even if we pass none-default value, we still setup a model with default values.
        model_wrapper = model_factory.get_model_wrapper(ModelNames.SERESNEXT, 5, True, 'cpu', False, 0,
                                                        {ModelLiterals.VALID_RESIZE_SIZE: 256 + 32,
                                                         ModelLiterals.VALID_CROP_SIZE: 224 + 32})
        assert model_wrapper.valid_resize_size == ModelParameters.DEFAULT_VALID_RESIZE_SIZE
        assert model_wrapper.valid_crop_size == ModelParameters.DEFAULT_VALID_CROP_SIZE
        # resnest50
        model_wrapper = model_factory.get_model_wrapper(model_name=ModelNames.RESNEST50, num_classes=5,
                                                        multilabel=True, device='cpu', distributed=False, rank=0,
                                                        settings={ModelLiterals.VALID_RESIZE_SIZE: 256 - 32,
                                                                  ModelLiterals.VALID_CROP_SIZE: 224 - 32})
        assert model_wrapper.valid_resize_size == 256 - 32 and model_wrapper.valid_crop_size == 224 - 32
        # resnest101
        model_wrapper = model_factory.get_model_wrapper(model_name=ModelNames.RESNEST101, num_classes=5,
                                                        multilabel=True, device='cpu', distributed=False, rank=0,
                                                        settings={ModelLiterals.VALID_RESIZE_SIZE: 256 + 32,
                                                                  ModelLiterals.VALID_CROP_SIZE: 224 + 32})
        assert model_wrapper.valid_resize_size == 256 + 32 and model_wrapper.valid_crop_size == 224 + 32

        # vitb16r224
        model_wrapper = model_factory.get_model_wrapper(model_name=ModelNames.VITB16R224, num_classes=5,
                                                        multilabel=True, device='cpu', distributed=False, rank=0,
                                                        settings={ModelLiterals.VALID_RESIZE_SIZE: 256 + 32,
                                                                  ModelLiterals.VALID_CROP_SIZE: 224 + 32})
        assert model_wrapper.valid_resize_size == 256 + 32 and model_wrapper.valid_crop_size == 224 + 32
        # (unlike other models) vit models don't support different values for train_crop_size and valid_crop_size.
        # If different values are passed, valid_crop_size is used for both
        model_wrapper = model_factory.get_model_wrapper(model_name=ModelNames.VITB16R224, num_classes=5,
                                                        multilabel=True, device='cpu', distributed=False, rank=0,
                                                        settings={ModelLiterals.VALID_RESIZE_SIZE: 256 + 32,
                                                                  ModelLiterals.VALID_CROP_SIZE: 224 + 32,
                                                                  ModelLiterals.TRAIN_CROP_SIZE: 256 + 32})
        assert model_wrapper.valid_resize_size == 256 + 32 and model_wrapper.valid_crop_size == 224 + 32
        assert model_wrapper.train_crop_size == 224 + 32

        # vits16r224
        model_wrapper = model_factory.get_model_wrapper(model_name=ModelNames.VITS16R224, num_classes=5,
                                                        multilabel=True, device='cpu', distributed=False, rank=0,
                                                        settings={ModelLiterals.VALID_RESIZE_SIZE: 256 + 32,
                                                                  ModelLiterals.VALID_CROP_SIZE: 224 + 32})
        assert model_wrapper.valid_resize_size == 256 + 32 and model_wrapper.valid_crop_size == 224 + 32
        # (unlike other models) vit models don't support different values for train_crop_size and valid_crop_size.
        # If different values are passed, valid_crop_size is used for both
        model_wrapper = model_factory.get_model_wrapper(model_name=ModelNames.VITS16R224, num_classes=5,
                                                        multilabel=True, device='cpu', distributed=False, rank=0,
                                                        settings={ModelLiterals.VALID_RESIZE_SIZE: 256 + 32,
                                                                  ModelLiterals.VALID_CROP_SIZE: 224 + 32,
                                                                  ModelLiterals.TRAIN_CROP_SIZE: 256 + 32})
        assert model_wrapper.valid_resize_size == 256 + 32 and model_wrapper.valid_crop_size == 224 + 32
        assert model_wrapper.train_crop_size == 224 + 32

        # vitl16r224
        model_wrapper = model_factory.get_model_wrapper(model_name=ModelNames.VITL16R224, num_classes=5,
                                                        multilabel=True, device='cpu', distributed=False, rank=0,
                                                        settings={ModelLiterals.VALID_RESIZE_SIZE: 256 + 32,
                                                                  ModelLiterals.VALID_CROP_SIZE: 224 + 32})
        assert model_wrapper.valid_resize_size == 256 + 32 and model_wrapper.valid_crop_size == 224 + 32
        # (unlike other models) vit models don't support different values for train_crop_size and valid_crop_size.
        # If different values are passed, valid_crop_size is used for both
        model_wrapper = model_factory.get_model_wrapper(model_name=ModelNames.VITL16R224, num_classes=5,
                                                        multilabel=True, device='cpu', distributed=False, rank=0,
                                                        settings={ModelLiterals.VALID_RESIZE_SIZE: 256 + 32,
                                                                  ModelLiterals.VALID_CROP_SIZE: 224 + 32,
                                                                  ModelLiterals.TRAIN_CROP_SIZE: 256 + 32})
        assert model_wrapper.valid_resize_size == 256 + 32 and model_wrapper.valid_crop_size == 224 + 32
        assert model_wrapper.train_crop_size == 224 + 32

    def test_model_factory_nonpresent_model(self):
        with pytest.raises(AutoMLVisionValidationException):
            ModelFactory().get_model_wrapper('nonexistent_model', 5, True, 'cpu', False, 0)

    @pytest.mark.skip(reason="not implemented")
    def test_model_predict(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="not implemented")
    def test_model_predict_proba(self):
        raise NotImplementedError
