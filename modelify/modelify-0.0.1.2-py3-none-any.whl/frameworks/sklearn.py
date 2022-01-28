from onnxmltools.convert import convert_sklearn
from modelify.schema import InputList
from modelify.frameworks import BaseController
from modelify.utils import message


class SklearnController(BaseController):
    def __init__(self):
        self.name = "SKLEARN"
        super().__init__()

    def deploy(self, model_name, model, inputs:InputList, version=9):
        message("Model is converting...")
        export_path, file_name = self.export_model(model, inputs=inputs, version=version)
        message("Model converted successfully")
        super().upload_pipeline(framework_name= self.name, export_path=export_path, file_name=file_name,
         model_name=model_name, inputs=inputs,input_type=inputs.type)
        message("Done")

    def update(self, model_name, model, inputs:InputList, version=9):
        message("Model is converting...")
        export_path, file_name = self.export_model(model, inputs=inputs, version=version)
        message("Model converted successfully")
        super().upload_pipeline(framework_name= self.name, export_path=export_path, file_name=file_name,
         model_name=model_name, inputs=inputs,input_type=inputs.type, update=True)
        message("Done")

        

    def export_model(self, model, inputs:InputList, version):
        initial_type = inputs.convert_onnx()
        onnx = convert_sklearn(model, initial_types=initial_type, target_opset=version)
        export_path, file_name = super().save_onnx_file(onnx)

        return export_path, file_name


