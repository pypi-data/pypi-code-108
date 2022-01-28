from onnxmltools.convert import convert_keras
from modelify.frameworks import BaseController
from modelify.utils import message
import tf2onnx


class KerasController(BaseController):
    def __init__(self):
        self.name = "KERAS"
        super().__init__()
        tf2onnx.logging.set_level(20)

    def deploy(self, model_name, model, inputs, version=9):
        message("Model is converting...")
        export_path, file_name = self.export_model(model, inputs=inputs, version=version)
        message("Model converted successfully")
        super().upload_pipeline(framework_name= self.name, export_path=export_path, file_name=file_name,
         model_name=model_name, inputs=inputs,input_type=inputs.type)
        message("Done")

    def update(self, model_name, model, inputs, version=9):
        message("Model is converting...")
        export_path, file_name = self.export_model(model, inputs=inputs, version=version)
        message("Model converted successfully")
        super().upload_pipeline(framework_name= self.name, export_path=export_path, file_name=file_name,
         model_name=model_name, inputs=inputs,input_type=inputs.type, update=True)
        message("Done")

        

    def export_model(self, model, inputs, version):
        onnx = convert_keras(model)
        export_path, file_name = super().save_onnx_file(onnx)

        return export_path, file_name


