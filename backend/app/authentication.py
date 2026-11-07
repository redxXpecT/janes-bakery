
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from typing import cast

from app.database import get_db
from app.models.customer import Customer
from app.models.administrator import Administrator
from app.services.security import verify_password, create_access_token


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/customer/login")
def customer_login(
    login: LoginRequest,
    db: Session = Depends(get_db)
):
    customer = db.query(Customer).filter(
        Customer.email == login.email
    ).first()

    if not customer or not verify_password(
        login.password,
        cast(str, customer.password_hash)
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )

    token = create_access_token(
        customer.customer_id,
        "CUSTOMER"
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_type": "CUSTOMER",
        "customer_id": customer.customer_id
    }


@router.post("/admin/login")
def admin_login(
    login: LoginRequest,
    db: Session = Depends(get_db)
):
    admin = db.query(Administrator).filter(
        Administrator.email == login.email
    ).first()

    if not admin or not verify_password(
        login.password,
        cast(str, admin.password_hash)
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )

    token = create_access_token(
        admin.admin_id,
        "ADMIN"
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_type": "ADMIN",
        "admin_id": admin.admin_id
    }
