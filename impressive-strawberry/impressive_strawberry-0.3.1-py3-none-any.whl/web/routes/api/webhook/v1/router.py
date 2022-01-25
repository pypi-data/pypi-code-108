import fastapi.routing
from sqlalchemy.orm import Session

from impressive_strawberry.database import tables
from impressive_strawberry.web import crud
from impressive_strawberry.web import deps
from impressive_strawberry.web import models
from impressive_strawberry.web import responses

router = fastapi.routing.APIRouter(
    prefix="/api/webhook/v1",
    tags=[
        "Webhook v1",
    ],
)


@router.get(
    "/",
    summary="Get the webhooks of a certain group within the application you're authenticating as.",
    response_model=list[models.read.WebhookRead],
)
async def webhook_list(
        *,
        group: tables.Group = fastapi.Depends(deps.dep_group_thisapp),
):
    return group.webhooks


@router.get(
    "/{webhook}",
    summary="Get the details of a webhook belonging to a certain group within the application you're authenticating as.",
    response_model=models.full.WebhookFull,
)
async def webhook_retrieve(
        *,
        webhook: tables.Webhook = fastapi.Depends(deps.dep_webhook_thisapp),
):
    return webhook


@router.post(
    "/",
    summary="Add a new webhook to a certain group within the application you're authenticating as.",
    response_model=models.full.WebhookFull,
    status_code=201,
)
async def webhook_create(
        *,
        data: models.edit.WebhookEdit,
        session: Session = fastapi.Depends(deps.dep_dbsession),
        group: tables.Group = fastapi.Depends(deps.dep_group_thisapp),
):
    return crud.quick_create(session, tables.Webhook(
        url=data.url,
        kind=data.kind,
        group=group,
    ))


@router.put(
    "/{webhook}",
    summary="Update a webhook belonging to a certain group within the application you're authenticating as.",
    response_model=models.full.WebhookFull
)
async def webhook_update(
        *,
        data: models.edit.WebhookEdit,
        webhook: tables.Webhook = fastapi.Depends(deps.dep_webhook_thisapp),
        session: Session = fastapi.Depends(deps.dep_dbsession)
):
    return crud.quick_update(session, webhook, data)


@router.delete(
    "/{webhook}",
    summary="Delete a webhook belonging to a certain group within the application you're authenticating as.",
    status_code=204,
)
async def webhook_delete(
        *,
        webhook: tables.Webhook = fastapi.Depends(deps.dep_webhook_thisapp),
        session: Session = fastapi.Depends(deps.dep_dbsession)
):
    session.delete(webhook)
    session.commit()
    return responses.raw.NO_CONTENT
