from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_customer, get_current_admin
from app.models.receipt import Receipt
from app.models.customer_order import CustomerOrder
from app.schemas.receipt import ReceiptResponse

router = APIRouter(
    prefix="/api/receipts",
    tags=["Receipts"]
)


@router.get("/my-receipts", response_model=list[ReceiptResponse])
def get_my_receipts(
    db: Session = Depends(get_db),
    customer: dict = Depends(get_current_customer)
):
    receipts = db.query(Receipt).join(
        CustomerOrder,
        Receipt.order_id == CustomerOrder.order_id
    ).filter(
        CustomerOrder.customer_id == customer["user_id"]
    ).order_by(
        Receipt.receipt_date.desc()
    ).all()

    return receipts


@router.get("/{receipt_id}", response_model=ReceiptResponse)
def get_receipt(
    receipt_id: int,
    db: Session = Depends(get_db),
    customer: dict = Depends(get_current_customer)
):
    receipt = db.query(Receipt).join(
        CustomerOrder,
        Receipt.order_id == CustomerOrder.order_id
    ).filter(
        Receipt.receipt_id == receipt_id,
        CustomerOrder.customer_id == customer["user_id"]
    ).first()

    if not receipt:
        raise HTTPException(
            status_code=404,
            detail="Receipt not found"
        )

    return receipt


@router.get("/", response_model=list[ReceiptResponse])
def get_all_receipts(
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    return db.query(Receipt).order_by(
        Receipt.receipt_date.desc()
    ).all()