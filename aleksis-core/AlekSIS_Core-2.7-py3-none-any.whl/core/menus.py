from django.conf import settings
from django.utils.translation import gettext_lazy as _

from .util.core_helpers import unread_notifications_badge

MENUS = {
    "NAV_MENU_CORE": [
        {
            "name": _("Login"),
            "url": settings.LOGIN_URL,
            "icon": "lock_open",
            "validators": ["menu_generator.validators.is_anonymous"],
        },
        {
            "name": _("Sign up"),
            "url": "account_signup",
            "icon": "how_to_reg",
            "validators": [
                "menu_generator.validators.is_anonymous",
                ("aleksis.core.util.predicates.permission_validator", "core.can_register"),
            ],
        },
        {
            "name": _("Accept invitation"),
            "url": "enter_invitation_code",
            "icon": "vpn_key",
            "validators": [
                "menu_generator.validators.is_anonymous",
                ("aleksis.core.util.predicates.permission_validator", "core.invite_enabled"),
            ],
        },
        {
            "name": _("Dashboard"),
            "url": "index",
            "icon": "home",
            "validators": [
                ("aleksis.core.util.predicates.permission_validator", "core.view_dashboard_rule")
            ],
        },
        {
            "name": _("Notifications"),
            "url": "notifications",
            "icon": "notifications",
            "badge": unread_notifications_badge,
            "validators": [
                (
                    "aleksis.core.util.predicates.permission_validator",
                    "core.view_notifications",
                ),
            ],
        },
        {
            "name": _("Account"),
            "url": "#",
            "icon": "person",
            "root": True,
            "validators": ["menu_generator.validators.is_authenticated"],
            "submenu": [
                {
                    "name": _("Stop impersonation"),
                    "url": "impersonate-stop",
                    "icon": "stop",
                    "validators": [
                        "menu_generator.validators.is_authenticated",
                        "aleksis.core.util.core_helpers.is_impersonate",
                    ],
                },
                {
                    "name": _("Logout"),
                    "url": "logout",
                    "icon": "exit_to_app",
                    "validators": ["menu_generator.validators.is_authenticated"],
                },
                {
                    "name": _("2FA"),
                    "url": "two_factor:profile",
                    "icon": "phonelink_lock",
                    "validators": [
                        "menu_generator.validators.is_authenticated",
                    ],
                },
                {
                    "name": _("Change password"),
                    "url": "account_change_password",
                    "icon": "lock",
                    "validators": [
                        "menu_generator.validators.is_authenticated",
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "core.can_change_password",
                        ),
                    ],
                },
                {
                    "name": _("Me"),
                    "url": "person",
                    "icon": "insert_emoticon",
                    "validators": [
                        "menu_generator.validators.is_authenticated",
                        "aleksis.core.util.core_helpers.has_person",
                    ],
                },
                {
                    "name": _("Preferences"),
                    "url": "preferences_person",
                    "icon": "settings",
                    "validators": [
                        "menu_generator.validators.is_authenticated",
                        "aleksis.core.util.core_helpers.has_person",
                    ],
                },
                {
                    "name": _("Third-party accounts"),
                    "url": "socialaccount_connections",
                    "icon": "public",
                    "validators": [
                        "menu_generator.validators.is_authenticated",
                        "aleksis.core.util.core_helpers.has_person",
                    ],
                },
                {
                    "name": _("Authorized applications"),
                    "url": "oauth2_provider:authorized-token-list",
                    "icon": "touch_app",
                    "validators": [
                        "menu_generator.validators.is_authenticated",
                        "aleksis.core.util.core_helpers.has_person",
                    ],
                },
            ],
        },
        {
            "name": _("Admin"),
            "url": "#",
            "icon": "security",
            "validators": [
                ("aleksis.core.util.predicates.permission_validator", "core.view_admin_menu"),
            ],
            "submenu": [
                {
                    "name": _("Announcements"),
                    "url": "announcements",
                    "icon": "announcement",
                    "validators": [
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "core.view_announcements_rule",
                        ),
                    ],
                },
                {
                    "name": _("School terms"),
                    "url": "school_terms",
                    "icon": "date_range",
                    "validators": [
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "core.view_schoolterm_rule",
                        ),
                    ],
                },
                {
                    "name": _("Dashboard widgets"),
                    "url": "dashboard_widgets",
                    "icon": "dashboard",
                    "validators": [
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "core.view_dashboardwidget_rule",
                        ),
                    ],
                },
                {
                    "name": _("Data management"),
                    "url": "data_management",
                    "icon": "view_list",
                    "validators": [
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "core.manage_data_rule",
                        ),
                    ],
                },
                {
                    "name": _("System status"),
                    "url": "system_status",
                    "icon": "power_settings_new",
                    "validators": [
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "core.view_system_status_rule",
                        ),
                    ],
                },
                {
                    "name": _("Configuration"),
                    "url": "preferences_site",
                    "icon": "settings",
                    "validators": [
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "core.change_site_preferences_rule",
                        ),
                    ],
                },
                {
                    "name": _("Data checks"),
                    "url": "check_data",
                    "icon": "done_all",
                    "validators": ["menu_generator.validators.is_superuser"],
                },
                {
                    "name": _("Manage permissions"),
                    "url": "manage_user_global_permissions",
                    "icon": "shield",
                    "validators": [
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "core.manage_permissions",
                        ),
                    ],
                },
                {
                    "name": _("Backend Admin"),
                    "url": "admin:index",
                    "icon": "settings",
                    "validators": [
                        "menu_generator.validators.is_superuser",
                    ],
                },
                {
                    "name": _("OAuth2 Applications"),
                    "url": "oauth2_applications",
                    "icon": "touch_app",
                    "validators": [
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "core.list_oauth_applications_rule",
                        ),
                    ],
                },
            ],
        },
        {
            "name": _("People"),
            "url": "#",
            "icon": "people",
            "root": True,
            "validators": [
                ("aleksis.core.util.predicates.permission_validator", "core.view_people_menu_rule")
            ],
            "submenu": [
                {
                    "name": _("Persons"),
                    "url": "persons",
                    "icon": "person",
                    "validators": [
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "core.view_persons_rule",
                        )
                    ],
                },
                {
                    "name": _("Groups"),
                    "url": "groups",
                    "icon": "group",
                    "validators": [
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "core.view_groups_rule",
                        )
                    ],
                },
                {
                    "name": _("Group types"),
                    "url": "group_types",
                    "icon": "category",
                    "validators": [
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "core.view_grouptypes_rule",
                        )
                    ],
                },
                {
                    "name": _("Groups and child groups"),
                    "url": "groups_child_groups",
                    "icon": "group_add",
                    "validators": [
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "core.assign_child_groups_to_groups_rule",
                        )
                    ],
                },
                {
                    "name": _("Additional fields"),
                    "url": "additional_fields",
                    "icon": "style",
                    "validators": [
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "core.view_additionalfields_rule",
                        )
                    ],
                },
                {
                    "name": _("Invite person"),
                    "url": "invite_person",
                    "icon": "card_giftcard",
                    "validators": [
                        "menu_generator.validators.is_authenticated",
                        ("aleksis.core.util.predicates.permission_validator", "core.can_invite"),
                    ],
                },
            ],
        },
    ],
    "DATA_MANAGEMENT_MENU": [
        {
            "name": _("Assign child groups to groups"),
            "url": "groups_child_groups",
            "validators": [
                (
                    "aleksis.core.util.predicates.permission_validator",
                    "core.assign_child_groups_to_groups_rule",
                )
            ],
        },
    ],
}
