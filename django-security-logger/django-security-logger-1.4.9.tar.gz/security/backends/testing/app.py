from security.backends.app import SecurityBackend


class SecurityTestingBackend(SecurityBackend):

    name = 'security.backends.testing'
    label = 'security_backends_testing'
    backend_name = 'testing'
    reader = 'security.backends.testing.reader.TestingBackendReader'
