import os
import uuid
from decimal import Decimal

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.dependencies import get_current_customer, get_current_admin
from app.models.customer import Customer
from app.models.customer_order import CustomerOrder
from app.models.payment import Payment
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.services.paystack import initialize_transaction, verify_transaction
from app.services.receipt_service import generate_receipt

load_dotenv()

router = APIRouter(
    prefix="/api/payments",
    tags=["Payments"]
)


@router.post("/initialize")
def initialize_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    customer: dict = Depends(get_current_customer)
):
    order = db.query(CustomerOrder).filter(
        CustomerOrder.order_id == payment_data.order_id,
        CustomerOrder.customer_id == customer["user_id"]
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.order_status == "Cancelled":
        raise HTTPException(status_code=400, detail="Cannot pay for a cancelled order")

    if payment_data.payment_method == "Cash":
        raise HTTPException(
            status_code=400,
            detail="Cash payments are recorded by an administrator after cash is received."
        )

    customer_record = db.query(Customer).filter(
        Customer.customer_id == customer["user_id"]
    ).first()

    if not customer_record:
        raise HTTPException(status_code=404, detail="Customer account not found")

    channel_mapping = {
        "Mobile Money": "mobile_money",
        "Card": "card",
        "Bank Transfer": "bank_transfer"
    }
    channel = channel_mapping.get(payment_data.payment_method)

    if not channel:
        raise HTTPException(status_code=400, detail="Unsupported Paystack payment method")

    existing_payment = db.query(Payment).filter(
        Payment.order_id == order.order_id
    ).first()

    if existing_payment and existing_payment.payment_status != "Failed":
        raise HTTPException(
            status_code=409,
            detail="A payment already exists or is being processed"
        )

    payment = existing_payment or Payment(
        order_id=order.order_id,
        payment_method=payment_data.payment_method,
        payment_amount=order.total_amount,
        payment_status="Pending"
    )

    reference = f"BAKERY-{uuid.uuid4().hex}"
    payment.payment_method = payment_data.payment_method
    payment.payment_amount = order.total_amount
    payment.payment_status = "Pending"
    payment.transaction_reference = reference

    try:
        if existing_payment is None:
            db.add(payment)
        db.flush()

        amount_in_pesewas = int(Decimal(str(order.total_amount)) * 100)
        if amount_in_pesewas <= 0:
            raise HTTPException(status_code=400, detail="Invalid order amount")

        frontend_url = os.getenv("FRONTEND_URL")
        if not frontend_url:
            raise RuntimeError("FRONTEND_URL is missing from .env")

        paystack_data = initialize_transaction(
            email=customer_record.email,
            amount=amount_in_pesewas,
            reference=reference,
            currency=os.getenv("PAYSTACK_CURRENCY", "GHS"),
            channels=[channel],
            callback_url=f"{frontend_url.rstrip('/')}/payment/callback"
        )

        db.commit()
        db.refresh(payment)

    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A payment record already exists for this order"
        ) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=502,
            detail="Could not initialize payment. Please try again."
        ) from exc

    return {
        "message": "Payment initialized successfully",
        "payment_id": payment.payment_id,
        "reference": reference,
        "authorization_url": paystack_data["authorization_url"],
        "access_code": paystack_data["access_code"]
    }


@router.post("/verify/{reference}")
def verify_payment(
    reference: str,
    db: Session = Depends(get_db),
    customer: dict = Depends(get_current_customer)
):
    payment = db.query(Payment).join(
        CustomerOrder,
        Payment.order_id == CustomerOrder.order_id
    ).filter(
        Payment.transaction_reference == reference,
        CustomerOrder.customer_id == customer["user_id"]
    ).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    order = db.query(CustomerOrder).filter(
        CustomerOrder.order_id == payment.order_id
    ).first()

    customer_record = db.query(Customer).filter(
        Customer.customer_id == customer["user_id"]
    ).first()

    if not order or not customer_record:
        raise HTTPException(status_code=404, detail="Order or customer account not found")

    if payment.payment_status == "Successful":
        receipt = generate_receipt(db, payment, order)
        db.commit()
        return {
            "message": "Payment already verified",
            "payment_status": "Successful",
            "order_id": order.order_id,
            "receipt_id": receipt.receipt_id
        }

    if payment.payment_status != "Pending":
        raise HTTPException(
            status_code=409,
            detail="This payment is not awaiting verification. Initialize a new payment attempt."
        )

    try:
        paystack_data = verify_transaction(reference)

        expected_amount = int(Decimal(str(order.total_amount)) * 100)

        if paystack_data.get("reference") != reference:
            raise HTTPException(status_code=400, detail="Transaction reference does not match")

        if paystack_data.get("amount") != expected_amount:
            raise HTTPException(status_code=400, detail="Payment amount does not match the order total")

        if paystack_data.get("currency") != os.getenv("PAYSTACK_CURRENCY", "GHS"):
            raise HTTPException(status_code=400, detail="Payment currency does not match")

        paystack_email = paystack_data.get("customer", {}).get("email", "").lower()
        if paystack_email != customer_record.email.lower():
            raise HTTPException(status_code=400, detail="Payment customer email does not match")

        transaction_status = paystack_data.get("status")

        if transaction_status == "success":
            payment.payment_status = "Successful"
            if order.order_status == "Pending":
                order.order_status = "Confirmed"

            receipt = generate_receipt(db, payment, order)
            db.commit()
            db.refresh(receipt)

            return {
                "message": "Payment verified successfully",
                "payment_status": payment.payment_status,
                "order_id": order.order_id,
                "reference": reference,
                "receipt_id": receipt.receipt_id
            }

        if transaction_status in ("failed", "abandoned"):
            payment.payment_status = "Failed"
            db.commit()
            return {
                "message": "Payment was not successful",
                "payment_status": "Failed"
            }

        return {
            "message": "Payment is still being processed",
            "payment_status": payment.payment_status,
            "transaction_status": transaction_status
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=502,
            detail="Could not verify payment. Please try again."
        ) from exc


@router.post("/cash/confirm/{order_id}")
def confirm_cash_payment(
    order_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    order = db.query(CustomerOrder).filter(
        CustomerOrder.order_id == order_id
    ).with_for_update().first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.order_status == "Cancelled":
        raise HTTPException(status_code=400, detail="Cannot record payment for a cancelled order")

    existing_payment = db.query(Payment).filter(
        Payment.order_id == order_id
    ).first()

    if existing_payment:
        raise HTTPException(
            status_code=409,
            detail="A payment record already exists for this order"
        )

    payment = Payment(
        order_id=order_id,
        payment_method="Cash",
        payment_amount=order.total_amount,
        payment_status="Successful"
    )

    try:
        db.add(payment)
        db.flush()
        order.order_status = "Confirmed"
        receipt = generate_receipt(db, payment, order)
        db.commit()
        db.refresh(payment)
        db.refresh(receipt)

        return {
            "message": "Cash payment recorded successfully",
            "payment_id": payment.payment_id,
            "payment_status": payment.payment_status,
            "order_id": order_id,
            "receipt_id": receipt.receipt_id
        }

    except Exception as exc:
        db.rollback()
        if isinstance(exc, HTTPException):
            raise
        raise HTTPException(
            status_code=500,
            detail="Cash payment could not be recorded"
        ) from exc


@router.get("/my-payments", response_model=list[PaymentResponse])
def get_my_payments(
    db: Session = Depends(get_db),
    customer: dict = Depends(get_current_customer)
):
    return db.query(Payment).join(
        CustomerOrder,
        Payment.order_id == CustomerOrder.order_id
    ).filter(
        CustomerOrder.customer_id == customer["user_id"]
    ).order_by(Payment.payment_date.desc()).all()


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    customer: dict = Depends(get_current_customer)
):
    payment = db.query(Payment).join(
        CustomerOrder,
        Payment.order_id == CustomerOrder.order_id
    ).filter(
        Payment.payment_id == payment_id,
        CustomerOrder.customer_id == customer["user_id"]
    ).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    return payment


@router.get("/", response_model=list[PaymentResponse])
def get_all_payments(
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    return db.query(Payment).order_by(Payment.payment_date.desc()).all()
