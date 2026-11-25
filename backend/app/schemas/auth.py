from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    tenant_id: str
    role: str
    user_name: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    tenant_id: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[int] = None

class LoginRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="Plain password")

class UserCreate(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="Plain password")
    full_name: str = Field(..., description="Full name of user")
    role: str = "researcher"
    tenant_id: Optional[str] = None

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
