from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.customer import Customer
from app.models.administrator import Administrator
from app.services.security import verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_type: str
    user_id: int


@router.post("/customer/login", response_model=LoginResponse)
def customer_login(data: LoginRequest, db: Session = Depends(get_db)):

    customer = db.query(Customer).filter(
        Customer.email == data.email
    ).first()

    if not customer:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(data.password, customer.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token(
        user_id=customer.customer_id,
        role="CUSTOMER"
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_type": "CUSTOMER",
        "user_id": customer.customer_id
    }



@router.post("/admin/login", response_model=LoginResponse)
def admin_login(data: LoginRequest, db: Session = Depends(get_db)):

    admin = db.query(Administrator).filter(
        Administrator.email == data.email
    ).first()

    if not admin:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(data.password, admin.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token(
        user_id=admin.admin_id,
        role="ADMIN"
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_type": "ADMIN",
        "user_id": admin.admin_id
    }