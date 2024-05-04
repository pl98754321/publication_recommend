import time

from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI

from .config import VERSION
from .routers import recommend
from .services import get_logger


def add_middleware(app: FastAPI) -> FastAPI:
    logger = get_logger(VERSION)

    @app.middleware("http")
    async def add_process_time_header(request, call_next):
        # get reqest name
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        logger.debug(f"Process time: {process_time:.7f} for {request.url.path}")
        return response

    return app


def init_fastapi() -> FastAPI:
    print("START FASTAPI")
    app = FastAPI()
    origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(recommend.router)
    app = add_middleware(app)

    return app


app = init_fastapi()
