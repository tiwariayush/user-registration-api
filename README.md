# Dailymotion Registration API

User registration API with email verification and 4-digit activation codes.

## Features

- User registration with email and password
- 4-digit activation codes sent via email
- Basic Auth for activation
- Configurable code expiration (default 1 minute) >> in testing its 2 seconds
- Rate limiting for security
- FastAPI with PostgreSQL

## Requirements

- Docker & Docker Compose

## Setup

Start all services:
```bash
docker compose up -d
```

This starts:
- API server on http://localhost:8000
- Mock email service on http://localhost:8081
- PostgreSQL database

## Testing

Run the test suite:
```bash
docker compose up tests
```

Or with fresh build:
```bash
docker compose up --build tests
```


## Manual Testing Instructions

### Step 1: Start the services
```bash
docker compose up -d
```

Wait for all services to be healthy (about 10 seconds).

### Step 2: Register a new user
```bash
curl -X POST http://localhost:8000/v1/users \
  -H 'Content-Type: application/json' \
  -d '{"email":"test@example.com","password":"testpass123"}'
```

Expected response (201):
```json
{
  "id": "some-uuid",
  "email": "test@example.com", 
  "created_at": "2024-01-01T12:00:00Z",
  "active": false
}
```

### Step 3: Get the activation code
The mock mailer stores the last sent code. Retrieve it:
```bash
curl 'http://localhost:8081/__last_code?email=test@example.com'
```

Expected response (200):
```json
{"email": "test@example.com", "code": "1234"}
```

### Step 4: Generate Basic Auth token
```bash
echo -n 'test@example.com:testpass123' | base64
```
Result: `dGVzdEBleGFtcGxlLmNvbTp0ZXN0cGFzczEyMw==`

### Step 5: Activate the user account
Use the code from step 3 with the Basic Auth token:
**(Adjust token and code according to last results)**
```bash
curl -X POST http://localhost:8000/v1/users/activate \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Basic dGVzdEBleGFtcGxlLmNvbTp0ZXN0cGFzczEyMw==' \
  -d '{"code":"3349"}'
```

Expected response (200):
```json
{"message": "Account activated successfully"}
```

### Step 6: Test invalid code
Register a new user and try with wrong code:
```bash
# Register new user
curl -X POST http://localhost:8000/v1/users \
  -H 'Content-Type: application/json' \
  -d '{"email":"test2@example.com","password":"testpass123"}'

# Try with invalid code (should fail)
curl -X POST http://localhost:8000/v1/users/activate \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Basic dGVzdDJAZXhhbXBsZS5jb206dGVzdHBhc3MxMjM=' \
  -d '{"code":"0000"}'
```

Expected response (400):
```json
{
  "detail": {
    "error": "INVALID_CODE",
    "message": "Invalid activation code.", 
    "code": "DM_REG_004"
  }
}
```

### Step 7: Verify activation worked
Try to activate again with the same code:
```bash
curl -X POST http://localhost:8000/v1/users/activate \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Basic dGVzdEBleGFtcGxlLmNvbTp0ZXN0cGFzczEyMw==' \
  -d '{"code":"1234"}'
```

Expected response (409):
```json
{
  "detail": {
    "error": "ALREADY_ACTIVE",
    "message": "Account already active.",
    "code": "DM_REG_005"
  }
}
```

### Step 6: Test code expiration
Register another user and wait for the code to expire:
```bash
# Register
curl -X POST http://localhost:8000/v1/users \
  -H 'Content-Type: application/json' \
  -d '{"email":"test2@example.com","password":"testpass123"}'

# Wait 70 seconds (codes expire after 60 seconds in production)
sleep 70

# Get the code
curl 'http://localhost:8081/__last_code?email=test2@example.com'

# Try to activate with expired code
curl -X POST http://localhost:8000/v1/users/activate \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Basic dGVzdDJAZXhhbXBsZS5jb206dGVzdHBhc3MxMjM=' \
  -d '{"code":"XXXX"}'
```

Expected response (400):
```json
{
  "detail": {
    "error": "CODE_EXPIRED", 
    "message": "Activation code expired.",
    "code": "DM_REG_003"
  }
}
```

### API Documentation
Visit http://localhost:8000/docs for interactive API documentation.

### Common Issues During Manual Testing

**Services not responding:**
```bash
# Check if services are running
docker compose ps

# If not healthy, restart
docker compose down && docker compose up -d
```

**Email code not found:**
- Wait a few seconds after registration for background task to complete
- Check mailer logs: `docker compose logs mailer`

**Invalid Basic Auth:**
```bash
# Generate correct Basic Auth header
echo -n 'your-email@example.com:your-password' | base64
```

## API Endpoints

### POST /v1/users
Create a new user account.

Request:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

Response (201):
```json
{
  "id": "uuid-here",
  "email": "user@example.com",
  "created_at": "2024-01-01T12:00:00Z",
  "active": false
}
```

### POST /v1/users/activate
Activate user account with Basic Auth and 4-digit code.

Requires Basic Auth header with email:password.

Request:
```json
{
  "code": "1234"
}
```

Response: 204 No Content (success)

## Development

### Code Quality

Format code:
```bash
docker compose --profile tools run --rm format
```

Run linting:
```bash
docker compose --profile tools run --rm lint
```

### Configuration

Copy the example environment file:
```bash
cp env.example .env
```

All configuration is handled via environment variables. See `env.example` for all available options.

Key environment variables:
- `CODE_TTL_SECONDS`: Code expiration time (60 seconds - comfortable for manual testing)
- `BCRYPT_ROUNDS`: Password hashing rounds (default: 12)  
- `EMAIL_TIMEOUT_SECONDS`: Email service timeout (default: 3)
- `DB_*`: Database connection settings
- `EMAIL_API_BASE_URL`: External email service URL


## Error Codes

| Code | Status | Description |
|------|--------|-------------|
| DM_REG_001 | 409 | Email already registered |
| DM_REG_002 | 401 | Invalid credentials |
| DM_REG_003 | 400 | Activation code expired |
| DM_REG_004 | 400 | Invalid activation code |
| DM_REG_005 | 409 | Account already active |

## Troubleshooting

### Check service status
```bash
docker compose ps
docker compose logs app
```

### Reset everything
```bash
docker compose down -v
docker compose up -d
```