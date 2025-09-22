import httpx
from config import get_settings


async def send_activation_email(email: str, code: str) -> None:
    settings = get_settings()
    
    payload = {
        "to": email,
        "subject": "Your activation code",
        "body": f"Your code is: {code}"
    }
    
    async with httpx.AsyncClient(timeout=settings.email_timeout_seconds) as client:
        resp = await client.post(f"{settings.email_api_base_url}/send", json=payload)
        resp.raise_for_status()
