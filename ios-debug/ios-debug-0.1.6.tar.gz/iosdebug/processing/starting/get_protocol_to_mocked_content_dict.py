def get_protocol_to_mocked_content_dict(repository_protocols, path_to_content_map):
    protocol_to_mocked_contents = {}

    for protocol in repository_protocols:
        for file_path in path_to_content_map:
            if "protocol " + protocol in path_to_content_map[file_path]:
                with open(file_path, "r") as file:
                    content = file.read()
                content_split = content.split("// MARK: - Mock implementation init")
                mocked_content = content_split[1][1:]
                protocol_to_mocked_contents[protocol] = mocked_content
    return protocol_to_mocked_contents
