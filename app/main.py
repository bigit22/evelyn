from fastapi import FastAPI

app = FastAPI(
    title="Evelyn",
    description="AI-powered job search assistant",
    version="0.1.0",
)


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok", "name": "evelyn"}
