import lusid_drive


def name_to_id(item_list, target_item):
    item_id = [obj.id for obj in item_list.values if obj.name == target_item]

    if len(item_id) != 1:
        # TODO: raise an exception due to no matching item name, or multiple matches
        pass

    else:
        return item_id[0]


# a path to id function would be useful to build here...


def get_folder_id(api_factory, folder_name):
    folders_api = api_factory.build(lusid_drive.api.FoldersApi)
    response = folders_api.get_root_folder()
    folder_id = name_to_id(response, folder_name)

    return folder_id


def get_file_id(api_factory, file_name, folder_id):
    folders_api = api_factory.build(lusid_drive.api.FoldersApi)
    response = folders_api.get_folder_contents(folder_id)
    file_id = name_to_id(response, file_name)

    return file_id




