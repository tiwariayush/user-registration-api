import time
import uuid
import httpx
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("tests")

APP_BASE = "http://app:8000"
MAILER_BASE = "http://mailer:8081"

def setup_module():
    logger.info("Starting Dailymotion Registration API Tests")


def test_full_registration_flow():
    """Test complete user registration and activation flow"""
    email = f"alice-{uuid.uuid4().hex[:8]}@example.com"
    password = "SuperSecret123!"
    
    logger.info(f"Testing full registration flow for {email}")
    
    with httpx.Client() as c:
        logger.info("Registering new user...")
        r = c.post(f"{APP_BASE}/v1/users", json={"email": email, "password": password})
        logger.info(f"Registration response: {r.status_code}")
        assert r.status_code == 201
        
        user_data = r.json()
        user_id = user_data.get('id', 'N/A')
        logger.info(f"User created successfully: {user_id}")
        assert user_data["email"] == email
        assert "id" in user_data
        
        logger.info("Waiting for activation email to be sent...")
        time.sleep(2)
        
        logger.info("Retrieving activation code from mailer...")
        r = httpx.get(f"{MAILER_BASE}/__last_code", params={"email": email}, timeout=2.0)
        assert r.status_code == 200
        code = r.json()["code"]
        logger.info(f"Activation code received: {code}")
        assert len(code) == 4
        
        logger.info("Attempting to activate user account...")
        r = c.post(
            f"{APP_BASE}/v1/users/activate",
            json={"code": code},
            auth=(email, password)
        )
        logger.info(f"Activation response: {r.status_code}")
        assert r.status_code == 200
        response_data = r.json()
        logger.info(f"Activation successful: {response_data}")
        assert "message" in response_data
        
        logger.info("Registration and activation flow completed successfully")


def test_invalid_code():
    """Test that invalid codes are rejected"""
    email = f"bob-{uuid.uuid4().hex[:8]}@example.com"
    password = "TestPass456!"
    
    logger.info(f"Testing invalid code rejection for {email}")
    
    with httpx.Client() as c:
        logger.info("Creating user account...")
        r = c.post(f"{APP_BASE}/v1/users", json={"email": email, "password": password})
        logger.info(f"User registration: {r.status_code}")
        assert r.status_code == 201
        
        logger.info("Attempting activation with invalid code...")
        r = c.post(
            f"{APP_BASE}/v1/users/activate",
            json={"code": "0000"},
            auth=(email, password)
        )
        logger.info(f"Invalid code response: {r.status_code} - {r.text}")
        assert r.status_code == 400
        
        logger.info("Invalid code test passed")


def test_background_task_sends_email():
    """Test that FastAPI BackgroundTasks sends emails asynchronously"""
    email = f"bg-task-{uuid.uuid4().hex[:8]}@example.com"
    password = "StrongPass123!"

    logger.info(f"Testing background email delivery for {email}")

    with httpx.Client() as c:
        logger.info("Registering user to trigger background email task...")
        r = c.post(f"{APP_BASE}/v1/users", json={"email": email, "password": password})
        logger.info(f"Registration status: {r.status_code}")
        assert r.status_code == 201

    logger.info("Checking if background task sent email...")
    for attempt in range(10):
        r = httpx.get(f"{MAILER_BASE}/__last_code", params={"email": email}, timeout=2.0)
        if r.status_code == 200:
            code = r.json()["code"]
            logger.info(f"Background task completed successfully, code: {code}")
            assert len(code) == 4
            return
        if attempt % 2 == 0:
            logger.info(f"Still waiting for background task... ({attempt + 1}/10)")
        time.sleep(0.5)
    
    logger.error(f"Background task failed to send email to {email}")
    raise AssertionError(f"Background task did not send email to {email}")