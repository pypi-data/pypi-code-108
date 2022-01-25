import fastapi.routing
from sqlalchemy.orm import Session

from impressive_strawberry.database import tables
from impressive_strawberry.web import crud
from impressive_strawberry.web import deps
from impressive_strawberry.web import models
from impressive_strawberry.web import responses

router = fastapi.routing.APIRouter(
    prefix="/api/achievement/v1",
    tags=[
        "Achievements v1",
    ],
)


@router.get(
    "/",
    summary="Get the achievements of a certain group within the application you're authenticating as.",
    response_model=list[models.read.AchievementRead],
)
async def achievement_list(
        *,
        group: tables.Group = fastapi.Depends(deps.dep_group_thisapp),
):
    return group.achievements


@router.get(
    "/{achievement}",
    summary="Get the details of an achievement belonging to a certain group within the application you're authenticating as.",
    response_model=models.full.AchievementFull,
)
async def achievement_retrieve(
        *,
        achievement: tables.Achievement = fastapi.Depends(deps.dep_achievement_thisapp),
):
    return achievement


@router.post(
    "/",
    summary="Create a new achievement belonging to a certain group within the application you're authenticating as.",
    response_model=models.full.AchievementFull,
    status_code=201,
)
async def achievement_create(
        *,
        data: models.edit.AchievementEdit,
        session: Session = fastapi.Depends(deps.dep_dbsession),
        group: tables.Group = fastapi.Depends(deps.dep_group_thisapp),
):
    return crud.quick_create(session, tables.Achievement(
        name=data.name,
        description=data.description,
        alloy=data.alloy,
        secret=data.secret,
        icon=data.icon,
        repeatable=data.repeatable,
        group=group,
        crystal=data.crystal,
    ))


@router.put(
    "/{achievement}",
    summary="Update an achievement belonging to a certain group within the application you're authenticating as.",
    response_model=models.full.AchievementFull
)
async def achievement_update(
        *,
        data: models.edit.AchievementEdit,
        achievement: tables.Achievement = fastapi.Depends(deps.dep_achievement_thisapp),
        session: Session = fastapi.Depends(deps.dep_dbsession)
):
    return crud.quick_update(session, achievement, data)


@router.delete(
    "/{achievement}",
    summary="Delete an achievement belonging to a certain group within the application you're authenticating as.",
    status_code=204,
)
async def achievement_delete(
        *,
        achievement: tables.Achievement = fastapi.Depends(deps.dep_achievement_thisapp),
        session: Session = fastapi.Depends(deps.dep_dbsession)
):
    session.delete(achievement)
    session.commit()
    return responses.raw.NO_CONTENT
