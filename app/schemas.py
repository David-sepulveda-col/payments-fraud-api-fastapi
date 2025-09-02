
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

# ---- Auth ----
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    class Config:
        from_attributes = True

class TokenOut(BaseModel):
    access_token: str
    token_type: str

# ---- Orders / Payments ----
class OrderItemIn(BaseModel):
    sku: str
    qty: int
    unit_price: float

class OrderCreate(BaseModel):
    customer_id: str
    items: List[OrderItemIn]
    shipping_address: str

class OrderItemOut(OrderItemIn):
    id: int

    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: int
    customer_id: str
    shipping_address: str
    total_amount: float
    items: List[OrderItemOut]

    class Config:
        from_attributes = True

class PaymentCreate(BaseModel):
    order_id: int
    amount: float
    method: str
    provider: str
    metadata: Optional[dict] = None

class PaymentOut(PaymentCreate):
    id: int
    class Config:
        from_attributes = True

# ---- Fraud ----
class FraudScoreIn(BaseModel):
    order_id: int
    ip_country: str | None = None
    email_domain: str | None = None
    distance_km: float | None = None  # distancia IP vs envío
    attempts_last_hour: int | None = None
    ticket_amount: float | None = None

class FraudScoreOut(BaseModel):
    score: float
    reasons: list[str]
    decision: str

# ---- Metrics ----
class MetricsOut(BaseModel):
    total_orders: int
    total_payments: int
    total_revenue: float
    suspected_fraud_rate: float
