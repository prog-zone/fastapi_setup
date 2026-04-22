import time
from fastapi import FastAPI, Request, Response
from contextlib import asynccontextmanager
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings
from app.core.database import engine
from app.core.limiter import limiter

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield 
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan
)

async def custom_rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    # 1. Use dummy response to let slowapi calculate the wait time
    dummy_response = Response()
    dummy_response = request.app.state.limiter._inject_headers(
        dummy_response, request.state.view_rate_limit
    )
    
    # 2. Extract ONLY the retry-after value (defaults to "60" if missing)
    retry_after = dummy_response.headers.get("retry-after", "60")

    # 3. Return the JSON response with ONLY the specific header we want
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Too Many Requests",
            "message": f"Rate limit exceeded. Please try again in {retry_after} seconds.",
            "wait_seconds": int(retry_after)
        },
        headers={"Retry-After": retry_after}
    )

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_exceeded_handler)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": f"{settings.PROJECT_NAME} API is running"}