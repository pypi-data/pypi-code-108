import logging
import os

import alembic.config
import dotenv
import fastapi.middleware.cors as cors
import uvicorn

logging.basicConfig(level="DEBUG")
log = logging.getLogger(__name__)

dotenv.load_dotenv(".env", override=True)
dotenv.load_dotenv(".env.local", override=True)

from impressive_strawberry.web.app import app

log.info("Running migrations with Alembic...")
alembic.config.main(argv=["--raiseerr", "upgrade", "head"])
log.info("Creating CORS middleware...")
app.add_middleware(
    cors.CORSMiddleware,
    allow_origins=os.environ["CORS_ALLOW_ORIGINS"].split(" "),
    allow_methods=["*"],
    allow_headers=["*"],
)
log.info("Running impressive_strawberry with Uvicorn...")
# noinspection PyTypeChecker
uvicorn.run(app, port=int(os.environ["IS_WEB_PORT"]), host=os.environ["IS_WEB_HOST"])
