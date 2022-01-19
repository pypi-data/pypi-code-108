"""This module contains constants."""
# Default Myst Platform API configuration
# Note that these can be overridden by setting `myst_v1alpha1.api_host` and `myst_v1alpha1.api_version`.
DEFAULT_API_HOST = "https://api.myst.ai"
DEFAULT_API_VERSION = "v1alpha1"

USER_AGENT_PREFORMAT = "Myst/{api_version} PythonBindings/{package_version}"

# Environment variables
MYST_APPLICATION_CREDENTIALS_ENVIRONMENT_VARIABLE = "MYST_APPLICATION_CREDENTIALS"

# Default user credentials cache directory and file names
MYST_CACHE_DIRNAME = "myst"
MYST_USER_CREDENTIALS_FILENAME = "myst_user_credentials.json"
