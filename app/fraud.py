
from sqlalchemy.orm import Session
from . import models, schemas

RISK_COUNTRIES = {"VN", "RU", "NG", "PK"}
DISPOSABLE_DOMAINS = {"mailinator.com", "tempmail.com", "yopmail.com"}

def score_transaction(session: Session, req: schemas.FraudScoreIn) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []

    # Datos base
    order = session.get(models.Order, req.order_id)
    if not order:
        return 1.0, ["order_not_found"]

    amount = req.ticket_amount or order.total_amount

    # Reglas
    if amount >= 300:
        score += 0.35; reasons.append("high_amount")
    if req.ip_country and req.ip_country in RISK_COUNTRIES:
        score += 0.25; reasons.append("risky_country")
    if req.email_domain and req.email_domain.lower() in DISPOSABLE_DOMAINS:
        score += 0.20; reasons.append("disposable_email")
    if req.distance_km and req.distance_km > 1000:
        score += 0.15; reasons.append("ip_shipping_distance")
    if req.attempts_last_hour and req.attempts_last_hour >= 3:
        score += 0.20; reasons.append("multiple_attempts")

    # Simple "anomaly": ticket vs promedio
    # (Aquí puedes reemplazar por un modelo ML real)
    # Nota: esto es deliberadamente sencillo para el portafolio.
    avg_ticket = _avg_ticket(session, order.user_id)
    if avg_ticket and amount > avg_ticket * 2.5:
        score += 0.2; reasons.append("ticket_outlier")

    # Clampear score
    score = min(1.0, score)
    return score, reasons

def _avg_ticket(session: Session, user_id: int) -> float | None:
    from sqlalchemy import func, select
    from .models import Order
    stmt = select(func.avg(Order.total_amount)).where(Order.user_id == user_id)
    res = session.execute(stmt).scalar()
    return float(res) if res is not None else None
