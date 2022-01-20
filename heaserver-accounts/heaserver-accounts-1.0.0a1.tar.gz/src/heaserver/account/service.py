"""
The HEA Server AWS Accounts Microservice provides ...
"""

from heaserver.service.runner import init_cmd_line, routes, start, web
from heaserver.service.db import awsservicelib, mongo
from heaserver.service.wstl import builder_factory, action


@routes.get('/volumes/{volume_id}/awsaccounts/me')
async def get_awsaccount(request: web.Request) -> web.Response:
    """
    Gets the AWS account associated with the given volume id. If the volume's credentials are None, it uses any
    credentials found by the AWS boto3 library.

    :param request: the HTTP request.
    :return: the requested AWS account or Not Found.
    ---
    summary: The user's AWS account.
    tags:
        - heaserver-accounts-get-awsaccount
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the user's AWS volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    return await awsservicelib.get_account(request, request.match_info["volume_id"])


@routes.post('/volumes/{volume_id}/awsaccounts/me')
async def post_account_awsaccounts(request: web.Request) -> web.Response:
    """
    Posts the awsaccounts information given the correct access key and secret access key
    :param request: the HTTP request.
    :return: the requested awsaccounts or Not Found.

    FIXME: should only be permitted by an AWS organization administrator, I would think. Need to sort out what the call looks like.
    """
    return await awsservicelib.post_account(request, request.match_info["volume_id"])


@routes.put('/volumes/{volume_id}/awsaccounts/me')
async def put_account_awsaccounts(request: web.Request) -> web.Response:
    """
    Puts the awsaccounts information given the correct access key and secret access key
    :param request: the HTTP request.
    :return: the requested awsaccounts or Not Found.
    """
    return await awsservicelib.put_account(request, request.match_info["volume_id"])


@routes.delete('/volumes/{volume_id}/awsaccounts/me')
async def delete_account_awsaccounts(request: web.Request) -> web.Response:
    """
    Deletes the awsaccounts information given the correct access key and secret access key
    :param request: the HTTP request.
    :return: the requested awsaccounts or Not Found.

    FIXME: should only be permitted by an AWS organization administrator, I would think. Need to sort out what the call looks like.
    """
    return await awsservicelib.delete_account(request, request.match_info["volume_id"])


def main() -> None:
    config = init_cmd_line(description='It manages account information details', default_port=8080)
    start(db=mongo.Mongo, wstl_builder_factory=builder_factory(__package__), config=config)
