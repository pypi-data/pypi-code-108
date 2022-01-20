import re


def find_repository_protocols(path_to_content_map):
    print("Looking for repository protocols.")
    repository_protocols = []

    for file_path in path_to_content_map:
        content = path_to_content_map[file_path]
        repository_definition = re.findall(r"class .*Repository.*{[\s\S]*}", content)
        if repository_definition:
            protocol_conformance_row = re.findall(
                r"extension (\w+)" + "Impl: \\1 \{", repository_definition[0]
            )
            if protocol_conformance_row:
                repository_protocols.append(protocol_conformance_row[0])

    print("Found repositories:")
    _ = [print(repo) for repo in repository_protocols]
    print()
    return repository_protocols
