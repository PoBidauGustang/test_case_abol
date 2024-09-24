import logging
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from redis.asyncio import Redis

from src.api.endpoints.v1 import (
    books,
    users,
)
from src.cache import redis
from src.configs import LOGGING, settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    redis.redis = redis.RedisCache(Redis(**settings.redis.connection_dict))
    await FastAPILimiter.init(Redis(**settings.redis.connection_dict))
    yield
    await redis.redis.close()
    await FastAPILimiter.close()


app = FastAPI(
    title=settings.app.name,
    description=settings.app.description,
    docs_url=settings.app.docs_url,
    openapi_url=settings.app.openapi_url,
    lifespan=lifespan,
)

app.include_router(books.router, prefix="/book/v1/books", tags=["books"])

app.include_router(
    users.router,
    prefix="/book/v1/users",
    tags=["users"],
)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.app.host,
        port=settings.app.port,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
