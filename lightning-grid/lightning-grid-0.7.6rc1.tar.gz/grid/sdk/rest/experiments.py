from grid.openapi import V1DeleteExperimentResponse
from grid.openapi.models import (Externalv1Experiment, Body7, V1ExperimentState)

from grid.sdk.rest import GridRestClient
from grid.sdk.rest.exceptions import throw_with_message


@throw_with_message
def get_experiment_from_id(client: GridRestClient, cluster_id: str, experiment_id: str) -> Externalv1Experiment:
    return client.experiment_service_get_experiment(cluster_id=cluster_id, id=experiment_id)


@throw_with_message
def get_experiment_by_name(client: GridRestClient, cluster_id: str, experiment_name: str) -> Externalv1Experiment:
    exps = client.experiment_service_list_experiments(cluster_id=cluster_id, names=[experiment_name])
    if len(exps.experiments) == 0:
        raise KeyError(f"experiment with name {experiment_name} not found")
    elif len(exps.experiments) > 1:
        raise ValueError(f"multiple experiments found with the name {experiment_name}. please report error.")
    return exps.experiments[0]


@throw_with_message
def update_experiment(
    client: GridRestClient, cluster_id: str, experiment_id: str, desired_state: V1ExperimentState
) -> Externalv1Experiment:
    exp = get_experiment_from_id(client=client, cluster_id=cluster_id, experiment_id=experiment_id)
    spec = exp.spec
    spec.desired_state = desired_state
    update_exp_body = Body7(name=exp.name, spec=spec)
    return client.experiment_service_update_experiment(
        spec_cluster_id=cluster_id, id=experiment_id, body=update_exp_body
    )


@throw_with_message
def delete_experiment(client: GridRestClient, cluster_id: str, experiment_id: str) -> V1DeleteExperimentResponse:
    return client.experiment_service_delete_experiment(cluster_id=cluster_id, id=experiment_id)
