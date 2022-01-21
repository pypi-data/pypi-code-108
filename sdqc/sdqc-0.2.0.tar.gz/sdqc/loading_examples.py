import os
import json


def read_data_william_artifacts(file_name, diff_file=None):
    """
    Reads the data from WILIAM's artifacts to create a valid dictionary
    for loading external objects.

    Parameters
    ----------
    file_name: str
        Name of the json file with the symbols information.
    diff_file: str (Optional)
        Name of the diff file from artifacts, will provide a dictionary
        only with the new ones. By default it is None, all symbols in
        file_name will be checked.

    Returns
    -------
    elements: dict
        Dictionary of elements compatible with the loading function.

    """
    json_dict = json.load(open(file_name,))[0]['symbols']
    root = os.path.split(file_name)[0]

    if diff_file:
        # TODO define which list should be passed
        new = json.load(open(diff_file,))[0]['symbols']['not_found_in_DB']
        elements_to_read = {key: json_dict[key] for key in new}
    else:
        elements_to_read = json_dict

    elements = {}
    for element, data in elements_to_read.items():
        if data['type'] == 'SUBSCRIPT':
            # subscript elements
            elements[element] = {'type': 'SUBSCRIPT',
                                 'values': data['dependencies']}
        elif 'excels' in data:
            # excel elements
            elements[element] = {'type': 'EXTERNAL',
                                 'excel': []}
            for sheet in data['excels']:
                for info in sheet['info']:
                    elements[element]['excel'].append(
                        {'filename': sheet.get('filename'),
                         'sheet': sheet.get('sheet'),
                         'cell': info.get('cellrange'),
                         'x_row_or_cols': info.get('series'),
                         'subs': info.get('indexes'),
                         'root': root}
                    )
    return elements
