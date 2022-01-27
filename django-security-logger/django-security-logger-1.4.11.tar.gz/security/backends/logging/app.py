from security.backends.app import SecurityBackend


class SecurityLoggingBackend(SecurityBackend):

    name = 'security.backends.logging'
    label = 'security_backends_logging'
    backend_name = 'logging'
    writer = 'security.backends.logging.writer.LoggingBackendWriter'
