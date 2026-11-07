
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.dependencies import get_current_customer
from app.database import get_db
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerResponse
from app.services.security import hash_password


router = APIRouter(
    prefix="/api/customers",
    tags=["Customers"]
)


@router.post("/register", response_model=CustomerResponse, status_code=201)
def register_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db)
):
    existing_customer = db.query(Customer).filter(
        Customer.email == customer.email
    ).first()

    if existing_customer:
        raise HTTPException(
            status_code=409,
            detail="Email is already registered"
        )

    new_customer = Customer(
        full_name=customer.full_name,
        email=customer.email,
        phone_number=customer.phone_number,
        password_hash=hash_password(customer.password),
        address=customer.address
    )

    try:
        db.add(new_customer)
        db.commit()
        db.refresh(new_customer)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Customer could not be created because of conflicting data"
        )

    return new_customer


@router.get("/me", response_model=CustomerResponse)
def get_my_profile(
    db: Session = Depends(get_db),
    customer=Depends(get_current_customer)
):
    account = db.query(Customer).filter(
        Customer.customer_id == customer["user_id"]
    ).first()

    if not account:
        raise HTTPException(404, "Customer not found")

    return account
