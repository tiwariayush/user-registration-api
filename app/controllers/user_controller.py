import logging

from fastapi import BackgroundTasks, Depends, status
from fastapi.responses import Response
from fastapi.security import HTTPBasicCredentials

from async_tasks import log_user_activation_task, send_activation_email_task
from errors import AlreadyActive, CodeExpired, InvalidCode, InvalidCredentials
from schemas import ActivateRequest, CreateUserRequest, CreateUserResponse
from services.auth_service import AuthService
from services.user_service import UserService


logger = logging.getLogger(__name__)


class UserController:
    
    def __init__(self, user_service: UserService, auth_service: AuthService):
        self.user_service = user_service
        self.auth_service = auth_service
    
    async def register_user(self, payload: CreateUserRequest, background_tasks: BackgroundTasks) -> CreateUserResponse:
        result = self.user_service.register_user(payload.email, payload.password)
        user = result["user"]
        activation_code = result["activation_code"]

        background_tasks.add_task(send_activation_email_task, payload.email, activation_code)
        
        logger.info(f"User {user['id']} registered, activation email queued")
        return CreateUserResponse(**user)
    
    async def activate_user(self, payload: ActivateRequest, credentials: HTTPBasicCredentials, background_tasks: BackgroundTasks) -> Response:
        user = self.auth_service.authenticate_user(credentials.username, credentials.password)
        if not user:
            raise InvalidCredentials()

        if user["active"]:
            raise AlreadyActive()

        try:
            self.user_service.activate_user(user["id"], payload.code)
            background_tasks.add_task(log_user_activation_task, user["id"])
            
        except (InvalidCode, CodeExpired) as e:
            raise e

        return {"message": "Account activated successfully"}
