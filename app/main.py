
from fastapi import FastAPI

from app.routers.jobs import router as jobs_router
from app.routers.certificates import router as certificates_router

app = FastAPI(
    title="Bulk Certificate Generator API",
    description="API for generating certificates in bulk",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "Bulk Certificate Generator API is running"
    }


app.include_router(jobs_router)
app.include_router(certificates_router)
