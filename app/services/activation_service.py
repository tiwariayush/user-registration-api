import secrets
import hashlib
from datetime import datetime, timezone, timedelta

from database import get_conn
from config import Settings
from errors import InvalidCode, CodeExpired


class ActivationService:
    
    def __init__(self):
        self.settings = Settings()
    
    def hash_code(self, code: str, salt: bytes) -> bytes:
        h = hashlib.sha256()
        h.update(salt + code.encode())
        return h.digest()

    def create_activation(self, user_id: str, code: str) -> None:
        salt = secrets.token_bytes(self.settings.code_salt_bytes)
        code_hash = self.hash_code(code, salt)
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO activation_codes (user_id, code_hash, salt) VALUES (%s, %s, %s)",
                    (user_id, code_hash, salt)
                )

    def verify_and_use_code(self, user_id: str, code: str) -> None:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, code_hash, salt, created_at, used FROM activation_codes WHERE user_id=%s ORDER BY created_at DESC LIMIT 1",
                    (user_id,)
                )
                row = cur.fetchone()
                if not row:
                    raise InvalidCode()
                code_id, code_hash_db, salt, created_at, used = row
                if used:
                    raise InvalidCode()

                if datetime.now(timezone.utc) - created_at > timedelta(seconds=self.settings.code_ttl_seconds):
                    raise CodeExpired()

                candidate = self.hash_code(code, bytes(salt))
                if candidate != bytes(code_hash_db):
                    raise InvalidCode()

                cur.execute("UPDATE activation_codes SET used=TRUE WHERE id=%s", (code_id,))
                cur.execute("UPDATE users SET active=TRUE WHERE id=%s", (user_id,))
                conn.commit()

