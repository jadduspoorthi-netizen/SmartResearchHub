from typing import Optional

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=6, max_length=200)
    role: str = Field(default="user")


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=6, max_length=200)


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    limit: int = Field(default=10, ge=1, le=50)


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    limit: int = Field(default=5, ge=1, le=20)


class PaperUpdateRequest(BaseModel):
    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=500,
    )
    authors: Optional[str] = Field(
        default=None,
        max_length=1000,
    )
    domain: Optional[str] = Field(
        default=None,
        max_length=100,
    )
    year: Optional[int] = Field(
        default=None,
        ge=1800,
        le=2100,
    )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    username: str
    role: str


class AuthResponse(BaseModel):
    message: str
    user: UserResponse
    access_token: str
    token_type: str = "bearer"
