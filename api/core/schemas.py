from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID


class UserOAuth(BaseModel):
    id: UUID
    email: str
    is_active: bool = True
    roles: Optional[List[str]]


class LoginSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=6)


class RegisterUserAdminSchema(BaseModel):
    firstname: str = Field(...)
    lastname: str = Field(...)
    middlename: Optional[str] = Field(None)
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=6)


class ResetPasswordSchema(BaseModel):
    reset_password_token: str = Field(...)
    new_password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=6)


class ChangePasswordSchema(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str


class CreateWorkspace(BaseModel):
    title: str
    description: Optional[str]


class UploadChunkFile(BaseModel):
    archive_id: Optional[UUID] = None
    name: str
    size: str
    currentChunkIndex: str
    totalChunks: str
