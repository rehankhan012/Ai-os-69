from pydantic import BaseModel, EmailStr

from app.schemas.common import UuidStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    id: UuidStr
    email: str
    username: str
    full_name: str | None = None
    avatar_url: str | None = None
    is_active: bool
    is_verified: bool

    model_config = {"from_attributes": True}


class OAuthCallback(BaseModel):
    provider: str
    code: str
    redirect_uri: str