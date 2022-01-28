from typing import Any, Dict, List, cast

from chaoslib.types import (
    Activity,
    Configuration,
    Experiment,
    Hypothesis,
    Journal,
    Run,
    Secrets,
)
from logzero import logger

from chaosreliably import get_session
from chaosreliably.types import (
    EntityContext,
    EntityContextExperimentEventLabels,
    EntityContextExperimentLabels,
    EntityContextExperimentRunLabels,
    EntityContextExperimentVersionLabels,
    EntityContextMetadata,
    EventType,
)

__all__ = [
    "after_activity_control",
    "after_experiment_control",
    "after_hypothesis_control",
    "after_method_control",
    "after_rollback_control",
    "before_activity_control",
    "before_experiment_control",
    "before_hypothesis_control",
    "before_method_control",
    "before_rollback_control",
]


def before_experiment_control(
    context: Experiment,
    configuration: Configuration = None,
    secrets: Secrets = None,
    **kwargs: Any,
) -> None:
    """
    Control run *before* the execution of an Experiment.

    For a given Experiment, the control creates (if not already created) an Experiment
    Entity Context and an Experiment Version Entity Context in the Reliably service.

    A unique Experiment Run Entity Context is also created, with an Experiment Event
    Entity Context of type `EXPERIMENT_START` created, relating to the run.

    The control requires the `arguments` of `commit_hash`, `source`, and `user` to be
    provided to the control definition. If not provided, the control will simply not
    create any Entity Contexts.

    Once the Entity Contexts have been created, an entry into the configuration is made
    under configuration["chaosreliably"]["experiment_run_labels"] to allow for
    other controls to create events relating to the Experiment Run.

    :param context: Experiment object representing the Experiment that will be executed
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    :param **kwargs: Expected required `kwargs` are 'commit_hash' (str), `source` (str),
        and `user` (str), optional is `experiment_related_to_labels`
        (List[Dict[str, str]]) representing labels of entities the Experiment relates to

    Examples
    --------
    # Experiment has no relation to any Reliably entity
    "controls": [
        {
            "name": "chaosreliably",
            "provider": {
                "type": "python",
                "module": "chaosreliably.controls.experiment",
                "arguments": {
                    "commit_hash": "59f9f577e2d90719098f4d23d26329ce41f2d0bd",
                    "source": "https://github.com/chaostoolkit-incubator/chaostoolkit-reliably/exp.json",  # Noqa
                    "user": "A users name"
                }
            }
        }
    ]

    # Experiment relates to a Reliably Entity
    "controls": [
        {
            "name": "chaosreliably",
            "provider": {
                "type": "python",
                "module": "chaosreliably.controls.experiment",
                "arguments": {
                    "commit_hash": "59f9f577e2d90719098f4d23d26329ce41f2d0bd",
                    "source": "https://github.com/chaostoolkit-incubator/chaostoolkit-reliably/exp.json",  # Noqa
                    "user": "A users name",
                    "experiment_related_to_labels": [
                        {
                            "name": "must-be-good-slo",
                            "service": "must-be-good-service"
                        }
                    ]
                }
            }
        }
    ]
    """
    try:
        reliably_secrets = secrets.get("reliably", None) if secrets else None
        commit_hash = kwargs.get("commit_hash")
        source = kwargs.get("source")
        user = kwargs.get("user")
        if not commit_hash or not source or not user:
            logger.debug(
                "The parameters: `commit_hash`, `source`, and `user` are required for "
                "the chaosreliably controls, please provide them. This Experiment Run"
                " will not be tracked with Reliably."
            )
            return

        experiment_related_to_labels = kwargs.get("experiment_related_to_labels") or []

        experiment_run_labels = (
            _create_experiment_entities_for_before_experiment_control(
                experiment_title=context["title"],
                commit_hash=commit_hash,
                source=source,
                user=user,
                configuration=configuration,
                secrets=reliably_secrets,
                experiment_related_to_labels=experiment_related_to_labels,
            )
        )

        configuration.update(
            {"chaosreliably": {"experiment_run_labels": experiment_run_labels}}
        )
    except Exception as ex:
        logger.debug(
            f"An error occurred: {ex}, whilst running the Before Experiment control, "
            "no further entities will be created, the Experiment execution won't be "
            "affected"
        )


def after_experiment_control(
    context: Experiment,
    state: Journal,
    configuration: Configuration = None,
    secrets: Secrets = None,
    **kwargs: Any,
) -> None:
    """
    Control run *after* the execution of an Experiment.

    For a given Experiment and its state in Journal form, the control creates an
    Experiment Event Entity Context in the Reliably service.

    The Event has the `event_type` of `EXPERIMENT_END`

    :param context: Experiment object representing the Experiment that was executed
    :param state: Journal object representing the state of the Experiment after
        execution
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    :param **kwargs: Any additional keyword arguments passed to the control
    """
    try:
        reliably_secrets = secrets.get("reliably", None) if secrets else None
        _create_experiment_event(
            event_type=EventType.EXPERIMENT_END,
            name=f"Experiment: {context['title']} - Ended",
            output=state,
            experiment_run_labels=configuration["chaosreliably"][
                "experiment_run_labels"
            ],
            configuration=configuration,
            secrets=reliably_secrets,
        )
    except Exception as ex:
        logger.debug(
            f"An error occurred: {ex}, while running the After Experiment control, the"
            " Experiment execution won't be affected."
        )


def before_hypothesis_control(
    context: Hypothesis,
    configuration: Configuration = None,
    secrets: Secrets = None,
    **kwargs: Any,
) -> None:
    """
    Control run *before* the execution of an Experiments Steady State Hypothesis.

    For a given Steady State Hypothesis, the control creates an Experiment Event Entity
    Context in the Reliably service.

    The Event has the `event_type` of `HYPOTHESIS_START`.

    :param context: Hypothesis object representing the Steady State Hypothesis that is
        to be executed
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    :param **kwargs: Any additional keyword arguments passed to the control
    """
    try:
        reliably_secrets = secrets.get("reliably", None) if secrets else None
        _create_experiment_event(
            event_type=EventType.HYPOTHESIS_START,
            name=context["title"],
            output=None,
            experiment_run_labels=configuration["chaosreliably"][
                "experiment_run_labels"
            ],
            configuration=configuration,
            secrets=reliably_secrets,
        )
    except Exception as ex:
        logger.debug(
            f"An error occurred: {ex}, while running the Before Hypothesis control, the"
            " Experiment execution won't be affected."
        )


def after_hypothesis_control(
    context: Hypothesis,
    state: Dict[str, Any],
    configuration: Configuration = None,
    secrets: Secrets = None,
    **kwargs: Any,
) -> None:
    """
    Control run *after* the execution of an Experiments Steady State Hypothesis.

    For a given Steady State Hypothesis and its state, post execution, the control
    creates an Experiment Event Entity Context in the Reliably service.

    The Event has the `event_type` of `HYPOTHESIS_END`.

    :param context: Hypothesis object representing the Steady State Hypothesis that has
        been executed
    :param state: Dict[str, Any] representing the output of
        `run_steady_state_hypothesis` in `chaoslib`
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    :param **kwargs: Any additional keyword arguments passed to the control
    """
    try:
        reliably_secrets = secrets.get("reliably", None) if secrets else None
        _create_experiment_event(
            event_type=EventType.HYPOTHESIS_END,
            name=context["title"],
            output=state,
            experiment_run_labels=configuration["chaosreliably"][
                "experiment_run_labels"
            ],
            configuration=configuration,
            secrets=reliably_secrets,
        )
    except Exception as ex:
        logger.debug(
            f"An error occurred: {ex}, while running the After Hypothesis control, the"
            " Experiment execution won't be affected."
        )


def before_method_control(
    context: Experiment,
    configuration: Configuration = None,
    secrets: Secrets = None,
    **kwargs: Any,
) -> None:
    """
    Control run *before* the execution of an Experiments Method.

    For a given Experiment, the control creates an Experiment Event Entity Context in
    the Reliably service.

    The Event has the `event_type` of `METHOD_START`.

    :param context: Experiment object representing the Experiment that will be executed
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    :param **kwargs: Any additional keyword arguments passed to the control
    """
    try:
        reliably_secrets = secrets.get("reliably", None) if secrets else None
        _create_experiment_event(
            event_type=EventType.METHOD_START,
            name=f"{context['title']} - Method Start",
            output=None,
            experiment_run_labels=configuration["chaosreliably"][
                "experiment_run_labels"
            ],
            configuration=configuration,
            secrets=reliably_secrets,
        )
    except Exception as ex:
        logger.debug(
            f"An error occurred: {ex}, while running the Before Method control, the"
            " Experiment execution won't be affected."
        )


def after_method_control(
    context: Experiment,
    state: List[Run],
    configuration: Configuration = None,
    secrets: Secrets = None,
    **kwargs: Any,
) -> None:
    """
    Control run *after* the execution of an Experiments Method.

    For a given Experiment Method and its state, the control creates an Experiment
    Event Entity Context in the Reliably service.

    The Event has the `event_type` of `METHOD_END`.

    :param context: Experiment object representing the Experiment that will be executed
    :param state: List[Run] object presenting the executed Activities within the
        Experiments Method
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    :param **kwargs: Any additional keyword arguments passed to the control
    """
    try:
        reliably_secrets = secrets.get("reliably", None) if secrets else None
        _create_experiment_event(
            event_type=EventType.METHOD_END,
            name=f"{context['title']} - Method End",
            output=state,
            experiment_run_labels=configuration["chaosreliably"][
                "experiment_run_labels"
            ],
            configuration=configuration,
            secrets=reliably_secrets,
        )
    except Exception as ex:
        logger.debug(
            f"An error occurred: {ex}, while running the After Method control, the"
            " Experiment execution won't be affected."
        )


def before_rollback_control(
    context: Experiment,
    configuration: Configuration = None,
    secrets: Secrets = None,
    **kwargs: Any,
) -> None:
    """
    Control run *before* the execution of an Experiments Rollback.

    For a given Experiment, the control creates an Experiment Event Entity Context in
    the Reliably service.

    The Event has the `event_type` of `ROLLBACK_START`.

    :param context: Experiment object representing the Experiment that will be executed
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    :param **kwargs: Any additional keyword arguments passed to the control
    """
    try:
        reliably_secrets = secrets.get("reliably", None) if secrets else None
        _create_experiment_event(
            event_type=EventType.ROLLBACK_START,
            name=f"{context['title']} - Rollback Start",
            output=None,
            experiment_run_labels=configuration["chaosreliably"][
                "experiment_run_labels"
            ],
            configuration=configuration,
            secrets=reliably_secrets,
        )
    except Exception as ex:
        logger.debug(
            f"An error occurred: {ex}, while running the Before Rollback control, the"
            " Experiment execution won't be affected."
        )


def after_rollback_control(
    context: Experiment,
    state: List[Run],
    configuration: Configuration = None,
    secrets: Secrets = None,
    **kwargs: Any,
) -> None:
    """
    Control run *after* the execution of an Experiments Rollback.

    For a given Experiment Rollback and its state, the control creates an Experiment
    Event Entity Context in the Reliably service.

    The Event has the `event_type` of `ROLLBACK_END`.

    :param context: Experiment object representing the Experiment that will be executed
    :param state: List[Run] object presenting the executed Activities within the
        Experiments Rollback
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    :param **kwargs: Any additional keyword arguments passed to the control
    """
    try:
        reliably_secrets = secrets.get("reliably", None) if secrets else None
        _create_experiment_event(
            event_type=EventType.ROLLBACK_END,
            name=f"{context['title']} - Rollback End",
            output=state,
            experiment_run_labels=configuration["chaosreliably"][
                "experiment_run_labels"
            ],
            configuration=configuration,
            secrets=reliably_secrets,
        )
    except Exception as ex:
        logger.debug(
            f"An error occurred: {ex}, while running the After Rollback control, the"
            " Experiment execution won't be affected."
        )


def before_activity_control(
    context: Activity,
    configuration: Configuration = None,
    secrets: Secrets = None,
    **kwargs: Any,
) -> None:
    """
    Control run *before* the execution of an Experiment Activity.

    For a given Experiment Activity, the control creates an Experiment Event Entity
    Context in the Reliably service.

    The Event has the `event_type` of `ACTIVITY_START`.

    :param context: Activity object representing the Experiment Activity
        that will be executed
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    :param **kwargs: Any additional keyword arguments passed to the control
    """
    try:
        reliably_secrets = secrets.get("reliably", None) if secrets else None
        _create_experiment_event(
            event_type=EventType.ACTIVITY_START,
            name=context["name"],
            output=None,
            experiment_run_labels=configuration["chaosreliably"][
                "experiment_run_labels"
            ],
            configuration=configuration,
            secrets=reliably_secrets,
        )
    except Exception as ex:
        logger.debug(
            f"An error occurred: {ex}, while running the Before Activity control, the"
            " Experiment execution won't be affected."
        )


def after_activity_control(
    context: Activity,
    state: Run,
    configuration: Configuration = None,
    secrets: Secrets = None,
    **kwargs: Any,
) -> None:
    """
    Control run *after* the execution of an Experiment Activity.

    For a given Experiment Activity and its state, the control creates an Experiment
    Event Entity Context in the Reliably service.

    The Event has the `event_type` of `ACTIVITY_END`.

    :param context: Activity object representing the Experiment Activity
        that was executed
    :param state: Run object representing the state of the executed Experiment Activity
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    :param **kwargs: Any additional keyword arguments passed to the control
    """
    try:
        reliably_secrets = secrets.get("reliably", None) if secrets else None
        _create_experiment_event(
            event_type=EventType.ACTIVITY_END,
            name=context["name"],
            output=state,
            experiment_run_labels=configuration["chaosreliably"][
                "experiment_run_labels"
            ],
            configuration=configuration,
            secrets=reliably_secrets,
        )
    except Exception as ex:
        logger.debug(
            f"An error occurred: {ex}, while running the After Activity control, the"
            " Experiment execution won't be affected."
        )


def _create_entity_context_on_reliably(
    entity_context: EntityContext, configuration: Configuration, secrets: Secrets
) -> EntityContext:
    """
    For a given EntityContext, create it on the Reliably services.

    :param entity_context: EntityContext which will be created on the Reliably service
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    :returns: EntityContext representing the EntityContext that was just created
    """
    with get_session(configuration, secrets) as session:
        url = "/entitycontext"
        resp = session.post(url, content=entity_context.json(by_alias=True))
        resp.raise_for_status()
        return entity_context


def _create_experiment(
    experiment_title: str,
    configuration: Configuration,
    secrets: Secrets,
    related_to_labels: List[Dict[str, str]] = [],
) -> EntityContextExperimentLabels:
    """
    For a given Experiment title, create a Experiment Entity Context
    on the Reliably services.

    :param experiment_title: str representing the name of the Experiment
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    :returns: EntityContextExperimentLabels representing the metadata labels of the
        created entity - used for `relatedTo` properties in Reliably
    """
    experiment_entity = EntityContext(
        metadata=EntityContextMetadata(
            labels=EntityContextExperimentLabels(title=experiment_title),
            related_to=related_to_labels,
        )
    )

    created_entity = _create_entity_context_on_reliably(
        entity_context=experiment_entity, configuration=configuration, secrets=secrets
    )
    return cast(
        EntityContextExperimentLabels,
        created_entity.metadata.labels.dict(by_alias=True),
    )


def _create_experiment_version(
    commit_hash: str,
    source: str,
    experiment_labels: EntityContextExperimentLabels,
    configuration: Configuration,
    secrets: Secrets,
) -> EntityContextExperimentVersionLabels:
    """
    For a given commit hash, source link, and Experiment labels, create a
    ExperimentVersion Entity Context on the Reliably services.

    :param commit_hash: str representing the SHA1 Hash of the current commit of the
        Experiments repo at the time of running it
    :param source: str representing the URL to the source control location
        of the Experiment being run
    :param experiment_labels: EntityContextExperimentLabels object representing the
        labels of the Experiment this version is related to
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    :returns: EntityContextExperimentVersionLabels representing the metadata labels
        of the created entity - used for `relatedTo` properties in Reliably
    """
    experiment_version_entity = EntityContext(
        metadata=EntityContextMetadata(
            labels=EntityContextExperimentVersionLabels(
                commit_hash=commit_hash,
                source=source,
            ),
            related_to=[experiment_labels],
        )
    )

    created_entity = _create_entity_context_on_reliably(
        entity_context=experiment_version_entity,
        configuration=configuration,
        secrets=secrets,
    )
    return cast(
        EntityContextExperimentVersionLabels,
        created_entity.metadata.labels.dict(by_alias=True),
    )


def _create_experiment_run(
    user: str,
    experiment_version_labels: EntityContextExperimentVersionLabels,
    configuration: Configuration,
    secrets: Secrets,
) -> EntityContextExperimentRunLabels:
    """
    For a given user and Experiment Version labels, create a ExperimentRun Entity
    Context on the Reliably services.

    :param user: str representing the name of the user that is running the Experiment
    :param experiment_version_labels: EntityContextExperimentVersionLabels object
        representing the labels of the Experiment Version this run is related to
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    :returns: EntityContextExperimentRunLabels representing the metadata labels of
        the created entity - used for `relatedTo` properties in Reliably
    """
    experiment_run_entity = EntityContext(
        metadata=EntityContextMetadata(
            labels=EntityContextExperimentRunLabels(user=user),
            related_to=[experiment_version_labels],
        )
    )

    created_entity = _create_entity_context_on_reliably(
        entity_context=experiment_run_entity,
        configuration=configuration,
        secrets=secrets,
    )
    return cast(
        EntityContextExperimentRunLabels,
        created_entity.metadata.labels.dict(by_alias=True),
    )


def _create_experiment_event(
    event_type: EventType,
    name: str,
    output: Any,
    experiment_run_labels: EntityContextExperimentRunLabels,
    configuration: Configuration,
    secrets: Secrets,
) -> EntityContextExperimentEventLabels:
    """
    For a given event type, name, output, and Experiment Run labels, create a
    ExperimentEvent Entity Context on the Reliably services.

    :param event_type: EventType representing the type of the Event that has happened
    :param name: str representing the name of the Event in the Experiment
    :param output: Any object representing the output of the event in the Experiment
    :param experiment_run_labels: EntityContextExperimentRunLabels object
        representing the labels of the Experiment Run this Event is related to
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    :returns: EntityContextExperimentEventLabels representing the metadata labels of
        the created entity - used for `relatedTo` properties in Reliably
    """
    experiment_event_entity = EntityContext(
        metadata=EntityContextMetadata(
            labels=EntityContextExperimentEventLabels(
                event_type=event_type.value, name=name, output=str(output)
            ),
            related_to=[experiment_run_labels],
        )
    )

    created_entity = _create_entity_context_on_reliably(
        entity_context=experiment_event_entity,
        configuration=configuration,
        secrets=secrets,
    )
    return cast(
        EntityContextExperimentEventLabels,
        created_entity.metadata.labels.dict(by_alias=True),
    )


def _create_experiment_entities_for_before_experiment_control(
    experiment_title: str,
    commit_hash: str,
    source: str,
    user: str,
    configuration: Configuration,
    secrets: Secrets,
    experiment_related_to_labels: List[Dict[str, str]] = [],
) -> EntityContextExperimentRunLabels:
    """
    For a given Experiment title, commit hash, source link and user, create
    an Experiment, Experiment Version, Experiment Run, and Experiment start Entity
    Context on the Reliably services.

    If the Experiment and version already exist, new ones will not be created, however
    a new run is *always* created.

    :param experiment_title: str representing the name of the Experiment
    :param commit_hash: str representing the SHA1 Hash of the current commit of the
        Experiments repo at the time of running it
    :param source: str representing the URL to the source control location
        of the Experiment being run
    :param user: str representing the name of the user that is running the Experiment
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    :returns: EntityContextExperimentRunLabels representing the metadata labels of
        the Experiment Run entity - used for updating the configuration of the
        Experiment so that Events may relate to it
    """
    experiment_labels = _create_experiment(
        experiment_title=experiment_title,
        configuration=configuration,
        secrets=secrets,
        related_to_labels=experiment_related_to_labels,
    )
    experiment_version_labels = _create_experiment_version(
        commit_hash=commit_hash,
        source=source,
        experiment_labels=experiment_labels,
        configuration=configuration,
        secrets=secrets,
    )
    experiment_run_labels = _create_experiment_run(
        user=user,
        experiment_version_labels=experiment_version_labels,
        configuration=configuration,
        secrets=secrets,
    )
    _ = _create_experiment_event(
        event_type=EventType.EXPERIMENT_START,
        name=f"Experiment: {experiment_title} - Started",
        output=None,
        experiment_run_labels=experiment_run_labels,
        configuration=configuration,
        secrets=secrets,
    )
    return experiment_run_labels
