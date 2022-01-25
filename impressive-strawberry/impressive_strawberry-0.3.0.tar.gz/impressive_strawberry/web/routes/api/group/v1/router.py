import fastapi.routing
from sqlalchemy.orm import Session

from impressive_strawberry.database import tables
from impressive_strawberry.web import crud
from impressive_strawberry.web import deps
from impressive_strawberry.web import models
from impressive_strawberry.web import responses

router = fastapi.routing.APIRouter(
    prefix="/api/group/v1",
    tags=[
        "Group v1",
    ],
)


@router.get(
    "/",
    summary="Get the groups of the application you're authenticating as.",
    response_model=list[models.read.GroupRead],
)
async def group_list(
        *,
        application: tables.Application = fastapi.Depends(deps.dep_application_this),
):
    return application.groups


@router.get(
    "/{group}",
    summary="Get a specific group that exists within the application you're authenticating as.",
    response_model=models.full.GroupFull
)
async def group_retrieve(
        *,
        group: tables.Group = fastapi.Depends(deps.dep_group_thisapp),
):
    return group


@router.post(
    "/",
    summary="Add a group to the application you're authenticating as.",
    response_model=models.full.GroupFull,
    status_code=201,
)
async def group_create(
        *,
        data: models.edit.GroupEdit,
        session: Session = fastapi.Depends(deps.dep_dbsession),
        application: tables.Application = fastapi.Depends(deps.dep_application_this)
):
    return crud.quick_create(session, tables.Group(crystal=data.crystal, application_id=application.id))


@router.put(
    "/{group}",
    summary="Update a group within the application you're authenticating as.",
    response_model=models.full.GroupFull
)
async def group_update(
        *,
        data: models.edit.GroupEdit,
        session: Session = fastapi.Depends(deps.dep_dbsession),
        group: tables.Group = fastapi.Depends(deps.dep_group_thisapp),
):
    return crud.quick_update(session, group, data)


@router.delete(
    "/{group}",
    summary="Delete a group within the application you're authenticating as.",
    status_code=204
)
async def group_delete(
        *,
        session: Session = fastapi.Depends(deps.dep_dbsession),
        group: tables.Group = fastapi.Depends(deps.dep_group_thisapp),
):
    session.delete(group)
    session.commit()
    return responses.raw.NO_CONTENT
