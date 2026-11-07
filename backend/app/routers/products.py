
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_admin

from app.models.product import Product

from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse
)

router = APIRouter(
    prefix="/api/products",
    tags=["Products"]
)


@router.get("/", response_model=list[ProductResponse])
def get_products(
    db: Session = Depends(get_db)
):
    return db.query(Product).order_by(
        Product.product_id.desc()
    ).all()


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.product_id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product


@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    product = Product(
        admin_id=admin["user_id"],
        product_name=product_data.product_name,
        description=product_data.description,
        cost_price=product_data.cost_price,
        selling_price=product_data.selling_price,
        stock_quantity=product_data.stock_quantity,
        image_url=product_data.image_url
    )

    try:
        db.add(product)
        db.commit()
        db.refresh(product)

    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Product could not be created because of a database conflict"
        ) from exc

    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="An error occurred while creating the product"
        ) from exc

    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    product = db.query(Product).filter(
        Product.product_id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    update_data = product_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No product information provided"
        )

    for field, value in update_data.items():
        setattr(product, field, value)

    try:
        db.commit()
        db.refresh(product)

    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="An error occurred while updating the product"
        ) from exc

    return product


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    product = db.query(Product).filter(
        Product.product_id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    db.delete(product)

    try:
        db.commit()

    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Product cannot be deleted while it is referenced by other records"
        ) from exc

    return {
        "message": "Product deleted successfully"
    }
