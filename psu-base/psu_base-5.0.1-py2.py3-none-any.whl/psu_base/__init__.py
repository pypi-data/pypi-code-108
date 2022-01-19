from django.conf import settings

__version__ = "5.0.1"
name = "psu_base"

default_app_config = "psu_base.apps.PsuTemplateConfig"

# Default settings
_DEFAULTS = {
    "PSU_BASE_VERSION": __version__,
    "FINTI_URL": "https://ws-test.oit.pdx.edu",
    "FINTI_SIMULATE_CALLS": False,  # Simulate Finti calls (i.e. when not on VPN)
    "FINTI_SAVE_RESPONSES": False,  # Save/record actual Finti responses for offline use?
    "AUTHORIZE_GLOBAL": False,  # Allow authorizing for other apps?
    # Admin Menu Items
    "PSU_BASE_ADMIN_LINKS": [
        {"url": "psu:test", "label": "Status Page", "icon": "fa-medkit"},
        {
            "url": "psu:errors",
            "label": "Error Log",
            "icon": "fa-exclamation-triangle",
            "authorities": "~SuperUser",
        },
        {"url": "psu:emails", "label": "Email Log", "icon": "fa-envelope-o"},
        {
            "url": "psu:features",
            "label": "Feature Toggles",
            "icon": "fa-plug",
            "authorities": "~SuperUser+features",
        },
        {
            "url": "psu:audit",
            "label": "Audit Events",
            "icon": "fa-id-card-o",
            "authorities": "~SecurityOfficer",
        },
        {
            "url": "psu:audit_xss",
            "label": "XSS Attempts",
            "icon": "fa-user-secret",
            "authorities": "~SecurityOfficer",
        },
        {
            "url": "psu:finti",
            "label": "Finti Interface",
            "icon": "fa-laptop",
            "authorities": "developer",
            "feature": "finti_console",
            "nonprod_only": True,
        },
        {
            "url": "psu:session",
            "label": "Session Contents",
            "icon": "fa-microchip",
            "authorities": "developer",
        },
        {
            "url": "psu:email",
            "label": "Send Test Email",
            "icon": "fa-paper-plane-o",
            "authorities": "developer",
        },
        {
            "url": "psu:scripts",
            "label": "Admin Script",
            "icon": "fa-code",
            "authorities": "~SuperUser+scriptor",
            "feature": "admin_script",
        },
        {
            "url": "psu:export",
            "label": "Database Export",
            "icon": "fa-database",
            "authorities": "developer",
            "feature": "database_export",
        },
        {
            "url": "psu:downtimes",
            "label": "Downtimes",
            "icon": "fa-bed",
            "authorities": "developer",
        },
    ],
}

# Assign default setting values
for key, value in _DEFAULTS.items():
    try:
        getattr(settings, key)
    except AttributeError:
        setattr(settings, key, value)
    # Suppress errors from DJANGO_SETTINGS_MODULE not being set
    except:
        pass
