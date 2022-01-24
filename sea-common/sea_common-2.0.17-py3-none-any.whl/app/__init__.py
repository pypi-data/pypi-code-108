from fastapi import FastAPI, Request

from ..config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=f'SEA Web Services - {settings.SERVER_ID}',
        openapi_url=f'/api/{settings.SERVER_ID}/openapi.json',
        docs_url=f'/api/{settings.SERVER_ID}/docs',
        redoc_url=f'/api/{settings.SERVER_ID}/redoc',
    )

    @app.get(f'/api/{settings.SERVER_ID}/')
    async def index():
        return {'message': f'{settings.SERVER_ID.upper()} service is up!'}

    @app.middleware('http')
    async def add_header(request: Request, call_next):
        response = await call_next(request)
        response.headers['server-id'] = settings.SERVER_ID

        return response

    return app
