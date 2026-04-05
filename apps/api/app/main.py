from fastapi import FastAPI


app = FastAPI(
    title="Resume Agent API",
    description="Foundation service shell for the Resume Agent platform.",
    version="0.1.0",
)


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "service": "resume-agent-api",
        "status": "ok",
        "phase": "foundations",
    }
