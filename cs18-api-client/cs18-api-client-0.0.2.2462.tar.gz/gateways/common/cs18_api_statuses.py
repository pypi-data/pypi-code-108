"""
Container for Status classes used in cs18-api-client.
"""


class AppInstanceDeploymentStatus:
    PENDING = "Pending"
    DEPLOYING = "Deploying"
    CONFIGURING = "Configuring"
    DONE = "Done"
    ERROR = "Error"
    ABORTED = "Aborted"


class AppDeploymentStatus:
    PENDING = "Pending"
    DEPLOYING = "Deploying"
    DONE = "Done"
    ERROR = "Error"
    ABORTED = "Aborted"


class ServiceStatus:
    PENDING = "Pending"
    SETUP = "Setup"
    DONE = "Done"
    SETUP_FAILED = "SetupFailed"
    ABORTED = "Aborted"
    TERMINATING = "Terminating"
    TERMINATE_FAILED = "TerminateFailed"
    TERMINATED = "Terminated"
    VALIDATION_FAILED = "ValidationFailed"


class TfStageStatus:
    PENDING = "Pending"
    EXECUTING = "Executing"
    DONE = "Done"
    ERROR = "Error"
    SKIPPED = "Skipped"


class SandboxDeploymentStatus:
    WAITING = "Waiting"
    INITIATING = "Initiating"
    DEPLOYING = "Deploying"
    DONE = "Done"
    ERROR = "LaunchFailed"
    ENDING = "EndingSandbox"
    ENDING_FAILED = "EndingFailed"
    ABORTED = "ManuallyAborted"


class SandboxStatus:
    LAUNCHING = "Launching"
    ACTIVE = "Active"
    ACTIVE_WITH_ERROR = "ActiveWithError"
    ENDING = "Ending"
    ENDING_FAILED = "EndingFailed"
    ENDED = "Ended"
    ENDED_WITH_ERROR = "EndedWithError"
    NOT_FOUND = "NotFound"


class LogOutputTypes:
    INITIALIZATION = "initialization"
    HEALTHCHECK = "healthcheck"
    EVENTS = "events"
    ALL = [INITIALIZATION, HEALTHCHECK, EVENTS]


class Achievements:
    cloud_account_added = "cloud_account_added"
    first_blueprint_published = "first_blueprint_published"
    first_sandbox_launched = "first_sandbox_launched"
    first_automation_sandbox = "first_automation_sandbox"


class ProductionUpdateStatus:
    NONE = "None"
    DEPLOYING_GREEN = "DeployingGreen"
    REMOVING_GREEN = "RemovingGreen"
    EXPOSING_GREEN = 'ExposingGreen'
    TRANSITIONING_TO_GREEN = "TransitioningToGreen"
    CLEANING_UP = "CleaningUp"


class ProductionUpdateStrategy:
    BLUE_GREEN = "full environment blue/green"


class UserInviteReasons:
    ADMIN_JOIN_ACCOUNT = "AdminJoinAccount"
    TEAM_MEMBER_JOIN_SPACE = "TeamMemberJoinSpace"
    ADMIN_AUTHENTICATE_CLOUD_ACCOUNT = "AdminAuthenticateCloudAccount"


class DebuggingServiceStatus:
    ON = 'on'
    OFF = 'off'
    TURNING_ON = 'turning_on'
    TURNING_OFF = 'turning_off'
    DISABLED = 'disabled'
    NOT_READY = 'not_ready'


class DefaultComputeServices:
    AWS_EC2 = "aws/EC2"
    AZURE_VM = "azure/AZURE_VM"

    @staticmethod
    def is_default_compute_service(compute_service: str) -> bool:
        return compute_service.lower() in [DefaultComputeServices.AWS_EC2.lower(),
                                           DefaultComputeServices.AZURE_VM.lower()]


class CustomTagScopes:
    ACCOUNT_TAG_SCOPE = 'account'
    SPACE_TAG_SCOPE = 'space'
    BLUEPRINT_TAG_SCOPE = 'blueprint'
    RUNTIME_TAG_SCOPE = 'runtime'
