import fastapi.routing
from sqlalchemy.orm import Session
from sqlalchemy.sql import select

from impressive_strawberry.database import tables
from impressive_strawberry.web import crud
from impressive_strawberry.web import deps
from impressive_strawberry.web import models
from impressive_strawberry.web import responses
from impressive_strawberry.web.errors import DuplicatingUnrepeatableUnlock
from impressive_strawberry.webhooks import notify_unlock

app_router = fastapi.routing.APIRouter(
    prefix="/api/unlock/v1",
    tags=[
        "Unlock v1",
    ],
)

group_router = fastapi.routing.APIRouter(
    prefix="/api/unlock-group/v1",
    tags=[
        "Unlock v1",
    ]
)

token_router = fastapi.routing.APIRouter(
    prefix="/api/unlock-direct/v1",
    tags=[
        "Unlock v1",
    ]
)


@group_router.get(
    "/",
    summary="List unlocked achievements obtained by a certain user in a certain group, both belonging to the same application you're authenticating as.",
    response_model=list[models.full.UnlockFull],
)
async def group_unlock_list(
        *,
        session: Session = fastapi.Depends(deps.dep_dbsession),
        group: tables.Group = fastapi.Depends(deps.dep_group_thisapp),
        user: tables.User = fastapi.Depends(deps.dep_user_thisapp),
):
    data = session.execute(
        select(tables.Unlock).where(tables.Unlock.user == user).join(tables.Achievement).where(tables.Achievement.group == group)
    ).all()
    return list(map(lambda d: d[0], data))


@app_router.post(
    "/",
    summary="Adds a certain achievement of a group to a user, both belonging to the same application you're authenticating as.",
    response_model=models.full.UnlockFull,
    status_code=201,
)
async def unlock_create(
        *,
        session: Session = fastapi.Depends(deps.dep_dbsession),
        achievement: tables.Achievement = fastapi.Depends(deps.dep_achievement_thisapp),
        user: tables.User = fastapi.Depends(deps.dep_user_thisapp),
):
    if achievement in [u.achievement for u in user.unlocks] and not achievement.repeatable:
        raise DuplicatingUnrepeatableUnlock()
    unlock = crud.quick_create(session, tables.Unlock(achievement_id=achievement.id, user_id=user.id))
    await notify_unlock(group=achievement.group, unlock=unlock)
    return unlock


@app_router.delete(
    "/{unlock}",
    summary="Removes an unlock of an user belonging to the application you're authenticating as.",
    status_code=204,
)
async def unlock_delete(
        *,
        unlock: tables.Unlock = fastapi.Depends(deps.dep_unlock_thisapp),
        session: Session = fastapi.Depends(deps.dep_dbsession),
):
    session.delete(unlock)
    session.commit()
    return responses.raw.NO_CONTENT


@token_router.post(
    "/",
    summary="Adds a certain achievement of a group to a user, both belonging to the same application, using a token.",
    status_code=201,
)
async def direct_unlock_create(
        *,
        session: Session = fastapi.Depends(deps.dep_dbsession),
        achievement: tables.Achievement = fastapi.Depends(deps.dep_achievement_token),
        user: tables.User = fastapi.Depends(deps.dep_user_token)
):
    if achievement in [u.achievement for u in user.unlocks] and not achievement.repeatable:
        raise DuplicatingUnrepeatableUnlock()
    unlock = crud.quick_create(session, tables.Unlock(achievement_id=achievement.id, user_id=user.id))
    await notify_unlock(group=achievement.group, unlock=unlock)
    return unlock
