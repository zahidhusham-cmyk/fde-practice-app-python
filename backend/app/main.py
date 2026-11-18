from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import SessionLocal, init_db
from app.routers import drivers, health, shipments
from app.seed import seed_if_empty


def create_app(*, seed_on_startup: bool = True) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        if seed_on_startup:
            init_db()
            with SessionLocal() as session:
                seed_if_empty(session)
        yield

    app = FastAPI(title="Harborline Dispatch API", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router)
    app.include_router(shipments.router)
    app.include_router(drivers.router)
    return app


app = create_app()
