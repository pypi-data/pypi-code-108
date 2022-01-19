import os
import sys


is_async = os.environ.get('AZUREML_ASYNC_SERVING')

instance = None
if not is_async:
    from synchronous.framework import *
else:
    from asynchronous.framework import *
instance = Framework()

# override the azureml.contrib.services package with local one, meanwhile keep the other stuff under azureml.* untouched
# note this must be done prior to importing the package in app logic
import azureml.contrib.services.aml_request
import azureml_contrib_services.aml_request
# works for 'import azureml.contrib.services.aml_request'
sys.modules["azureml.contrib.services"].aml_request = sys.modules["azureml_contrib_services"].aml_request
# works for 'from azureml.contrib.services.aml_request import *'
sys.modules["azureml.contrib.services.aml_request"] = sys.modules["azureml_contrib_services.aml_request"]

import azureml.contrib.services.aml_response
import azureml_contrib_services.aml_response
# works for 'import azureml.contrib.services.aml_response'
sys.modules["azureml.contrib.services"].aml_response = sys.modules["azureml_contrib_services"].aml_response
# works for 'from azureml.contrib.services.aml_response import *'
sys.modules["azureml.contrib.services.aml_response"] = sys.modules["azureml_contrib_services.aml_response"]
