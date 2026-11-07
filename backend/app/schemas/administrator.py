
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class AdministratorCreate(BaseModel):
    full_name: str = Field(min_length=1)
    email: EmailStr
    phone_number: str = Field(min_length=1)
    password: str = Field(min_length=1)
    role: str = Field(min_length=1)


class AdministratorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    admin_id: int
    full_name: str
    email: EmailStr
    phone_number: str
    role: str
