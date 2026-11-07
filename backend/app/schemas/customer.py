
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field



class CustomerCreate(BaseModel):
    full_name: str = Field(min_length=1)
    email: EmailStr
    phone_number: str = Field(min_length=1)
    password: str = Field(min_length=1)
    address: str = Field(min_length=1)



class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    customer_id: int
    full_name: str
    email: EmailStr
    phone_number: str
    address: str
    date_registered: datetime
