
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from .models import Order, Payment

def metrics_summary(session: Session, user_id: int):
    total_orders = session.scalar(select(func.count(Order.id)).where(Order.user_id==user_id)) or 0
    total_payments = session.scalar(select(func.count(Payment.id))) or 0
    total_revenue = session.scalar(select(func.coalesce(func.sum(Payment.amount), 0.0))) or 0.0
    # Simulado: 5% sospechoso si ticket > 300
    suspicious = session.scalar(select(func.count(Order.id)).where(Order.user_id==user_id, Order.total_amount>=300)) or 0
    suspected_rate = (suspicious/total_orders) if total_orders else 0.0
    return {
        "total_orders": total_orders,
        "total_payments": total_payments,
        "total_revenue": float(total_revenue),
        "suspected_fraud_rate": round(suspected_rate, 3),
    }
