
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import db, schemas, models, security, fraud
from .security import get_current_user
from .metrics import metrics_summary

app = FastAPI(title="Payments & Fraud API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    db.Base.metadata.create_all(bind=db.engine)

# ---- Auth ----
@app.post("/auth/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, session: Session = Depends(db.get_session)):
    if session.query(models.User).filter_by(email=user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    new = models.User(email=user.email)
    new.set_password(user.password)
    session.add(new)
    session.commit()
    session.refresh(new)
    return new

@app.post("/auth/login", response_model=schemas.TokenOut)
def login(creds: schemas.UserLogin, session: Session = Depends(db.get_session)):
    user = session.query(models.User).filter_by(email=creds.email).first()
    if not user or not user.verify_password(creds.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = security.create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

# ---- Orders ----
@app.post("/orders", response_model=schemas.OrderOut)
def create_order(order: schemas.OrderCreate, session: Session = Depends(db.get_session), user=Depends(get_current_user)):
    o = models.Order.from_schema(order, user_id=user.id)
    session.add(o)
    session.commit()
    session.refresh(o)
    return o

@app.get("/orders/{order_id}", response_model=schemas.OrderOut)
def get_order(order_id: int, session: Session = Depends(db.get_session), user=Depends(get_current_user)):
    o = session.get(models.Order, order_id)
    if not o or o.user_id != user.id:
        raise HTTPException(status_code=404, detail="Order not found")
    return o

# ---- Payments ----
@app.post("/payments", response_model=schemas.PaymentOut)
def create_payment(payment: schemas.PaymentCreate, session: Session = Depends(db.get_session), user=Depends(get_current_user)):
    o = session.get(models.Order, payment.order_id)
    if not o or o.user_id != user.id:
        raise HTTPException(status_code=404, detail="Order not found")
    p = models.Payment.from_schema(payment)
    session.add(p)
    session.commit()
    session.refresh(p)
    return p

# ---- Fraud ----
@app.post("/fraud/score", response_model=schemas.FraudScoreOut)
def score(req: schemas.FraudScoreIn, session: Session = Depends(db.get_session), user=Depends(get_current_user)):
    score, reasons = fraud.score_transaction(session, req)
    return {"score": score, "reasons": reasons, "decision": "reject" if score >= 0.75 else ("review" if score >= 0.5 else "approve")}

# ---- Metrics ----
@app.get("/metrics/summary", response_model=schemas.MetricsOut)
def metrics(session: Session = Depends(db.get_session), user=Depends(get_current_user)):
    return metrics_summary(session, user_id=user.id)
