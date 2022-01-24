from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from whale_googleanalytics.server.routes.routes_gcp import router as routes_gcp

app = FastAPI()

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(routes_gcp, tags=["api"], prefix="/api")

# Get routes
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to Google Analytics"}


def pytest():
    return app
