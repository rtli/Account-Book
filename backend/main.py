from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend import constants as C
from backend.database import init_db
from backend.routers import category, data, spending, statistics

app = FastAPI(title=C.APP_TITLE, version=C.APP_VERSION)

# CORS for frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=C.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(spending.router)
app.include_router(category.router)
app.include_router(statistics.router)
app.include_router(data.router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": C.APP_VERSION}
