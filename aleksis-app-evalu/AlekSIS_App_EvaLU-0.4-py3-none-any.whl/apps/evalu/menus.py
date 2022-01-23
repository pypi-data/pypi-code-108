from django.utils.translation import ugettext_lazy as _

MENUS = {
    "NAV_MENU_CORE": [
        {
            "name": _("EvaLU"),
            "url": "#",
            "icon": "forum",
            "root": True,
            "validators": [
                (
                    "aleksis.core.util.predicates.permission_validator",
                    "evalu.view_menu_rule",
                ),
            ],
            "submenu": [
                {
                    "name": _("Evaluation Phases"),
                    "url": "evaluation_phases",
                    "icon": "date_range",
                    "validators": [
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "evalu.view_evaluation_phases",
                        ),
                    ],
                },
                {
                    "name": _("Evaluation parts"),
                    "url": "evaluation_parts",
                    "icon": "live_help",
                    "validators": [
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "evalu.view_evaluation_parts",
                        ),
                    ],
                },
                {
                    "name": _("All Evaluations"),
                    "url": "evaluation_phases_overview",
                    "icon": "live_help",
                    "validators": [
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "evalu.view_evaluationphases_overview_rule",
                        ),
                    ],
                },
                {
                    "name": _("My Evaluations"),
                    "url": "evaluations_as_participant",
                    "icon": "live_help",
                    "validators": [
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "evalu.view_evaluations_as_participant_rule",
                        ),
                    ],
                },
            ],
        }
    ]
}
