
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_customer, get_current_admin

from app.models.custom_order import CustomOrder
from app.models.product import Product

from app.schemas.custom_order import (
    CustomOrderRequest,
    CustomOrderResponse
)

router = APIRouter(
    prefix="/api/custom-orders",
    tags=["Custom Orders"]
)


def format_custom_order(custom_order, product):
    return {
        "custom_order_id": custom_order.custom_order_id,
        "customer_id": custom_order.customer_id,
        "order_id": custom_order.order_id,
        "product_id": custom_order.product_id,
        "quantity": custom_order.quantity,
        "customization_details": custom_order.customization_details,
        "special_request": custom_order.special_request,
        "required_date": custom_order.required_date,
        "selling_price": product.selling_price
    }


@router.post("/", response_model=CustomOrderResponse, status_code=201)
def create_custom_order(
    order_data: CustomOrderRequest,
    db: Session = Depends(get_db),
    customer: dict = Depends(get_current_customer)
):
    product = db.query(Product).filter(
        Product.product_id == order_data.product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Selected product not found"
        )

    if order_data.required_date < date.today():
        raise HTTPException(
            status_code=400,
            detail="Required date cannot be in the past"
        )

    new_custom_order = CustomOrder(
        customer_id=customer["user_id"],
        product_id=order_data.product_id,
        quantity=order_data.quantity,
        customization_details=order_data.customization_details,
        special_request=order_data.special_request,
        required_date=order_data.required_date
    )

    db.add(new_custom_order)
    db.commit()
    db.refresh(new_custom_order)

    return format_custom_order(new_custom_order, product)


@router.get("/my-orders", response_model=list[CustomOrderResponse])
def get_my_custom_orders(
    db: Session = Depends(get_db),
    customer: dict = Depends(get_current_customer)
):
    results = db.query(CustomOrder, Product).join(
        Product,
        CustomOrder.product_id == Product.product_id
    ).filter(
        CustomOrder.customer_id == customer["user_id"]
    ).order_by(
        CustomOrder.custom_order_id.desc()
    ).all()

    return [
        format_custom_order(custom_order, product)
        for custom_order, product in results
    ]


@router.get("/", response_model=list[CustomOrderResponse])
def get_all_custom_orders(
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    results = db.query(CustomOrder, Product).join(
        Product,
        CustomOrder.product_id == Product.product_id
    ).order_by(
        CustomOrder.custom_order_id.desc()
    ).all()

    return [
        format_custom_order(custom_order, product)
        for custom_order, product in results
    ]
