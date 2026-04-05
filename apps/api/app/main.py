from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.sessions import router as session_router
from app.api.routes.vault import router as vault_router
from app.config import get_settings
from app.db.session import initialize_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


settings = get_settings()


app = FastAPI(
    title=settings.app_name,
    description="Foundation service shell for the Resume Agent platform.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(session_router)
app.include_router(vault_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "service": "resume-agent-api",
        "status": "ok",
        "phase": "foundations",
    }
