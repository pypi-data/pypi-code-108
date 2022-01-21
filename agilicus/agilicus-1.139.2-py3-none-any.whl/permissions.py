from . import context
import agilicus


def query(ctx, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    query_results = apiclient.permissions_api.list_elevated_user_roles(**kwargs)
    if query_results:
        return query_results.elevated_permissions
    return []


def _get_elevated_user_roles(client, user_id, **kwargs):
    return client.permissions_api.get_elevated_user_roles(user_id, **kwargs)


def show(ctx, user_id, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)
    return _get_elevated_user_roles(apiclient, user_id, **kwargs)


def add(ctx, user_id, application, name, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)
    user_perms = _get_elevated_user_roles(apiclient, user_id, **kwargs)
    role_list = user_perms.roles
    if application not in role_list:
        role_list[application] = [name]
        request = agilicus.ReplaceUserRoleRequest(roles=role_list)
        return apiclient.permissions_api.replace_elevated_user_role(
            user_id, replace_user_role_request=request
        )
    return None


def delete(ctx, user_id, application, name, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)
    user_perms = _get_elevated_user_roles(apiclient, user_id, **kwargs)
    role_list = user_perms.roles.to_dict()
    if application in role_list:
        role_list.pop(application, None)
        request = agilicus.ReplaceUserRoleRequest(roles=agilicus.Roles(**role_list))
        return apiclient.permissions_api.replace_elevated_user_role(
            user_id, replace_user_role_request=request
        )
    return None


def clear(ctx, user_id, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)
    request = agilicus.ReplaceUserRoleRequest(roles={})
    return apiclient.permissions_api.replace_elevated_user_role(
        user_id, replace_user_role_request=request
    )
