from ehelply_bootstrapper.utils.environment import Environment


def _get_environment_name() -> str:
    """
    Maps the dev environment to test as we don't store secrets specific to dev.

    Returns:

    """
    environment_name: str = Environment.stage()
    if environment_name == "dev":
        environment_name = "test"
    return environment_name


def secret_name_database():
    """
    AWS ASM secret name for database credentials

    Returns:
        None

    """
    return "ehelply-{environment}.db-rds.ehelply-{environment}-main.ehelply-secure-microservice".format(
        environment=_get_environment_name())


def secret_name_facts_vault():
    """
    AWS ASM secret name for access to the facts vault

    Returns:
        None

    """
    return "ehelply-{environment}.microservices.ehelply-facts.vault".format(environment=_get_environment_name())


def secret_name_security_vault():
    """
    AWS ASM secret name for access to the security vault

    Returns:
        None

    """
    return "ehelply-{environment}.microservices.ehelply-security.vault".format(environment=_get_environment_name())


def secret_name_updater_vault():
    """
    AWS ASM secret name for access to the updater vault

    Returns:
        None

    """
    return "ehelply-all.microservices.ehelply-updater.vault".format(environment=_get_environment_name())
