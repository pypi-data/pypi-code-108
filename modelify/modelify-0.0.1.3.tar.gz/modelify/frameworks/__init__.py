
import shutil
import uuid
import os
import uuid
import requests
import json
from modelify.utils.constants import MODELIFY_PRESIGNED_URL, MODELIFY_DEPLOY_URL, MODELIFY_UPDATE_URL
from modelify.utils.credential import Credential
from modelify.utils import message
import pyminizip



class BaseController:
    def __init__(self):
        self.credential = Credential()

    def create_folder(self):
        current_folder = os.path.dirname(os.path.abspath(__file__))
        temp_folder = os.path.join(current_folder, "temp")
        unique_folder = os.path.join(temp_folder, uuid.uuid4().hex)
        os.makedirs(unique_folder)
        return unique_folder

    def delete_folder(self):
        current_folder = os.path.dirname(os.path.abspath(__file__))
        temp_folder = os.path.join(current_folder, "temp")
        folder_list = os.listdir(temp_folder)
        try:
            for folder in folder_list:
                shutil.rmtree(os.path.join(temp_folder, folder))
        except OSError as e:
            print("Error: %s : %s" % (temp_folder, e.strerror))


    def save_onnx_file(self, onnx_model, built_in=False):

        output_folder = self.create_folder()

        unique_name = uuid.uuid4().hex
        file_name = unique_name+ ".onnx"
        tar_file_name = unique_name + ".zip"
        output_file = os.path.join(output_folder, file_name)
        output_tar_file = os.path.join(output_folder, tar_file_name)

        if built_in:
            onnx_model.save_model(output_file, format="onnx")
        else:
            with open(output_file, "wb") as f:
                f.write(onnx_model.SerializeToString())

        compression_level = 5 # 1-9
        pyminizip.compress(output_file, None, output_tar_file, "password", compression_level)

        return output_tar_file , tar_file_name

    def upload_pipeline(self, framework_name, export_path, file_name, model_name, inputs, input_type, update=False):
        input_list = inputs.to_list()
        upload_url = self.get_presigned_url(file_name)
        self.upload_model_storage(upload_url, export_path)
        if update:
            self.update_model(framework_name, model_name, file_name, input_list, input_type=input_type)
        else:
            self.send_model(framework_name, model_name, file_name, input_list, input_type=input_type)
        self.delete_folder()

    def get_presigned_url(self ,object_name):
        data = {'object_name': object_name}
        headers = {"api-token": f"{self.credential.api_key}", "Content-Type": "application/json"}
        req = requests.post(MODELIFY_PRESIGNED_URL, json=data, headers = headers)

        if req.status_code == 200:
            res_data = req.json()
            if "url" in res_data:
                return res_data["url"]
            raise Exception("Url couldnt find")

        raise Exception("There is something wrong in the Modelify Server")

    def upload_model_storage(self,url, file_path):
        message("Upload process is starting")
        req = requests.put(url, open(file_path, 'rb') , headers= {'Content-Type': 'application/zip'})
        
        if req.status_code != 200:
            raise Exception("There is something wrong in model upload stage")

        message("Model uploaded successfully")

    def update_model(self, framework, model_name, file_name, inputs, input_type):
        message("New version is registering to your account")
        data = {'framework': framework, 'name': model_name, 'file_name':file_name, 'model_metadata': {'inputs' : inputs, 'input_type': input_type}}
        headers = {"api-token": f"{self.credential.api_key}", "Content-Type": "application/json"}
        req = requests.put(MODELIFY_UPDATE_URL, json=data, headers = headers)
        if req.status_code == 201:
            print("New version has been sent.")
        else:
            print(req.text)
            response_dict = json.loads(req.text)

            for i in response_dict:
                print("key: ", i, "val: ", response_dict[i])
            print("Something went wrong while model sending.")

    def send_model(self, framework, model_name, file_name, inputs, input_type):
        message("Model is registering to your account")
        data = {'framework': framework, 'name': model_name, 'file_name':file_name, 'model_metadata': {'inputs' : inputs, 'input_type': input_type}}
        headers = {"api-token": f"{self.credential.api_key}", "Content-Type": "application/json"}
        req = requests.post(MODELIFY_DEPLOY_URL, json=data, headers = headers)
        if req.status_code == 201:
            print("Model has been sent.")
        else:
            print(req.text)
            response_dict = json.loads(req.text)

            for i in response_dict:
                print("key: ", i, "val: ", response_dict[i])
            print("Something went wrong while model sending.")