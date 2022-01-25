"""This module provide multiple function that convert data"""
import os


def change_resolution_value(new_res_val: str, file: str, line_idx: int = 0) -> dict:
    """
    This method update the first line of tfw file with the provided "new_res_val" - replace the line
    :param new_res_val: The new resolution value to be updated
    :param file: Full directory of tfw file to be changed
    :param line_idx: line on file to replace -> as default the first line, index=0
    :return: dict -> {success: True/False, reason: failure message | None if success}
    """
    result = {"success": True, "reason": None}
    try:
        fp = open(file, "r")
        temp_lines_list = fp.readlines()
        temp_lines_list[line_idx] = new_res_val + '\n'
        fp.close()

        fp = open(file, "w")
        fp.writelines(temp_lines_list)
        fp.close()
        result["reason"] = f"Change resolution into file {file} to value: [{new_res_val}]"

    except Exception as e:
        result["success"] = False
        result["reason"] = str(e)

    return result


def replace_discrete_resolution(discrete_directory: str, new_val: str, ext: str = 'tfw') -> list:
    """
    This method get directory of discrete source data and replace and update max resolution parameter on all included
    files (as default - .tfw)
    :param discrete_directory: parent directory of discrete
    :param new_val: new value to be update on relevant files
    :param ext: The files extensions to replace on
    :return: list -> [list of replaced files name]
    """
    # collect all relevant files
    list_of_files = []
    results = []
    for root, subFolders, files in os.walk(discrete_directory):
        if files:
            list_of_files = list_of_files + [os.path.join(root, file) for file in files if file.endswith('.' + ext)]

    # update each file
    for file in list_of_files:
        results.append(change_resolution_value(new_val, file))

    return results
