from . import access, context


def get(
    ctx,
    org_id=None,
    dt_sort=None,
    dt_from=None,
    dt_to=None,
    app=None,
    sub_org_id=None,
    limit=None,
    **kwargs,
):
    token = context.get_token(ctx)
    if not token:
        access_token = access.get_access_token(ctx)
        token = access_token.get()

    if not org_id:
        org_id = context.get_org_id(ctx, token)

    apiclient = context.get_apiclient(ctx, token)

    params = {}
    params["dt_from"] = dt_from
    params["dt_sort"] = dt_sort
    params["dt_to"] = dt_to
    params["sub_org_id"] = sub_org_id

    if app:
        params["app"] = app
    if limit:
        params["limit"] = int(limit)

    resp = apiclient.logs_api.list_logs(org_id, **params)

    return resp.logs
