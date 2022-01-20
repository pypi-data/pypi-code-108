import datetime
import json
import shutil
import urllib.parse

import requests

from . import context, hash, response

FILES_BASE_URI = "/v1/files"


def query(ctx, org_id=None, tag=None, **kwargs):
    token = context.get_token(ctx)

    headers = {}
    headers["Authorization"] = "Bearer {}".format(token)

    params = {}

    if org_id:
        params["org_id"] = org_id
    else:
        org_id = context.get_org_id(ctx, token)
        if org_id:
            params["org_id"] = org_id

    if tag:
        params["tag"] = tag

    query = urllib.parse.urlencode(params)
    uri = "{}?{}".format(FILES_BASE_URI, query)
    resp = requests.get(
        context.get_api(ctx) + uri,
        headers=headers,
        verify=context.get_cacert(ctx),
    )
    response.validate(resp)
    return json.loads(resp.text)["files"]


def upload(
    ctx,
    filename,
    region=None,
    org_id=None,
    tag=None,
    name=None,
    label=None,
    visibility=None,
    **kwargs,
):
    token = context.get_token(ctx)

    headers = {}
    headers["Authorization"] = "Bearer {}".format(token)

    if not name:
        name = filename

    if not label:
        label = datetime.datetime.utcnow().isoformat()

    md5_hash = hash.get_base64_md5(filename)

    multipart_form_data = {}
    multipart_form_data["md5_hash"] = md5_hash
    multipart_form_data["file_zip"] = (name, open(filename, "rb"))

    if org_id:
        multipart_form_data["org_id"] = (None, org_id)
    else:
        multipart_form_data["org_id"] = (None, context.get_org_id(ctx, token))

    if tag:
        multipart_form_data["tag"] = (None, tag)

    if region:
        multipart_form_data["region"] = (None, region)

    if name:
        multipart_form_data["name"] = (None, name)

    if label:
        multipart_form_data["label"] = (None, label)

    if visibility:
        multipart_form_data["visibility"] = (None, visibility)

    uri = "{}".format(FILES_BASE_URI)
    resp = requests.post(
        context.get_api(ctx) + uri,
        headers=headers,
        files=multipart_form_data,
        verify=context.get_cacert(ctx),
        timeout=60,
    )
    response.validate(resp)
    return json.loads(resp.text)


def delete(ctx, file_id, org_id=None, _continue_on_error=False):
    token = context.get_token(ctx)

    headers = {}
    headers["Authorization"] = "Bearer {}".format(token)

    params = {}

    if org_id:
        params["org_id"] = org_id
    else:
        org_id = context.get_org_id(ctx, token)
        if org_id:
            params["org_id"] = org_id

    query = urllib.parse.urlencode(params)
    uri = "{}/{}?{}".format(FILES_BASE_URI, file_id, query)
    resp = requests.delete(
        context.get_api(ctx) + uri,
        headers=headers,
        verify=context.get_cacert(ctx),
    )
    response.validate(resp, _continue_on_error=_continue_on_error)
    return resp.text


def get(ctx, file_id, org_id=None):
    token = context.get_token(ctx)

    headers = {}
    headers["Authorization"] = "Bearer {}".format(token)

    params = {}

    if org_id:
        params["org_id"] = org_id
    else:
        org_id = context.get_org_id(ctx, token)
        if org_id:
            params["org_id"] = org_id

    query = urllib.parse.urlencode(params)
    uri = "{}/{}?{}".format(FILES_BASE_URI, file_id, query)
    resp = requests.get(
        context.get_api(ctx) + uri,
        headers=headers,
        verify=context.get_cacert(ctx),
    )
    response.validate(resp)
    return json.loads(resp.text)


def download(ctx, file_id, org_id=None, destination=None):
    token = context.get_token(ctx)

    headers = {}
    headers["Authorization"] = "Bearer {}".format(token)

    params = {}

    if org_id:
        params["org_id"] = org_id
    else:
        org_id = context.get_org_id(ctx, token)
        if org_id:
            params["org_id"] = org_id

    if not destination:
        _file = get(ctx, file_id, org_id)
        destination = _file["name"]

    query = urllib.parse.urlencode(params)
    uri = "{}_download/{}?{}".format(FILES_BASE_URI, file_id, query)
    with requests.get(
        context.get_api(ctx) + uri,
        headers=headers,
        verify=context.get_cacert(ctx),
        stream=True,
    ) as handle:
        handle.raise_for_status()
        with open(destination, "wb") as f:
            shutil.copyfileobj(handle.raw, f)
