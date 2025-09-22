from functools import lru_cache

from config import Settings
from services.user_service import UserService
from services.auth_service import AuthService
from controllers.user_controller import UserController


@lru_cache()
def get_settings() -> Settings:
    """Get Settings instance (singleton)"""
    return Settings()


@lru_cache()
def get_user_service() -> UserService:
    """Get UserService instance (singleton)"""
    return UserService(settings=get_settings())


@lru_cache()
def get_auth_service() -> AuthService:
    """Get AuthService instance (singleton)"""
    return AuthService()


@lru_cache()
def get_user_controller() -> UserController:
    """Get UserController instance with injected dependencies"""
    return UserController(
        user_service=get_user_service(),
        auth_service=get_auth_service()
    )
