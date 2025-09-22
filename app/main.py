import logging

from fastapi import BackgroundTasks, Depends, FastAPI
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from config import Settings
from controllers.health_controller import HealthController
from controllers.user_controller import UserController
from dependencies import get_user_controller
from middleware.rate_limiting import InMemoryRateLimiter, RateLimitMiddleware
from middleware.security_middleware import SecurityMiddleware
from schemas import ActivateRequest, CreateUserRequest, CreateUserResponse

def create_app() -> FastAPI:
    settings = Settings()
    
    app = FastAPI(
        title="Dailymotion Registration API", 
        version="1.0.0",
        description="User registration API with email verification and activation codes",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    logger = logging.getLogger("uvicorn")
    logger.setLevel(getattr(logging, settings.log_level.upper()))

    rate_limiter = InMemoryRateLimiter()
    app.add_middleware(RateLimitMiddleware, limiter=rate_limiter)
    app.add_middleware(SecurityMiddleware)
    
    return app


security = HTTPBasic()
app = create_app()

@app.get("/health")
def health():
    return HealthController.check_health()


@app.post("/v1/users", response_model=CreateUserResponse, status_code=201)
async def register_user(
    payload: CreateUserRequest,
    background_tasks: BackgroundTasks,
    controller: UserController = Depends(get_user_controller)
):
    return await controller.register_user(payload, background_tasks)


@app.post("/v1/users/activate")
async def activate_user(
    payload: ActivateRequest,
    background_tasks: BackgroundTasks,
    credentials: HTTPBasicCredentials = Depends(security),
    controller: UserController = Depends(get_user_controller)
):
    return await controller.activate_user(payload, credentials, background_tasks)
