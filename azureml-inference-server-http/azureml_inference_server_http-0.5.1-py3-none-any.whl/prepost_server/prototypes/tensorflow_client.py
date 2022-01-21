from aiohttp import ClientSession
import requests
import grpc
import tensorflow as tf
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc

from prepost.clients.model_server_client import ModelServerClient


class TFClient(ModelServerClient):
    async def invoke_tf_serving_rest_async(aiohttp_session: ClientSession, data):
        payload = {"signature_name": "serving_default", "instances": data}
        # print(payload)
        headers = {"Content-Type": "application/json"}
        async with aiohttp_session.post(
            "http://localhost:8501/v1/models/fashion_model:predict", headers=headers, json=payload
        ) as r:
            json = await r.json()
            return json["predictions"]

    async def invoke_tf_serving_grpc_async(data):
        request = predict_pb2.PredictRequest()
        request.model_spec.name = "fashion_model"
        request.model_spec.signature_name = "serving_default"
        request.inputs["Conv1_input"].CopyFrom(tf.make_tensor_proto(data, shape=[1, 28, 28, 1]))

        async with grpc.aio.insecure_channel("localhost:8500") as channel:
            stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)
            result = await stub.Predict(request)
            print(result.outputs["Dense"].float_val)
            return [result.outputs["Dense"].float_val]
