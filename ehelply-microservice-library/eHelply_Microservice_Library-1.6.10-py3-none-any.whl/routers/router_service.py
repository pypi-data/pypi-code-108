"""
3rd Party Libraries
Not much interesting here. We have some default imports for FastAPI endpoints and common SQL Alchemy use cases
"""
from fastapi import APIRouter, Body, Depends

"""
eHelply Bootstrapper
Now we are getting interesting.
- State provides you with access to the app state
- get_db is used with Dependency injection to obtain a fresh DB connection session
    `db: Session = Depends(get_db)`
- Responses imports a bunch of default HTTP responses that eHelply has standardized on. Use these where possible as your
    return from each endpoint
"""
from ehelply_bootstrapper.utils.state import State
from ehelply_bootstrapper.drivers.fast_api_utils.responses import *

"""
Service Template Integration Dependency Injection
Super duper interesting!
This imports ALL of the integration dependency injection functions. Examples of how these are used are shown in the 
  endpoints below
"""
from ehelply_microservice_library.integrations.router_integrations import *

"""
Router
This is a self-contained router instance. By itself it does nothing, but by attaching endpoints to it using decorator
  notation, you can make an epic router!
"""
router = APIRouter()


@router.post(
    '/db/migrate',
    tags=["db"],
)
async def db_migrate():
    """
    Runs DB migrations
    :return:
    """
    try:
        State.logger.info("Running Migrations..")
        from alembic.config import Config
        import alembic.command

        config = Config('alembic.ini')
        config.attributes['configure_logger'] = False

        alembic.command.upgrade(config, 'head')
    except:
        return http_400_bad_request(error_message="Migrations failed")

    return http_200_ok({"message": "Migrations complete"})


@router.post(
    '/db/migrate/create',
    tags=["db"],
)
async def db_create_migration(data: dict = Body({})):
    """
    Runs DB migrations
    :return:
    """
    try:
        State.logger.info("Creating migration..")
        from alembic.config import Config
        import alembic.command

        config = Config('alembic.ini')
        config.attributes['configure_logger'] = False

        alembic.command.revision(config, autogenerate=True, message=data['message'])
    except:
        return http_400_bad_request(error_message="Creating migration failed")

    return http_200_ok({"message": "Creating migration complete"})


@router.post(
    '/install',
    tags=["service"],
)
async def service_install(integrations: Integrations = Depends(get_integrations), data: dict = Body({})):
    """
    Runs the microservice installer
    :return:
    """
    result = await State.bootstrapper.install(integrations, data)
    if result:
        response = {"message": "Installation complete"}
        if not isinstance(result, bool) and result is not None:
            response['result'] = result
        return http_200_ok(response)

    return http_500_error(error_message="Installation failed")


@router.post(
    '/seed',
    tags=["service"],
)
async def service_seed(integrations: Integrations = Depends(get_integrations), data: dict = Body({})):
    """
    Runs the microservice seeder
    :return:
    """
    result = await State.bootstrapper.seed(integrations, data)
    if result:
        response = {"message": "Seeding complete"}
        if not isinstance(result, bool) and result is not None:
            response['result'] = result
        return http_200_ok(response)

    return http_500_error(error_message="Seeding failed")
