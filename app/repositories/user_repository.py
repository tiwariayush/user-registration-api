import logging
from typing import Any, Dict

from database import get_conn

logger = logging.getLogger(__name__)


class UserRepository:
    
    @staticmethod
    def create_user(email: str, password_hash: bytes) -> Dict[str, Any]:
        import psycopg
        
        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id, email, created_at, active",
                        (email, password_hash)
                    )
                    row = cur.fetchone()
                    conn.commit()
                    return {
                        "id": str(row[0]),
                        "email": row[1],
                        "created_at": row[2].isoformat(),
                        "active": row[3],
                    }
        except psycopg.errors.UniqueViolation:
            logger.debug(f"Duplicate email attempted: {email}")
            from errors import EmailAlreadyUsed
            raise EmailAlreadyUsed()
        except Exception as e:
            logger.error(f"Database error creating user: {e}")
            raise

    @staticmethod
    def email_exists(email: str) -> bool:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM users WHERE email=%s", (email,))
                return cur.fetchone() is not None

