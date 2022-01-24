from azureml.automl.dnn.vision.common.pretrained_model_utilities import PretrainedModelFactory
from azureml.automl.dnn.vision.object_detection.models.base_model_wrapper import \
    BaseObjectDetectionModelWrapper
from azureml.automl.dnn.vision.common.constants import PretrainedModelNames


class CocoBaseModelWrapper(BaseObjectDetectionModelWrapper):
    num_classes = 91

    @property
    def model(self):
        """Returns the wrapped model."""
        return self._model

    @model.setter
    def model(self, value):
        """Sets the wrapped model.

        :param value: the model
        :type value: nn.Module
        """
        self._model = value

    def __init__(self) -> None:
        super().__init__(model_name=PretrainedModelNames.FASTERRCNN_RESNET50_FPN_COCO,
                         number_of_classes=CocoBaseModelWrapper.num_classes)
        self._model = self._create_model()

    def _create_model(self):
        return PretrainedModelFactory.fasterrcnn_resnet50_fpn(pretrained=True)
