# COMMON
CLI_UNEXPECTED_ERROR = "Unexpected error while executing command. details: {0}"

# LOGIN
LOGIN_PROMPT_DOMAIN = "Please enter your cnvrg domain"
LOGIN_PROMPT_EMAIL = "Please enter your email"
LOGIN_PROMPT_PASSWORD = "Please enter your password"
LOGIN_HELP_AUTH_TOKEN = "Use authentication token instead of password"
LOGIN_PROMPT_AUTH_TOKEN = "Please enter your authentication token"
LOGIN_ORGANIZATION_HELP = "Organization to log in to"
LOGIN_ALREADY_LOGGED_IN = "Seems you\'re already logged in"
LOGIN_SUCCESS = "Successfully logged in as {0}"
LOGIN_INVALID_CREDENTIALS = "Invalid credentials"

# LOGOUT
LOGOUT_SUCCESS = "Logged out successfully"
LOGOUT_CONFIG_MISSING = "Cannot logout. Config file is missing. Try logging in first"


# DATA OWNER
DATA_UPLOAD_SUCCESS = "Successfully uploaded updated files"
DATA_DOWNLOAD_SUCCESS = "Successfully downloaded updated files"
DATA_COMMIT_MESSAGE = "Commit message"
DATA_UPLOAD_HELP_GIT_DIFF = "From the list of files, upload those who returned from git diff command."


# DATASET
DATASET_PROMPT_CLONE = "Please enter dataset name to clone"
DATASET_HELP_CLONE = "Name of the dataset to clone"
DATASET_HELP_CLONE_OVERRIDE = "Whether or not re-clone in case the dataset already cloned"
DATASET_CLONE_SKIP = "Dataset {0} is already cloned, therefore skip clone." \
                     " If you want to override, run again using -o flag."
DATASET_PROMPT_NAME = "Please enter dataset name"
DATASET_HELP_NAME = "Name of the dataset"
DATASET_CLONE_SUCCESS = "Successfully cloned dataset: {0}"
DATASET_PUT_PROMPT_FILES = "Please enter a comma separated list of file paths to upload. use . " \
                           "to upload the whole directory"
DATASET_PUT_HELP_FILES = "A comma separated list of file paths to upload. use . " \
                           "to upload the whole directory"
DATASET_REMOVE_PROMPT_FILES = "Please enter a comma separated list of file paths to remove. Wildcards allowed"
DATASET_REMOVE_HELP_FILES = "A comma separated list of file paths to remove. use Wildcards allowed"
DATASET_REMOVE_SUCCESS = "Files removed successfully"

# PROJECT
PROJECT_PROMPT_CLONE = "Please enter project name to clone"
PROJECT_HELP_CLONE = "Name of the project to clone"
PROJECT_HELP_CLONE_OVERRIDE = "Whether or not re-clone in case the project already cloned"
PROJECT_CLONE_SKIP = "Project {0} is already cloned, therefore skip clone." \
                     " If you want to override, run again using -o flag."
PROJECT_CLONE_SUCCESS = "Successfully cloned project: {0}"
PROJECT_UPLOAD_SUCCESS = "Successfully uploaded updated files"
PROJECT_DOWNLOAD_SUCCESS = "Successfully downloaded updated files"
PROJECT_LINK_PROMPT_NAME = "Please enter a name for the new project"
PROJECT_LINK_HELP_NAME = "Name for the new project"
PROJECT_LINK_GIT_PROMPT_NAME = "Please enter the name of the git project"
PROJECT_LINK_GIT_HELP_NAME = "Name of the git project"
PROJECT_LINK_SUCCESS = "Finished linking project {0} successfully."
PROJECT_CREATE_NEW = "Creating new project {0}"
PROJECT_CONFIGURING_FOLDER = "Configuring project folder"
PROJECT_UPLOAD = "Uploading project files"
PROJECT_PROMPT_CREATE = "Please enter project name to create"
PROJECT_HELP_CREATE = "Name for the new project"
PROJECT_CREATE_FOLDER_NOT_EMPTY = "Warning! You're about to associate a non empty folder with the new project." \
                                  "\r\nContinue?"
PROJECT_CREATING_PROJECT = "Creating new project {0}"
PROJECT_CREATE_SUCCESS = "Successfully created project {0}"
PROJECT_DOWNLOAD_HELP_COMMIT = "Sha1 of the commit to download"


# EXPERIMENT
EXPERIMENT_PROMPT_TITLE = "Please enter a title for the experiment"
EXPERIMENT_HELP_TITLE = "Name of the experiment"
EXPERIMENT_HELP_TEMPLATES = "Comma separated list of template names"
EXPERIMENT_HELP_LOCAL = "Boolean. Run the experiment locally"
EXPERIMENT_PROMPT_COMMAND = "Please enter a command to run as experiment"
EXPERIMENT_HELP_COMMAND = "The command to run"
EXPERIMENT_HELP_DATASETS = "list of comma separated datasets names to use in the experiment"
EXPERIMENT_HELP_VOLUME = "A volume name to attach to this experiment"
EXPERIMENT_HELP_SYNC_BEFORE = "Boolean. Sync environment before running the experiment"
EXPERIMENT_HELP_SYNC_AFTER = "Boolean. sync environment after the experiment finished"
EXPERIMENT_HELP_IMAGE = "Image name and tag to create experiment with. format - image_name:tag"
EXPERIMENT_HELP_GIT_BRANCH = "The branch to pull files from for the experiment, in case project is git project"
EXPERIMENT_HELP_GIT_COMMIT = "The commit to pull files from for the experiment, in case project is git project"
EXPERIMENT_CREATE_SUCCESS = "Experiment {0} created successfully. \r\nExperiment is available at: {1}"

# LOGS
LOG_START_COMMAND = "Starting command {0}. Options: {1}"
LOG_CLONING_PROJECT = "Cloning project: {0}"
LOG_CLONING_DATASET = "Cloning dataset: {0}"

# SSH
SSH_HELP_PORT = "Port to bind on host"
SSH_HELP_USERNAME = "Username to login in container, default will be image default user"
SSH_HELP_PASSWORD = "Password for login"
SSH_HELP_KUBECTL = "Full path to kubeconfig file, otherwise default will be used"
SSH_STARTING_SESSION = "Starting a new ssh session"
SSH_WAITING_FOR_READY = "Waiting for ssh session to be ready..."
SSH_READY = "\r\nSsh session is ready to receive connections.\r\n" \
            "\r\nIn order to connect to your job, define your ssh connection with the following params:\r\n"\
            "host: 127.0.0.1\r\n"\
            "port: {0}\r\n"\
            "username: {1}\r\n"\
            "password: {2}"

# CONFIG
CONFIG_HELP_CHECK_CERTIFICATE = "{0} ssl validation on https requests"
CONFIG_UPDATE_SUCCESS = "Config updated successfully"
CONFIG_HELP_ORGANIZTION = "Name of organization to switch to"
CONFIG_NO_ARGS_LOG = "No arguments sent. Showing help message instead"
