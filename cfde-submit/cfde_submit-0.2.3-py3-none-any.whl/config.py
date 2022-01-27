"""
NOTE! This only lists the base config items for the cfde-submit package.

Dynamic configs are remotely fetched from the Production Globus Endpoint,
allowing flows to change independent of client code updates.

LOGGING: To enable extended logging, set the CFDE_SUBMIT_LOGGING env var.
EX: export CFDE_SUBMIT_LOGGING=DEBUG
"""
import os
import globus_automate_client

log_level = os.getenv("CFDE_SUBMIT_LOGGING") or "NOTSET"

CONFIG = {
    # Files with dynamic config information in JSON
    "DYNAMIC_CONFIG_LINKS": {
        "prod": ("https://g-5cf005.aa98d.08cc.data.globus.org/submission_dynamic_config/"
                 "cfde_client_config.json?download=0"),
        "staging": ("https://g-5cf005.aa98d.08cc.data.globus.org/submission_dynamic_config/"
                    "cfde_client_config.json?download=0"),
        "dev": ("https://g-5cf005.aa98d.08cc.data.globus.org/submission_dynamic_config/"
                "cfde_client_config.json?download=0")
    },
    # Translations for Automate states into nicer language
    "STATE_MSGS": {
        "ACTIVE": "is still in progress",
        "INACTIVE": "has stalled, and may need help to resume",
        "SUCCEEDED": "has completed successfully",
        "FAILED": "has failed"
    },
    "LOGGING": {
        "version": 1,
        "formatters": {
            "basic": {"format": "[%(levelname)s] %(name)s::%(funcName)s() %(message)s"}
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "basic",
                "level": "NOTSET"
            }
        },
        "loggers": {
            'cfde_submit': {
                "propagate": False,
                "level": "NOTSET",
                "handlers": ["console"],
            },
        },
    },
    # This scope lists the GCS server for PROD that holds config data. It MAY be different
    # from the server responsible for holding data (for instance --service-instance dev)
    "HTTPS_SCOPE": "https://auth.globus.org/scopes/0e57d793-f1ac-4eeb-a30f-643b082d68ec/https",
    "AUTOMATE_SCOPES": list(globus_automate_client.flows_client.ALL_FLOW_SCOPES),
    "TRANSFER_SCOPE": "urn:globus:auth:scope:transfer.api.globus.org:all",
    # Format for BDBag archives
    "ARCHIVE_FORMAT": "zip"
}
# Add all necessary scopes together for Auth call
CONFIG["ALL_SCOPES"] = CONFIG["AUTOMATE_SCOPES"] + [CONFIG["HTTPS_SCOPE"]]
