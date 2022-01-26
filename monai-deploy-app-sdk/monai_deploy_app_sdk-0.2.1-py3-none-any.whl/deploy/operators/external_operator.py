# # Copyright 2021 MONAI Consortium
# # Licensed under the Apache License, Version 2.0 (the "License");
# # you may not use this file except in compliance with the License.
# # You may obtain a copy of the License at
# #     http://www.apache.org/licenses/LICENSE-2.0
# # Unless required by applicable law or agreed to in writing, software
# # distributed under the License is distributed on an "AS IS" BASIS,
# # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# # See the License for the specific language governing permissions and
# # limitations under the License.

# from abc import abstractclassmethod, abstractmethod
# from typing import Dict

# import os
# import monai.deploy.core as md
# from monai.deploy.core import ExecutionContext, InputContext, Operator, OutputContext
# from monai.deploy.exceptions import MONAIAppSdkError

# @md.env(pip_packages=["docker"])
# class ExternalOperator(Operator):
#     """ """

#     @abstractclassmethod
#     def get_volume_mapping(
#         self, op_input: InputContext, op_output: OutputContext, context: ExecutionContext
#     ) -> Dict[str, Dict[str, str]]:

#         return {
#             # os.path.abspath(os.curdir): {"bind": "/var/monai/workspace", "mode": "rw"},
#             op_input.get().path: {'bind': '/input', 'mode': 'ro'},
#             op_output.get().path: {'bind': '/output', 'mode': 'rw'},
#         }

#     def compute(self, op_input: InputContext, op_output: OutputContext, context: ExecutionContext):
#         import json

#         import docker

#         # Set current output directory if not set
#         if op_output.get() is None:
#             op_output.set(".")

#         client = docker.from_env()

#         config = {
#             # "working_dir": "/var/monai/workspace",
#             "shm_size": "1g",
#             "volumes": self.get_volume_mapping(op_input, op_output, context),
#         }

#         container = client.containers.run("ubuntu:18.04", "echo hello", detach=True, **config)
#         status = container.wait()
#         if status["StatusCode"] != 0:
#             print(container.logs())
#             raise MONAIAppSdkError("Docker exited with non-zero status code")
#         stdout = container.logs(stdout=True, stderr=False).decode("utf-8")
#         stderr = container.logs(stdout=False, stderr=True).decode("utf-8")
#         container.remove()

#         output_folder = op_output.get().path

#         # Write result to "output.json"
#         output_path = output_folder / "output.json"
#         with open(output_path, "w") as fp:
#             json.dump({"output": stdout}, fp)

#         # {'Error': None, 'StatusCode': 0}

#         # Launch external process with input and output
#         # Wait for completion
#         # Return output

#         # input_path = op_input.get("image")
#         # output_dir = op_output.get().path
#         # output_dir.mkdir(parents=True, exist_ok=True)
#         # self.convert_and_save(input_path, output_dir)

# def main():
#     pass


# if __name__ == "__main__":
#     main()
