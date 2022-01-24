# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Base class for model wrappers."""

from abc import ABC
import time
import torch

from azureml.automl.dnn.vision.classification.common.constants import ModelParameters, ModelLiterals
from azureml.automl.dnn.vision.common.constants import ArtifactLiterals
from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionSystemException
from azureml.automl.dnn.vision.common.logging_utils import get_logger

logger = get_logger(__name__)


class BaseModelWrapper(ABC):
    """Base class for model wrappers.

    Base class that model wrappers should inherit from. All inheriting concrete classes should call the base
    constructor.
    """

    def __init__(self, model, number_of_classes, valid_resize_size, valid_crop_size, train_crop_size,
                 multilabel=False, model_name=None, image_mean=ModelParameters.DEFAULT_IMAGE_MEAN,
                 image_std=ModelParameters.DEFAULT_IMAGE_STD, featurizer=None):
        """BaseModelWrapper constructor that the concrete classes should call.

        :param model: torch model
        :type model: torch.nn.module
        :param number_of_classes: Number of object classes
        :type number_of_classes: Int
        :param valid_resize_size: length of side of the square that we have to resize to for validation dataset
        :type valid_resize_size: int
        :param valid_crop_size: length of side of the square that we have to crop for passing to model
            for validation dataset
        :type valid_crop_size: int
        :param train_crop_size: length of side of the square that we have to crop for passing to model
            for train dataset
        :type train_crop_size: int
        :param multilabel: boolean flag for whether the model is trained for multilabel
        :type multilabel: bool
        :param model_name: name of the model that is used by ModelFactory to retrieve the model
        :type model_name: str
        :param image_mean: mean for each channel
        :type image_mean: list[float]
        :param image_std: std for each channel
        :type image_std: list[float]
        :param featurizer: torch model that outputs features for an image
        :type featurizer: torch.nn.module
        """
        self._model = model
        self._number_of_classes = number_of_classes
        self._multilabel = multilabel
        self._model_name = model_name
        self._valid_resize_size = valid_resize_size
        self._valid_crop_size = valid_crop_size
        self._train_crop_size = train_crop_size
        self._image_mean = image_mean
        self._image_std = image_std
        self._featurizer = featurizer
        self._featurizer.eval()

        self._distributed = False
        self._labels = None

    def _get_model_output(self, input_tensor):
        """Do a forward pass on the model.

        :param input_tensor: torch tensor representing the images
        :type input_tensor: torch.Tensor
        :return: model output
        :rtype: torch.Tensor
        """
        output = None
        is_model_train = self.model.training
        self.model.eval()
        with torch.no_grad():
            output = self.model(input_tensor)
        # restore model training mode
        if is_model_train:
            self.model.train()
        return output

    def _get_multilabel_preds(self, outputs, cutoff_for_multilabel=0.5):
        """
        :param outputs: model output from forward pass
        :type outputs: torch.Tensor
        :param cutoff_for_multilabel: cutoff for multilabel
        :type cutoff_for_multilabel: torch.Tensor
        :return: one hot encoded prediction
        :rtype: torch.Tensor
        """
        outputs = torch.sigmoid(outputs)
        return (outputs > cutoff_for_multilabel).type(torch.float)

    @property
    def featurizer(self):
        """Return featurizer."""
        return self._featurizer

    @property
    def model(self):
        """Model."""
        return self._model

    @model.setter
    def model(self, model):
        self._model = model

    @property
    def model_name(self):
        """Name of the model."""
        return self._model_name

    def predict_probs_from_outputs(self, outputs=None):
        """
        :param outputs: model output from forward pass
        :type outputs: torch.Tensor
        :return: num_images x num_classes tensor
        :rtype: torch.Tensor
        """
        if self._multilabel:
            probs = torch.sigmoid(outputs)
        else:
            probs = torch.softmax(outputs, dim=-1)

        return probs

    def export_onnx_model(self, file_path=ArtifactLiterals.ONNX_MODEL_FILE_NAME, device=None, enable_norm=False):
        """
        Export the pytorch model to onnx model file.

        :param file_path: file path to save the exported onnx model.
        :type file_path: str
        :param device: device where model should be run (usually 'cpu' or 'cuda:0' if it is the first gpu)
        :type device: str
        :param enable_norm: enable normalization when exporting onnx
        :type enable_norm: bool
        """
        onnx_export_start = time.time()

        class ModelNormalizerWrapper(torch.nn.Module):
            def __init__(self, model,
                         mean=ModelParameters.DEFAULT_IMAGE_MEAN, std=ModelParameters.DEFAULT_IMAGE_STD):
                super(ModelNormalizerWrapper, self).__init__()
                self.model = model
                self.mean = mean
                self.std = std

            def forward(self, x):
                norm_x = self.normalize(x)
                output = self.model(norm_x)
                return output

            def normalize(self, imgs):
                # https://discuss.pytorch.org/t/tracerwarning-there-are-2-live-references-to-the-data-region-being-modified-when-tracing-in-place-operator-copy/68704/2
                new_imgs = imgs.clone()
                new_imgs /= 255
                # R
                new_imgs = torch.cat(((new_imgs[:, 0:1, :, :] - self.mean[0]) / self.std[0],
                                      new_imgs[:, 1:, :, :]), dim=1)
                # G
                new_imgs = torch.cat((new_imgs[:, 0:1, :, :],
                                      (new_imgs[:, 1:2, :, :] - self.mean[1]) / self.std[1],
                                      new_imgs[:, 2:, :, :]), dim=1)
                # B
                new_imgs = torch.cat((new_imgs[:, :2, :, :],
                                      (new_imgs[:, 2:, :, :] - self.mean[2]) / self.std[2]), dim=1)
                return new_imgs

        dummy_input = torch.rand(1, 3, self.valid_crop_size, self.valid_crop_size,
                                 device=device, requires_grad=False)
        model = self._model.module if self._distributed else self._model
        if device is not None:
            model.to(device=device)
        model.eval()
        new_model = model
        if enable_norm:
            dummy_input *= 255.
            new_model = ModelNormalizerWrapper(model, self._image_mean, self._image_std)
        torch.onnx.export(new_model,
                          dummy_input,
                          file_path,
                          do_constant_folding=True,
                          input_names=['input1'],
                          output_names=['output1'],
                          dynamic_axes={'input1': {0: 'batch'}, 'output1': {0: 'batch'}})
        onnx_export_time = time.time() - onnx_export_start
        logger.info('ONNX ({}) export time {:.2f}s with enable_onnx_normalization ({})'
                    .format(file_path, onnx_export_time, enable_norm))

    @property
    def valid_resize_size(self):
        """Size to which to resize before cropping for validation dataset."""
        return self._valid_resize_size

    @property
    def valid_crop_size(self):
        """Size to which to crop for validation dataset."""
        return self._valid_crop_size

    @property
    def train_crop_size(self):
        """Size to which to crop for train dataset."""
        return self._train_crop_size

    @property
    def model_settings(self):
        """Get model settings

        :return: model settings
        :rtype: dict
        """
        model_settings = {ModelLiterals.VALID_RESIZE_SIZE: self.valid_resize_size,
                          ModelLiterals.VALID_CROP_SIZE: self.valid_crop_size,
                          ModelLiterals.TRAIN_CROP_SIZE: self.train_crop_size}
        return model_settings

    @property
    def distributed(self):
        """Get if the model is a DistributedDataParallel model.

        :return: distributed
        :rtype: bool
        """
        return self._distributed

    @distributed.setter
    def distributed(self, value):
        """Set flag to indicate that the model is a DistributedDataParallel model.

        :param value: distributed
        :type value: bool
        """
        self._distributed = value

    @property
    def number_of_classes(self):
        """Get the number of classes

        :return: number of classes for this model
        :rtype: int
        """
        return self._number_of_classes

    @property
    def multilabel(self):
        """Returns True if the model is multilabel

        :return: if model is multilabel or not
        :rtype: bool
        """
        return self._multilabel

    @property
    def labels(self):
        """List of string labels.

        :return: the list of labels
        :rtype: list
        """
        return self._labels

    @labels.setter
    def labels(self, value):
        """Set the list of string labels.

        :param value: the list of labels
        :type value: list
        """
        self._labels = value

    def state_dict(self):
        """Get the state dictionary from PyTorch model.

        :return: State dictionary.
        :rtype: dict
        """
        if self._distributed:
            return self._model.module.state_dict()
        return self._model.state_dict()

    def load_state_dict(self, state_dict):
        """Set the state dictionary for PyTorch model.

        :param state_dict: State dictionary
        :type state_dict: dict
        """
        if self._distributed:
            self._model.module.load_state_dict(state_dict)
        else:
            self._model.load_state_dict(state_dict)

    def to_device(self, device):
        """Move the model to the given device.

        :param device: torch device
        :type device: torch.device
        """
        if device is None:
            msg = 'Cannot transfer model wrapper to a None device'
            logger.error(msg)
            raise AutoMLVisionSystemException(msg, has_pii=False)

        self._model.to(device)
        self._featurizer.to(device)
