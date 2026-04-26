from pydantic import BaseModel, EmailStr, Field, ConfigDict

from datetime import datetime

class RegisterPayload(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class RegisterResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True) # mold input to model based off matching fields