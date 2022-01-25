import secrets

import fastapi.routing
from sqlalchemy.orm import Session

from impressive_strawberry.database import tables
from impressive_strawberry.web import crud
from impressive_strawberry.web import deps
from impressive_strawberry.web import models
from impressive_strawberry.web import responses

router = fastapi.routing.APIRouter(
    prefix="/api/application/v1",
    tags=[
        "Application v1",
    ],
)


@router.post(
    "/",
    summary="Create a new application, and get a token.",
    response_model=models.full.ApplicationFull,
    status_code=201,
)
async def application_create(
        *,
        data: models.edit.ApplicationEdit,
        session: Session = fastapi.Depends(deps.dep_dbsession),
        _secret: None = fastapi.Depends(deps.dep_impressive_secret_required)
):
    return crud.quick_create(session,
                             tables.Application(name=data.name, description=data.description))


@router.get(
    "/this",
    summary="Get the application you're authenticating as.",
    response_model=models.full.ApplicationFull,
)
async def application_this_retrieve(
        *,
        application: tables.Application = fastapi.Depends(deps.dep_application_this),
):
    return application


@router.put(
    "/this",
    summary="Change the details of the application you're authenticating as.",
    response_model=models.full.ApplicationFull,
)
async def application_this_update(
        *,
        application: tables.Application = fastapi.Depends(deps.dep_application_this),
        data: models.edit.ApplicationEdit,
        session: Session = fastapi.Depends(deps.dep_dbsession)
):
    return crud.quick_update(session=session, obj=application, data=data)


@router.delete(
    "/this",
    summary="Delete the application you're authenticating as.",
    status_code=204,
)
async def application_this_delete(
        *,
        application: tables.Application = fastapi.Depends(deps.dep_application_this),
        session: Session = fastapi.Depends(deps.dep_dbsession),
):
    session.delete(application)
    session.commit()
    return responses.raw.NO_CONTENT


@router.patch(
    "/this/revoke",
    summary="Revoke and regenerate the token for the application you're authenticating as.",
    response_model=models.full.ApplicationFull,
)
async def application_this_revoke(
        *,
        application: tables.Application = fastapi.Depends(deps.dep_application_this),
        session: Session = fastapi.Depends(deps.dep_dbsession),
):
    application.token = secrets.token_urlsafe()
    session.commit()
    return application
