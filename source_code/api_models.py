from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=100,
    )
    email: EmailStr
    password: str = Field(
        min_length=6,
        max_length=200,
    )
    role: str = Field(
        default="user",
    )


class VerifyOTPRequest(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=100,
    )
    email: EmailStr
    password: str = Field(
        min_length=6,
        max_length=200,
    )
    role: str = Field(
        default="user",
    )
    otp: str = Field(
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
    )


class LoginRequest(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=100,
    )
    password: str = Field(
        min_length=6,
        max_length=200,
    )


class SearchRequest(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=1000,
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=50,
    )


class AskRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=2000,
    )
    limit: int = Field(
        default=5,
        ge=1,
        le=20,
    )


class RepositoryFilterRequest(BaseModel):
    search: Optional[str] = Field(
        default=None,
        max_length=500,
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
    abstract: Optional[str] = Field(
        default=None,
        max_length=10000,
    )


class UserResponse(BaseModel):
    id: int
    username: str
    role: str


class AuthResponse(BaseModel):
    message: str
    user: UserResponse
    access_token: str
    token_type: str = "bearer"


class OTPResponse(BaseModel):
    message: str


class PaperResponse(BaseModel):
    id: int
    title: str
    authors: Optional[str] = None
    abstract: Optional[str] = None
    domain: Optional[str] = None
    year: Optional[int] = None
    filename: Optional[str] = None
    file_path: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class SearchResultResponse(BaseModel):
    paper_id: int
    title: Optional[str] = None
    authors: Optional[str] = None
    domain: Optional[str] = None
    year: Optional[int] = None
    filename: Optional[str] = None
    chunk_id: int
    chunk_index: int
    content: str
    similarity: float


class SourceResponse(BaseModel):
    paper_id: Optional[int] = None
    title: Optional[str] = None
    authors: Optional[str] = None
    domain: Optional[str] = None
    year: Optional[int] = None
    chunk_index: Optional[int] = None
    similarity: Optional[float] = None


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceResponse]