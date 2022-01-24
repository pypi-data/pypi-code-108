# Copyright 2019 StreamSets Inc.

"""Common exceptions."""


class InternalServerError(Exception):
    """Internal server error."""
    def __init__(self, response):
        self.status_code = response.status_code
        self.response = response.json()
        self.text = self.response['RemoteException']['localizedMessage']

        # Propagate message from the REST interface as message of the exception
        super().__init__(self.text)


class ActivationError(Exception):
    """Activation error."""
    def __init__(self, reason=None):
        self.reason = reason

    def __str__(self):
        return ('Failed to activate Python SDK '
                'for StreamSets ({}).'.format('reason: {}'.format(self.reason)
                                              if self.reason
                                              else 'no reason provided'))


class BadRequestError(Exception):
    """Bad request error (HTTP 400)."""
    def __init__(self, response):
        super().__init__(response.text)


class ValidationError(Exception):
    """Validation issues."""
    def __init__(self, issues):
        self.issues = issues


class JobInactiveError(Exception):
    """Job status changed into INACTIVE_ERROR."""
    def __init__(self, message):
        self.message = message


class JobRunnerError(Exception):
    """JobRunner errors."""
    def __init__(self, code, message):
        super().__init__('{}: {}'.format(code, message))
        self.code = code
        self.message = message


class DeploymentInactiveError(Exception):
    """Deployment status changed into INACTIVE_ERROR."""
    def __init__(self, message):
        self.message = message


class UnsupportedMethodError(Exception):
    """An unsupported method was called."""
    def __init__(self, message):
        self.message = message


class TopologyIssuesError(Exception):
    """Topology has some issues."""
    def __init__(self, issues):
        self.message = issues


class InvalidCredentialsError(Exception):
    """Invalid credentials error."""
    def __init__(self, message):
        self.message = message


class ConnectionError(Exception):
    """Connection Catalog errors."""
    def __init__(self, code, message):
        super().__init__('{}: {}'.format(code, message))
        self.message = message
        self.code = code
