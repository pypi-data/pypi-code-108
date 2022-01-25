def add_datalab_project_ace(data_lab_project_id, ace_input, items_api):
    if data_lab_project_id:
        items_api.add_access_control_entry(id=data_lab_project_id, body=ace_input)


def set_addon_permissions(identity_id, tool_id, items_api):
    # Add permissions to the add-on tool
    ace_input = {'identityId': identity_id, 'permissions': {'read': True}}
    items_api.add_access_control_entry(id=tool_id, body=ace_input)


def datalab_permissions(identity_id, data_lab_project_id, items_api):
    # Add permissions to the add-on tool
    ace_input = {'identityId': identity_id,
                 'permissions': {'read': True,
                                 'write': True}}  # Data lab project also needs write permission
    add_datalab_project_ace(data_lab_project_id, ace_input, items_api)


def get_addon_permissions(tool_id, items_api):
    entries = items_api.get_access_control(id=tool_id).entries

    groups = [x.identity.name for x in entries if x.identity.type == "UserGroup"]
    users = [x.identity.username for x in entries if x.identity.type == "User"]

    return {"Groups": groups, "Users": users}


def remove_addon_permissions(tool_id, type_, items_api):
    entries = items_api.get_access_control(id=tool_id).entries
    # remove previous permissions
    entries_filtered = [x for x in entries if x.identity.type == type_]
    for entry in entries_filtered:
        items_api.remove_access_control_entry(id=tool_id, ace_id=entry.id)
