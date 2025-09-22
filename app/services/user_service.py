import secrets
import logging
from typing import Any, Dict, Optional

from config import Settings
from errors import EmailAlreadyUsed
from repositories.user_repository import UserRepository
from services.activation_service import ActivationService
from services.auth_service import AuthService

logger = logging.getLogger(__name__)


class UserService:
    
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
    
    def register_user(self, email: str, password: str) -> Dict[str, Any]:
        logger.info(f"Registering user: {email}")
        
        pwd_hash = AuthService.hash_password(password, rounds=self.settings.bcrypt_rounds)
        code = f"{secrets.randbelow(10000):04d}"

        try:
            user = UserRepository.create_user(email, pwd_hash)
            
            activation_service = ActivationService()
            activation_service.create_activation(user["id"], code)
            
            logger.info(f"User registered successfully: {user['id']}")
            return {"user": user, "activation_code": code}
        except EmailAlreadyUsed:
            logger.warning(f"Registration failed - email already exists: {email}")
            raise
    
    def activate_user(self, user_id: str, activation_code: str) -> None:
        try:
            activation_service = ActivationService()
            activation_service.verify_and_use_code(user_id, activation_code)
            logger.info(f"User activated: {user_id}")
        except Exception as e:
            logger.warning(f"Activation failed for user {user_id}: {e}")
            raise
