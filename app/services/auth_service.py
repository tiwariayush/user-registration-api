import bcrypt
import logging
from typing import Any, Dict, Optional

from database import get_conn

logger = logging.getLogger(__name__)


class AuthService:
    
    @staticmethod
    def hash_password(password: str, rounds: int) -> bytes:
        salt = bcrypt.gensalt(rounds=rounds)
        return bcrypt.hashpw(password.encode(), salt)

    @staticmethod
    def verify_password(password: str, password_hash: bytes) -> bool:
        try:
            return bcrypt.checkpw(password.encode(), password_hash)
        except ValueError:
            return False

    @staticmethod
    def fetch_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, email, created_at, active FROM users WHERE email=%s", (email,))
                row = cur.fetchone()
                if not row:
                    return None
                return {
                    "id": str(row[0]),
                    "email": row[1],
                    "created_at": row[2].isoformat(),
                    "active": row[3],
                }
    
    @staticmethod
    def verify_user_password(email: str, password: str) -> bool:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT password_hash FROM users WHERE email=%s", (email,))
                row = cur.fetchone()
                if not row:
                    return False
                return AuthService.verify_password(password, bytes(row[0]))
    
    @staticmethod
    def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
        if not AuthService.verify_user_password(email, password):
            logger.warning(f"Authentication failed for user: {email}")
            return None
            
        user = AuthService.fetch_user_by_email(email)
        logger.info(f"User authenticated: {email}")
        return user
    
    @staticmethod
    def is_user_active(user: Dict[str, Any]) -> bool:
        return user.get("active", False)
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        return AuthService.fetch_user_by_email(email)
