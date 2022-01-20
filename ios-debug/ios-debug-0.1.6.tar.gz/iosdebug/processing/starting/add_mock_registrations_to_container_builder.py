import iosdebug.logger as logger
import re


def add_mock_registrations_to_container_builder(swift_files, registrations):
    print("Looking for ContainerBuilder.swift file...")
    try:
        container_builder_file = [
            file for file in swift_files if "ContainerBuilder.swift" in file
        ][0]
    except IndexError:
        print("ContainerBuilder.swift file not found.")
    print("ContainerBuilder.swift file found.")
    print("Adding calls to mock implementaion registrations...")
    with open(container_builder_file, "r") as file:
        content = file.read()
        registration_rows = (
            "// MARK: - DO NOT EDIT THIS PART WHILE IN DEBUG MODE ↓\n        "
            + "\n        ".join(registrations)
            + "\n        // MARK: - DO NOT EDIT THIS PART WHILE IN DEBUG MODE ↑"
        )
        repository_registration = re.findall(
            r"static func registerRepository[\s\S]*?\n    \}", content
        )[0]
        repository_registration_processed = repository_registration.replace(
            "return container", registration_rows + "\n        return container"
        )

    if registration_rows not in content:
        with open(container_builder_file, "w") as file:
            file.write(
                content.replace(
                    repository_registration, repository_registration_processed
                )
            )

        print("Calls to mock implementaion registrations added.")
