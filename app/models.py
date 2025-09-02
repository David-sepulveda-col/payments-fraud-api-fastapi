
from sqlalchemy import Integer, String, Float, ForeignKey, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from passlib.hash import bcrypt
from .db import Base
from . import schemas

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String)

    def set_password(self, raw: str):
        self.password_hash = bcrypt.hash(raw)

    def verify_password(self, raw: str) -> bool:
        return bcrypt.verify(raw, self.password_hash)

class OrderItem(Base):
    __tablename__ = "order_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    sku: Mapped[str] = mapped_column(String, index=True)
    qty: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[float] = mapped_column(Float)

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    customer_id: Mapped[str] = mapped_column(String, index=True)
    shipping_address: Mapped[str] = mapped_column(String)
    total_amount: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    items: Mapped[list[OrderItem]] = relationship("OrderItem", cascade="all, delete-orphan")

    @staticmethod
    def from_schema(s: schemas.OrderCreate, user_id: int) -> "Order":
        o = Order(user_id=user_id, customer_id=s.customer_id, shipping_address=s.shipping_address, total_amount=sum(i.qty*i.unit_price for i in s.items))
        o.items = [OrderItem(sku=i.sku, qty=i.qty, unit_price=i.unit_price) for i in s.items]
        return o

class Payment(Base):
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    amount: Mapped[float] = mapped_column(Float)
    method: Mapped[str] = mapped_column(String)  # card, pse, cash
    provider: Mapped[str] = mapped_column(String)  # e.g. stripe-like
    metadata: Mapped[dict] = mapped_column(JSON, default={})
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    @staticmethod
    def from_schema(s: schemas.PaymentCreate) -> "Payment":
        return Payment(order_id=s.order_id, amount=s.amount, method=s.method, provider=s.provider, metadata=s.metadata or {})
