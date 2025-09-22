import logging

from email_client import send_activation_email

logger = logging.getLogger(__name__)


async def send_activation_email_task(email: str, code: str) -> None:
    max_retries = 3
    for attempt in range(max_retries):
        try:
            await send_activation_email(email, code)
            logger.info(f"Activation email sent successfully to {email}")
            return
        except Exception as e:
            logger.warning(f"Email send attempt {attempt + 1}/{max_retries} failed for {email}: {e}")
            if attempt == max_retries - 1:
                logger.error(f"All email send attempts failed for {email}. User will need manual assistance.")
            else:
                import asyncio
                await asyncio.sleep(2 ** attempt)


def log_user_activation_task(user_id: str) -> None:
    logger.info(f"User {user_id} successfully activated")


def log_email_failure_task(email: str, error: str, context: str) -> None:
    logger.warning(f"Email send failed for {email} in {context}: {error}")
