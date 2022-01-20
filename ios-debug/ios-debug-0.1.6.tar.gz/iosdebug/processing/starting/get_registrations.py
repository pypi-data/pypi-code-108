def get_registrations(repository_protocols):
    registrations = []
    cases = ["Mocked1", "Mocked2", "Mocked3"]
    for protocol in repository_protocols:
        registrations.append(
            "registerMock<PROTOCOL>(to: container)".replace("<PROTOCOL>", protocol)
        )
    return registrations
