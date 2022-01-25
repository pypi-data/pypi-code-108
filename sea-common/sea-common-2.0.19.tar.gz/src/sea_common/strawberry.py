import os
from datetime import datetime
from typing import Optional, TypedDict, Union
from enum import Enum

import json
from fastapi import HTTPException
import strawberry
from strawberry.asgi import GraphQL, Request, Response, WebSocket
from strawberry.extensions import Extension

from .config import settings


@strawberry.interface
class CreateUpdateFields:
    # Keep track when records are created and updated.
    created_at: Optional[datetime]


class UserPayloadDict(TypedDict):
    id: int
    username: str
    email: str


class MyContext(TypedDict):
    request: Union[Request, WebSocket]
    response: Optional[Response]
    current_user: Optional[UserPayloadDict]


class MyGraphQL(GraphQL):
    async def get_context(
        self,
        request: Union[Request, WebSocket],
        response: Optional[Response] = None,
    ) -> Optional[MyContext]:
        user_header: Optional[str] = request.headers.get('CurrentUser')
        user_payload: Optional[UserPayloadDict] = json.loads(user_header) if user_header else None

        return {
            'request': request,
            'response': response,
            'current_user': user_payload,
        }


class AuthExtension(Extension):
    def on_request_start(self):
        if (
            self.execution_context.context.get('current_user')  # Valid login credentials provided.
            or (os.environ.get('FASTAPI_ENV') == 'development'
            and (
                self.execution_context.query ==  # Subgraph introspection.
                'query SubgraphIntrospectQuery {\n    # eslint-disable-next-line\n    _service {\n        sdl\n    }\n}'
                or self.execution_context.context.get('request').headers.get('referer')
                == f'https://localhost/api/{settings.SERVER_ID}/graphql'  # GraphiQL request.
            )
        )
            # or current_app.config['TESTING']  # Test environment
        ):
            return
        else:
            raise HTTPException(status_code=401, detail='Invalid credentials provided.')


@strawberry.interface
class MutationResponse:
    success: bool
    message: str


@strawberry.enum(description='Selection of organisms.')
class OrganismSelect(Enum):
    NONE = ''
    HUMAN = 'human'
    MOUSE = 'mouse'
    RAT = 'rat'


organism_mapping = {
    'human': 9606,
    'mouse': 10090,
    'rat': 10116,
}


@strawberry.input
class InputWithOrganism:
    organism: Optional[OrganismSelect] = ''
