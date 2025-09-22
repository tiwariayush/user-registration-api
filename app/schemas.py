from pydantic import BaseModel, EmailStr, Field

class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=8, 
        max_length=128,
        description="Password must be at least 8 characters"
    )

class CreateUserResponse(BaseModel):
    id: str
    email: EmailStr
    created_at: str
    active: bool

class ActivateRequest(BaseModel):
    code: str = Field(pattern=r"^\d{4}$", description="4-digit activation code")
