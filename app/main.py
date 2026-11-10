from fastapi import FastAPI

from app.routers import cover, resume, vacancies

app = FastAPI(
    title="Evelyn API",
    description="AI-powered job search assistant API",
    version="0.1.0",
)

app.include_router(vacancies.router)
app.include_router(resume.router)
app.include_router(cover.router)


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok", "app": "evelyn"}
