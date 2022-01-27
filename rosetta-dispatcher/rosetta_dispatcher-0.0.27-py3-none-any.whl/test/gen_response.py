import json

from rosetta_dispatcher.model.dispatch_request_model import DispatchRequestModel
from rosetta_dispatcher.model.dispatch_response_model import DispatchResponseModel

reply_to = "a946e098-7674-11eb-8ee6-00163e140fb1"
correlation_id = "a946e099-7674-11eb-8ee6-00163e140fb1"

data = []
data = {'source_language': 'zh',
        'target_language': 'en',
        'chapter_content': [],
        'model_version': '1.0.0'}

response = DispatchResponseModel(correlation_id=correlation_id, data=json.dumps(data))
strresponse = json.dumps(response.dict(), ensure_ascii=True)

print(f'rpush {reply_to} \'{strresponse}\'')
