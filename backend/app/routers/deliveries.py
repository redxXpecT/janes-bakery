from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.dependencies import get_current_customer, get_current_admin
from app.models.delivery import Delivery
from app.models.customer_order import CustomerOrder
from app.models.payment import Payment
from app.schemas.delivery import (
    DeliveryCreate,
    DeliveryStatusUpdate,
    DeliveryResponse
)

router = APIRouter(
    prefix="/api/deliveries",
    tags=["Deliveries"]
)


@router.post("/", response_model=DeliveryResponse, status_code=201)
def create_delivery(
    delivery_data: DeliveryCreate,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    order = db.query(CustomerOrder).filter(
        CustomerOrder.order_id == delivery_data.order_id
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.order_status == "Cancelled":
        raise HTTPException(
            status_code=400,
            detail="Cannot arrange fulfilment for a cancelled order"
        )

    payment = db.query(Payment).filter(
        Payment.order_id == order.order_id
    ).first()

    if not payment or payment.payment_status != "Successful":
        raise HTTPException(
            status_code=400,
            detail="Only successfully paid orders can be arranged for fulfilment"
        )

    if order.delivery_method != delivery_data.fulfilment_method:
        raise HTTPException(
            status_code=400,
            detail="Fulfilment method does not match the order"
        )

    address = None
    if delivery_data.fulfilment_method == "Delivery":
        if not order.delivery_address:
            raise HTTPException(
                status_code=400,
                detail="The order has no delivery address"
            )
        address = order.delivery_address

    existing_delivery = db.query(Delivery).filter(
        Delivery.order_id == order.order_id
    ).first()

    if existing_delivery:
        raise HTTPException(
            status_code=409,
            detail="A fulfilment record already exists for this order"
        )

    delivery = Delivery(
        order_id=order.order_id,
        fulfilment_method=delivery_data.fulfilment_method,
        delivery_address=address,
        delivery_date=delivery_data.delivery_date,
        delivery_status="Pending"
    )

    try:
        db.add(delivery)
        db.commit()
        db.refresh(delivery)
        return delivery
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A fulfilment record already exists for this order"
        ) from exc


@router.get("/", response_model=list[DeliveryResponse])
def get_all_deliveries(
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    return db.query(Delivery).order_by(
        Delivery.delivery_id.desc()
    ).all()


@router.get("/my-deliveries", response_model=list[DeliveryResponse])
def get_my_deliveries(
    db: Session = Depends(get_db),
    customer: dict = Depends(get_current_customer)
):
    return db.query(Delivery).join(
        CustomerOrder,
        Delivery.order_id == CustomerOrder.order_id
    ).filter(
        CustomerOrder.customer_id == customer["user_id"]
    ).order_by(Delivery.delivery_id.desc()).all()


@router.patch("/{delivery_id}/status", response_model=DeliveryResponse)
def update_delivery_status(
    delivery_id: int,
    status_data: DeliveryStatusUpdate,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    try:
        delivery = db.query(Delivery).filter(
            Delivery.delivery_id == delivery_id
        ).with_for_update().first()

        if not delivery:
            raise HTTPException(status_code=404, detail="Fulfilment record not found")

        order = db.query(CustomerOrder).filter(
            CustomerOrder.order_id == delivery.order_id
        ).with_for_update().first()

        if not order:
            raise HTTPException(status_code=404, detail="Related order not found")

        if order.order_status == "Cancelled":
            raise HTTPException(
                status_code=409,
                detail="Cannot update fulfilment for a cancelled order"
            )

        delivery.delivery_status = status_data.delivery_status

        if status_data.delivery_status == "Delivered":
            order.order_status = "Completed"
        elif (
            status_data.delivery_status == "Dispatched"
            and delivery.fulfilment_method == "Delivery"
        ):
            order.order_status = "Out for Delivery"

        db.commit()
        db.refresh(delivery)
        return delivery

    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Fulfilment status could not be updated"
        ) from exc
