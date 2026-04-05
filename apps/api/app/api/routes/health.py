from fastapi import APIRouter

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("")
def healthcheck() -> dict[str, str]:
    return {
        "service": "resume-agent-api",
        "status": "ok",
    }
