# import json
# import requests
#
# from origin.serialize import json_serializer
#
# from .models import GetMixEmissionsResponse
#
#
# class ConnectionError(Exception):
#     """
#     Raised when invoking EnergyTypeService results
#     in a connection error
#     """
#     pass
#
#
# class ServiceError(Exception):
#     """
#     Raised when invoking EnergyTypeService results
#     in a status code != 200
#     """
#     def __init__(self, msg, status_code=None, response_body=None):
#         super(ServiceError, self).__init__(msg)
#         self.status_code = status_code
#         self.response_body = response_body
#
#
# # class ServiceUnavailable(Exception):
# #     """
# #     Raised when requesting energy type which is unavailable
# #     for the requested GSRN
# #     """
# #     pass
#
#
# class ServiceClient(object):
#     """
#     TODO
#     """
#     def __init__(self, base_url: str, debug: bool = False):
#         """
#         :param base_url:
#         """
#         self.base_url = base_url
#         self.debug = debug
#
#     def get_url(self, path: str):
#         """
#         :param path:
#         :return:
#         """
#         return f'{self.base_url}{path}'
#
#     def invoke(self, func, path, query, response_schema):
#         """
#         :param Callable func:
#         :param str path:
#         :param dict query:
#         :param Schema response_schema:
#         :rtype obj:
#         """
#         headers = {
#             'Content-type': 'application/json',
#             'accept': 'application/json',
#         }
#
#         url = self.get_url(path)
#
#         try:
#             response = func(
#                 url=url,
#                 params=query,
#                 verify=not self.debug,
#                 headers=headers,
#             )
#         except Exception as e:
#             raise ConnectionError(f'Failed to request request service: {e}')
#
#         if response.status_code != 200:
#             raise ServiceError(
#                 status_code=response.status_code,
#                 response_body=response.content.decode(),
#                 msg=(
#                     f'Request resulted in status {response.status_code}: '
#                     f'{url}\n\n{response.content}'
#                 ),
#             )
#
#         return json_serializer.deserialize(
#             data=response.content,
#             schema=response_schema,
#         )
#
#         # try:
#         #     response = json_serializer.deserialize(
#         #         data=response.content,
#         #         schema=response_schema,
#         #     )
#         #     # response_json = response.json()
#         #     # response_model = response_schema().load(response_json)
#         # except json.decoder.JSONDecodeError:
#         #     raise ServiceError(
#         #         f'Failed to parse response JSON: {url}\n\n{response.content}',  # noqa: E501
#         #         status_code=response.status_code,
#         #         response_body=str(response.content),
#         #     )
#         # except marshmallow.ValidationError as e:
#         #     raise ServiceError(
#         #         f'Failed to validate response JSON: {url}\n\n{response.content}\n\n{str(e)}', # noqa: E501
#         #         status_code=response.status_code,
#         #         response_body=str(response.content),
#         #     )
#         #
#         # return response
#
#     def get(self, *args, **kwargs):
#         return self.invoke(requests.get, *args, **kwargs)
#
#     def post(self, *args, **kwargs):
#         return self.invoke(requests.post, *args, **kwargs)
#
#     def get_residual_mix(self, sector, begin_from, begin_to) -> GetMixEmissionsResponse:  # noqa: E501
#         """
#         Returns a dict of emission data for a MeteringPoint.
#         :param list[str] sector:
#         :param datetime.datetime begin_from:
#         :param datetime.datetime begin_to:
#         :rtype: GetMixEmissionsResponse
#         """
#         return self.get(
#             path='/residual-mix',
#             response_schema=GetMixEmissionsResponse,
#             query={
#                 'sector': sector,
#                 'begin_from': begin_from.isoformat(),
#                 'begin_to': begin_to.isoformat(),
#             },
#         )
