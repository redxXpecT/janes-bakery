
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import engine

from app.routers import (
    authentication,
    customers,
    products,
    cart,
    orders,
    payments,
    receipts,
    custom_orders,
    deliveries,
    reports
)

app = FastAPI(
    title="Bakery E-commerce API",
    description="Backend API for the Bakery E-commerce Application",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(authentication.router)
app.include_router(customers.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(payments.router)
app.include_router(receipts.router)
app.include_router(custom_orders.router)
app.include_router(deliveries.router)
app.include_router(reports.router)


@app.get("/")
def home():
    return {
        "message": "Bakery E-commerce API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.get("/health/database")
def database_health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "database": "connected"
        }

    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed"
        ) from exc
