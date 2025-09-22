# App Architecture

## Overview

Standard layered architecture with FastAPI. Controllers handle HTTP, services contain business logic, repositories manage data access.

```
HTTP → Controllers → Services → Repositories → Database
```

## Component Relationships

```mermaid
graph TD
    HTTP[main.py] --> UC[UserController]
    HTTP --> HC[HealthController]
    
    UC --> US[UserService]
    UC --> AS[AuthService]
    UC --> BG[BackgroundTasks]
    
    US --> AS
    US --> ACS[ActivationService]
    US --> UR[UserRepository]
    
    AS --> DB[database.py]
    ACS --> DB
    UR --> DB
    
    BG --> EC[email_client.py]
    
    subgraph "Infrastructure"
        DB
        EC
        CFG[config.py]
    end
    
    subgraph "Middleware"
        RL[Rate Limiting]
        SM[Security Headers]
    end
    
    HTTP --> RL
    HTTP --> SM
```

## Components

### Controllers
- `UserController` - registration and activation endpoints
- `HealthController` - health check

### Services  
- `AuthService` - password hashing, user authentication
- `UserService` - registration workflow
- `ActivationService` - code generation and verification

### Repository
- `UserRepository` - user data operations

### Infrastructure
- `database.py` - connection pooling
- `config.py` - environment settings
- `email_client.py` - HTTP client for mailer service
