from typing import Set

JOIN_TYPES: Set[str] = {
    "inner",
    "cross",
    "left_semi",
    "left_anti",
    "left_outer",
    "right_outer",
    "full_outer",
}

AGGREGATION_FUNCTIONS: Set[str] = {
    "count",
    "mean",
    "avg",
    "min",
    "max",
    "sum",
    "first",
    "first_value",
    "last",
    "last_value",
}

WINDOW_FUNCTIONS: Set[str] = AGGREGATION_FUNCTIONS.union(
    {
        "rank",
        "dense_rank",
        "percentile_rank",
        "percent_rank",
        "row_number",
        "lag",
        "lead",
    }
)
