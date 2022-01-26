import re


class Mappings:
    def __init__(self, mappings_list, arguments):
        self.mappings_dict = {}
        for mapping in mappings_list:
            from_path, to_path = self.replace_dollar_variables_and_validate(mapping['from_path'],
                                                                            mapping['to_path'], arguments)
            self.mappings_dict[from_path] = to_path

    def get_mappings_for_path(self, path):
        mapped_file_names = []
        for from_path, to_path in self.mappings_dict.items():
            if (from_path.endswith('/') and path.startswith(from_path)) or path == from_path:

                # Mapping from dir to dir
                if from_path.endswith('/'):
                    mapped_file_names.append(to_path + path[len(from_path):])

                # Mapping from a file
                else:
                    # Mapping file to dir
                    if to_path.endswith('/'):
                        mapped_file_names.append(to_path + path.split('/')[-1])
                    # Mapping file to file
                    else:
                        mapped_file_names.append(to_path)

        return mapped_file_names

    def replace_dollar_variables_and_validate(self, from_path, to_path, arguments):
        from_path = self.replace_dollar_with_arg(from_path, arguments)
        to_path = self.replace_dollar_with_arg(to_path, arguments)

        assert_path_validity(from_path)
        assert_path_validity(to_path)

        return from_path, to_path

    def replace_dollar_with_arg(self, path, args):
        for arg_index in re.findall(r'\$(\d+)', path):
            if arg_index == '0':
                raise Exception('Attempted to substitute argument 0 which is invalid')

            if arg_index < len(args):
                raise Exception('Referred to an argument index out of bounds of arguments')

            path = path.replace(f'${arg_index}', args[int(arg_index) - 1])
        return path


def path_without_first_folder(path):
    """
    Removes the first folder in a relative path.
    example/test.txt -> test.txt
    some_dir/some_sub_dir/test.txt -> some_sub_dir/test.txt
    """
    return path.split('/', 1)[1]


def assert_path_validity(path: str):
    if not path.startswith('/'):
        raise Exception('Path must be absolute')

    if '//' in path:
        raise Exception('Path can not include consecutive slashes')

    if '/..' in path:
        raise Exception('Path can not include ".."')
