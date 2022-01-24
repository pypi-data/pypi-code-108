from pydantic import Field

DEPLOYMENT_FIELD_FLAG = 'deployment_field'


def DeploymentField(*args, **kwargs):
    """
    Has the same functionality as pydantic `Field` but adds a flag to mark the field as deployment attribute that
    responsible for the decision which deployment config to load.
    """
    if kwargs.get(DEPLOYMENT_FIELD_FLAG):
        raise ValueError(f'Cannot use "{DEPLOYMENT_FIELD_FLAG}" key inside `DeploymentField()`.')
    return Field(*args, **kwargs, **{DEPLOYMENT_FIELD_FLAG: True})


