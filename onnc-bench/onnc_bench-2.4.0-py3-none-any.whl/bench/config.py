import os
from os.path import expanduser
import requests
from typing import Union

from .core.compiler.onnc_saas import ONNCSaaSBuilder

from .core.compiler.builder import IBuilder
try:
    if int(os.environ['ONNC_TESTMODE']):
        api_host = 'http://127.0.0.1:8000'
except KeyError:
    api_host = 'https://api.onnc.skymizer.com'

onnc_key_var = 'ONNC_APIKEY'


api_protocol = 'https'
api_url = "api.onnc.skymizer.com"
api_port = 443

image_name = 'registry.skymizer.com/nnuxe/nnuxe/nnuxe_image'
image_tag = "v0.0.4-test"

default_builder: IBuilder
try:
    if os.environ['BENCH_COMPILER'] == "NNUXE":
        from .core.compiler.nnuxe import NNUXEBuilder

        default_builder = NNUXEBuilder
        default_builder_params = []
    elif os.environ['BENCH_COMPILER'] == "NNUXE_DOCKER":
        from .core.compiler.nnuxe_docker import NNUXEDockerBuilder

        default_builder = NNUXEDockerBuilder
        default_builder_params = [image_name, image_tag]
    else:
        default_builder = ONNCSaaSBuilder
        default_builder_params = [api_protocol, api_url, api_port]
except KeyError:
    default_builder = ONNCSaaSBuilder
    default_builder_params = [api_protocol, api_url, api_port]
