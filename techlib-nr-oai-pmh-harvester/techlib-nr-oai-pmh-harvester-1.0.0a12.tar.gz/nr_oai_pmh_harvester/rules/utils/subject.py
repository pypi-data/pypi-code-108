def fix_mesh(taxonomy_list: list):
    new_list = []
    for item in taxonomy_list:
        tree_number_list = item.get('TreeNumberList')
        if tree_number_list:
            if isinstance(tree_number_list, str):
                tree_number_list_new: list = eval(tree_number_list)
                assert isinstance(tree_number_list_new, list)
                item['TreeNumberList'] = tree_number_list_new
            new_list.append(item)
        else:
            new_list.append(item)
    return new_list
