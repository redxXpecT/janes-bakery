from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_customer
from app.models.shopping_cart import ShoppingCart
from app.models.cart_item import CartItem
from app.models.product import Product
from app.schemas.cart_item import (
    AddCartItemRequest,
    UpdateCartItemRequest
)

router = APIRouter(
    prefix="/api/cart",
    tags=["Shopping Cart"]
)


def get_customer_cart(db: Session, customer_id: int):
    return db.query(ShoppingCart).filter(
        ShoppingCart.customer_id == customer_id,
        ShoppingCart.cart_status == "Active"
    ).first()


@router.get("/")
def view_cart(
    db: Session = Depends(get_db),
    customer: dict = Depends(get_current_customer)
):
    cart = get_customer_cart(db, customer["user_id"])

    if not cart:
        return {
            "cart_id": None,
            "items": [],
            "total": Decimal("0.00")
        }

    cart_items = db.query(CartItem, Product).join(
        Product,
        CartItem.product_id == Product.product_id
    ).filter(
        CartItem.cart_id == cart.cart_id
    ).all()

    items = []
    total = Decimal("0.00")

    for cart_item, product in cart_items:
        subtotal = product.selling_price * cart_item.quantity
        total += subtotal

        items.append({
            "cart_item_id": cart_item.cart_item_id,
            "product_id": product.product_id,
            "product_name": product.product_name,
            "unit_price": product.selling_price,
            "quantity": cart_item.quantity,
            "subtotal": subtotal
        })

    return {
        "cart_id": cart.cart_id,
        "items": items,
        "total": total
    }


@router.post("/items", status_code=201)
def add_to_cart(
    item_data: AddCartItemRequest,
    db: Session = Depends(get_db),
    customer: dict = Depends(get_current_customer)
):
    product = db.query(Product).filter(
        Product.product_id == item_data.product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    if item_data.quantity > product.stock_quantity:
        raise HTTPException(
            status_code=400,
            detail="Requested quantity exceeds available stock"
        )

    cart = get_customer_cart(db, customer["user_id"])

    if not cart:
        cart = ShoppingCart(
            customer_id=customer["user_id"],
            cart_status="Active"
        )
        db.add(cart)
        db.flush()

    cart_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.cart_id,
        CartItem.product_id == product.product_id
    ).first()

    if cart_item:
        new_quantity = cart_item.quantity + item_data.quantity

        if new_quantity > product.stock_quantity:
            raise HTTPException(
                status_code=400,
                detail="Requested quantity exceeds available stock"
            )

        cart_item.quantity = new_quantity

    else:
        cart_item = CartItem(
            cart_id=cart.cart_id,
            product_id=product.product_id,
            quantity=item_data.quantity
        )
        db.add(cart_item)

    db.commit()

    return {
        "message": "Product added to cart successfully"
    }


@router.patch("/items/{cart_item_id}")
def update_cart_item(
    cart_item_id: int,
    item_data: UpdateCartItemRequest,
    db: Session = Depends(get_db),
    customer: dict = Depends(get_current_customer)
):
    cart = get_customer_cart(db, customer["user_id"])

    if not cart:
        raise HTTPException(
            status_code=404,
            detail="Shopping cart not found"
        )

    cart_item = db.query(CartItem).filter(
        CartItem.cart_item_id == cart_item_id,
        CartItem.cart_id == cart.cart_id
    ).first()

    if not cart_item:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found"
        )

    product = db.query(Product).filter(
        Product.product_id == cart_item.product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    if item_data.quantity > product.stock_quantity:
        raise HTTPException(
            status_code=400,
            detail="Requested quantity exceeds available stock"
        )

    cart_item.quantity = item_data.quantity

    db.commit()

    return {
        "message": "Cart quantity updated successfully"
    }



@router.delete("/items/{cart_item_id}")
def remove_cart_item(
    cart_item_id: int,
    db: Session = Depends(get_db),
    customer: dict = Depends(get_current_customer)
):
    cart = get_customer_cart(db, customer["user_id"])

    if not cart:
        raise HTTPException(
            status_code=404,
            detail="Shopping cart not found"
        )

    cart_item = db.query(CartItem).filter(
        CartItem.cart_item_id == cart_item_id,
        CartItem.cart_id == cart.cart_id
    ).first()

    if not cart_item:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found"
        )

    db.delete(cart_item)
    db.commit()

    return {
        "message": "Product removed from cart successfully"
    }