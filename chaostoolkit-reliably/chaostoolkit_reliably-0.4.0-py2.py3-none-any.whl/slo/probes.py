from typing import Dict, List
from urllib.parse import quote

from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Configuration, Secrets
from logzero import logger

from chaosreliably import get_session
from chaosreliably.types import ObjectiveResult

from .tolerances import all_objective_results_ok

__all__ = ["get_objective_results_by_labels", "slo_is_met"]


def get_objective_results_by_labels(
    labels: Dict[str, str],
    limit: int = 1,
    configuration: Configuration = None,
    secrets: Secrets = None,
) -> List[ObjectiveResult]:
    """
    For a given set of Objective labels, return all of the Ojective Results

    :param labels: Dict[str, str] representing the Objective Labels for the Objective
        to retrieve results for
    :param limit: int representing how many results to retrieve - Default 1
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    :returns: List[ObjectiveResult] representing the Objective Results for the given
        Objective

    """
    encoded_labels = quote(
        ",".join([f"{key}={value}" for key, value in labels.items()])
    )
    with get_session(configuration, secrets) as session:
        url = f"/objectiveresult?objective-match={encoded_labels}"
        resp = session.get(url, params={"limit": limit})
        logger.debug(f"Fetched SLO results from: {resp.url}")
        if resp.status_code != 200:
            raise ActivityFailed(f"Failed to retrieve SLO results: {resp.text}")
        return ObjectiveResult.parse_list(resp.json())


def slo_is_met(
    labels: Dict[str, str],
    limit: int = 1,
    configuration: Configuration = None,
    secrets: Secrets = None,
) -> bool:
    """
    For a given set of Objective labels, return whether the Objective was met

    :param labels: Dict[str, str] representing the Objective Labels for the Objective
        to retrieve results for
    :param limit: int representing how many results to retrieve - Default 1
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    :returns: bool representing whether the SLO was met or not
    """
    results = get_objective_results_by_labels(
        labels=labels, limit=limit, configuration=configuration, secrets=secrets
    )
    return all_objective_results_ok(results)
