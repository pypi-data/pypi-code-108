import sys
from typing import List
from typing import Optional

from colorama import Style

from tecton.cli import printer


def human_fco_type(fco_type: str, plural=False) -> str:
    name_map = {
        "virtual_data_source": ("VirtualDataSource", "VirtualDataSources"),
        "batch_data_source": ("BatchDataSource", "BatchDataSources"),
        "stream_data_source": ("StreamDataSource", "StreamDataSources"),
        "entity": ("Entity", "Entities"),
        "transformation": ("Transformation", "Transformations"),
        "new_transformation": ("Transformation", "Transformations"),
        "feature_table": ("FeatureTable", "FeatureTables"),
        "feature_view": ("FeatureView", "FeatureViews"),
        "batch_feature_view": ("BatchFeatureView", "BatchFeatureViews"),
        "on_demand_feature_view": ("OnDemandFeatureView", "OnDemandFeatureViews"),
        "stream_feature_view": ("StreamFeatureView", "StreamFeatureViews"),
        "batch_window_aggregate_feature_view": ("BatchWindowAggregateFeatureView", "BatchWindowAggregateFeatureViews"),
        "stream_window_aggregate_feature_view": (
            "StreamWindowAggregateFeatureView",
            "StreamWindowAggregateFeatureViews",
        ),
        "feature_service": ("FeatureService", "FeatureServices"),
    }
    if plural:
        return name_map[fco_type][1]
    else:
        return name_map[fco_type][0]


def ask_user(message: str, options: List[str], default=None, let_fail=False) -> Optional[str]:
    options_idx = {o.lower(): i for i, o in enumerate(options)}

    while True:
        if len(options) > 1:
            printer.safe_print(message, "[" + "/".join(options) + "]", end="> ")
        else:
            printer.safe_print(message, end="> ")

        try:
            user_input = input().strip().lower()
        except EOFError:
            return None

        if user_input == "" and default:
            return default

        if user_input in options_idx:
            return options[options_idx[user_input]]
        else:
            # If there is only one input option, typing "!" will select it.
            if user_input == "!" and len(options) == 1:
                return options[0]
            elif let_fail:
                return None


def confirm_or_exit(message, expect=None):
    try:
        if expect:
            if ask_user(message, options=[expect], let_fail=True) is not None:
                return
            else:
                printer.safe_print("Aborting")
                sys.exit(1)
        else:
            if ask_user(message, options=["y", "N"], default="N") == "y":
                return
            else:
                printer.safe_print("Aborting")
                sys.exit(1)
    except KeyboardInterrupt:
        printer.safe_print("Aborting")
        sys.exit(1)


def bold(x):
    return Style.BRIGHT + x + Style.NORMAL
