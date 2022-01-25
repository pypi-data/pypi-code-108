import fastapi.routing
from sqlalchemy.orm import Session

from impressive_strawberry.database import tables
from impressive_strawberry.web import crud
from impressive_strawberry.web import deps
from impressive_strawberry.web import models
from impressive_strawberry.web import responses

router = fastapi.routing.APIRouter(
    prefix="/api/user/v1",
    tags=[
        "User v1",
    ],
)


@router.get(
    "/",
    summary="Get the users of the application you're authenticating as.",
    response_model=list[models.read.UserRead]
)
async def user_list(
        *,
        application: tables.Application = fastapi.Depends(deps.dep_application_this)
):
    return application.users


@router.get(
    "/{user}",
    summary="Get a specific user that exists within the application you're authenticating as.",
    response_model=models.full.UserFull
)
async def user_retrieve(
        *,
        user: tables.User = fastapi.Depends(deps.dep_user_thisapp)
):
    return user


@router.post(
    "/",
    summary="Add an user to the application you're authenticating as.",
    response_model=models.full.UserFull,
    status_code=201,
)
async def user_create(
        *,
        data: models.edit.UserEdit,
        session: Session = fastapi.Depends(deps.dep_dbsession),
        application: tables.Application = fastapi.Depends(deps.dep_application_this)
):
    return crud.quick_create(session, tables.User(application_id=application.id, crystal=data.crystal))


@router.put(
    "/{user}",
    summary="Update a user within the application you're authenticating as.",
    response_model=models.full.UserFull
)
async def user_update(
        *,
        data: models.edit.UserEdit,
        session: Session = fastapi.Depends(deps.dep_dbsession),
        user: tables.User = fastapi.Depends(deps.dep_user_thisapp)
):
    return crud.quick_update(session, user, data)


@router.delete(
    "/{user}",
    summary="Remove a user within the application you're authenticating as.",
    status_code=204
)
async def user_delete(
        *,
        session: Session = fastapi.Depends(deps.dep_dbsession),
        user: tables.User = fastapi.Depends(deps.dep_user_thisapp)
):
    session.delete(user)
    session.commit()
    return responses.raw.NO_CONTENT
