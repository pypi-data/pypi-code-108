def create_path_to_content_dict(swift_files):
    path_to_content_map = {}

    for file_path in swift_files:
        with open(file_path, "r") as file:
            content = file.read()
            path_to_content_map[file_path] = content

    return path_to_content_map
