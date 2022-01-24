import numpy as np
import pandas as pd
from src.endpoints import X, repayment


def test_mean(json_metadata):
    prob = repayment(pd.read_parquet(X))
    mean_pred = np.mean(prob)

    json_metadata["section"] = "Plausibility"
    json_metadata["pass_message"] = f"Mean prediction is plausible ({mean_pred:.2f})"
    json_metadata["fail_message"] = f"Mean prediction is implausible ({mean_pred:.2f})"

    assert 0.85 < mean_pred < 0.90


def test_spread_10_90(json_metadata):
    prob = repayment(pd.read_parquet(X))
    p10 = np.quantile(prob, q=0.10)
    p90 = np.quantile(prob, q=0.90)
    spread = p90 - p10

    json_metadata["section"] = "Plausibility"
    json_metadata["pass_message"] = f"10%/90% Spread is plausible ({spread:.2f})"
    json_metadata["fail_message"] = f"10%/90% Spread is implausible ({spread:.2f})"

    assert 0.05 < spread < 0.15


def test_spread_25_75(json_metadata):
    prob = repayment(pd.read_parquet(X))
    p25 = np.quantile(prob, q=0.25)
    p75 = np.quantile(prob, q=0.75)
    spread = p75 - p25

    json_metadata["section"] = "Plausibility"
    json_metadata["pass_message"] = f"25%/75% Spread is plausible ({spread:.2f})"
    json_metadata["fail_message"] = f"25%/75% Spread is implausible ({spread:.2f})"

    assert 0.025 < spread < 0.05
