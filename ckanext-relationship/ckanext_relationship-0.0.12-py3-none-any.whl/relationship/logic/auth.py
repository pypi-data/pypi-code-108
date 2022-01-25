from ckan.plugins import toolkit as tk


_auth = {}


def auth(func):
    func.__name__ = f'relationship_{func.__name__}'
    _auth[func.__name__] = func
    return func


def get_auth_functions():
    return _auth.copy()


@auth
def relation_create(context, data_dict):
    return {'success': True}


@auth
@tk.auth_allow_anonymous_access
def relations_list(context, data_dict):
    return {'success': True}


@auth
def relation_delete(context, data_dict):
    return {'success': True}

@auth
@tk.auth_allow_anonymous_access
def get_entity_list(context, data_dict):
    return {'success': True}
