import pathlib

import fastapi
import pkg_resources
import sqlalchemy.exc

from impressive_strawberry.web.errors import StrawberryException
from impressive_strawberry.web.handlers import handle_strawberry_error, handle_sqlalchemy_not_found, handle_sqlalchemy_multiple_results, handle_generic_error
from impressive_strawberry.web.routes.api.achievement.v1.router import router as router_api_achievements_v1
from impressive_strawberry.web.routes.api.application.v1.router import router as router_api_application_v1
from impressive_strawberry.web.routes.api.group.v1.router import router as router_api_group_v1
from impressive_strawberry.web.routes.api.unlock.v1.router import app_router as router_api_unlock_v1_app
from impressive_strawberry.web.routes.api.unlock.v1.router import group_router as router_api_unlock_v1_group
from impressive_strawberry.web.routes.api.unlock.v1.router import token_router as router_api_unlock_v1_token
from impressive_strawberry.web.routes.api.user.v1.router import router as router_api_user_v1
from impressive_strawberry.web.routes.api.webhook.v1.router import router as router_api_webhook_v1
from impressive_strawberry.web.routes.root import home as route_home

with open(pathlib.Path(__file__).parent.joinpath("description.md")) as file:
    description = file.read()

app = fastapi.FastAPI(
    debug=__debug__,
    title="Impressive Strawberry",
    description=description,
    version=pkg_resources.get_distribution("impressive_strawberry").version,
)
app.include_router(router_api_application_v1)
app.include_router(router_api_group_v1)
app.include_router(router_api_achievements_v1)
app.include_router(router_api_user_v1)
app.include_router(router_api_unlock_v1_app)
app.include_router(router_api_unlock_v1_group)
app.include_router(router_api_unlock_v1_token)
app.include_router(router_api_webhook_v1)
app.add_route("/", route_home, methods=["GET"])

app.add_exception_handler(StrawberryException, handle_strawberry_error)
app.add_exception_handler(sqlalchemy.exc.NoResultFound, handle_sqlalchemy_not_found)
app.add_exception_handler(sqlalchemy.exc.MultipleResultsFound, handle_sqlalchemy_multiple_results)
app.add_exception_handler(Exception, handle_generic_error)
