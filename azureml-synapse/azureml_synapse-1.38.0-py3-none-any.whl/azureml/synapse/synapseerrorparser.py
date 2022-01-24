# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Synapse Error Parser module."""


from .synapseerrordetails import SynapseErrorDetails


class SynapseErrorParser:
    """Synapse Error Parser module."""
    error_details = {
        "LIBRARY_MANAGEMENT_FAILED": SynapseErrorDetails("SYNAPSE_LIVY_LIBRARY_MANAGEMENT_FAILED",
                                                         "Library management failed: The session could not be"
                                                         " created as there was a problem installing the session"
                                                         " specific libraries. Check or remove the provided"
                                                         " environment configuration and try again.",
                                                         101),
        "UNABLE_TO_REGISTER_JOB_WITH_TOKEN_PROVIDER": SynapseErrorDetails("SYNAPSE_UNABLE_TO_REGISTER_JOB_TOKEN"
                                                                          "_PROVIDER",
                                                                          "There is transient issue in Synapse LSR "
                                                                          "service. Please have a retry later.",
                                                                          100),
        "does not have the required Synapse RBAC "
        "permission to perform this action": SynapseErrorDetails("SYNAPSE_POOL_PERMISSION",
                                                                 "Please assign Spark Admin role to current user."
                                                                 " Follow document: "
                                                                 "https://docs.microsoft.com/en-us/azure/synapse-"
                                                                 "analytics/security/how-to-manage-synapse-rbac-role"
                                                                 "-assignments",
                                                                 110),
        "ClientIpAddressNotAuthorized": SynapseErrorDetails("CLIENT_IP_ADDRESS_NOT_AUTHORIZED",
                                                            "Please check firewall setting in synapse workspace."
                                                            " Allow your IP to access the workspace and retry."
                                                            " Follow document: https://docs.microsoft.com/en-us/azure/"
                                                            "synapse-analytics/security/synapse-workspace-ip-firewall",
                                                            105)

        # TODO: Enable this PR after synapse team supports throwing error if session level package is not enabled
        # "Session level package is mot enabled": SynapseErrorDetails("SESSION_LEVEL_PACKAGE_NOT_ENABLED",
        #                                                             "Session level package is not enabled in Synapse"
        #                                                             " pool. Please enable the package and retry.",
        #                                                             99)
    }

    @staticmethod
    def get_error_details(error_message_string: str):
        """get Synapse Error details."""
        if error_message_string is None:
            return None

        matching_error = SynapseErrorDetails()
        for error_type in SynapseErrorParser.error_details:
            matching_error = SynapseErrorParser._find_higher_priority_error(matching_error,
                                                                            error_type, error_message_string)
        return matching_error

    @staticmethod
    def _find_higher_priority_error(matching_error: SynapseErrorDetails, error_type: str, error_message_string: str):
        """find Synapse Error with higher priority.
            :param matching_error: Value in error_details_dictionary
            :param error_type: the key in error_details dictionary
            :params error_message_string: exception response string
        """
        if matching_error.error_priority < SynapseErrorParser.error_details[error_type].error_priority:
            if error_type in error_message_string:
                return SynapseErrorParser.error_details[error_type]
        return matching_error
