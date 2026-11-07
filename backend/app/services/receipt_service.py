from sqlalchemy.orm import Session

from app.models.receipt import Receipt


def generate_receipt(db: Session, payment, order):
    if payment.payment_status != "Successful":
        raise ValueError("A receipt can only be generated for a successful payment")

    receipt = db.query(Receipt).filter(
        Receipt.order_id == order.order_id
    ).first()

    if receipt:
        return receipt

    receipt = Receipt(
        order_id=order.order_id,
        total_amount=order.total_amount
    )

    db.add(receipt)
    db.flush()

    return receipt