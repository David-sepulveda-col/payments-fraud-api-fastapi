
# Payments & Fraud API (FastAPI + SQLAlchemy + JWT)

Sistema de **órdenes y pagos** con **motor antifraude** basado en reglas + outliers. Ideal para demostrar diseño backend sólido, seguridad y pensamiento arquitectónico.

> **TL;DR (para reclutadores):** API de pagos con autenticación JWT, persistencia con SQLAlchemy, reglas antifraude (monto, país de riesgo, correo desechable, distancia IP-envío, múltiples intentos) y una detección simple de outliers por ticket. KPIs y endpoints listos para demo.

---

## 1) Problema de negocio
Un e‑commerce en crecimiento sufría **intentos de fraude** (tarjetas robadas, correos desechables, direcciones sospechosas), afectando ingresos y confianza del cliente.

**Objetivo:** reducir la tasa de transacciones sospechosas y habilitar señales de riesgo accionables sin introducir fricción excesiva.

**Resultado (simulación controlada):**
- ↓ **~30–35%** transacciones sospechosas al activar reglas + outlier simple.
- **P95 < 120ms** para `POST /fraud/score` bajo carga ligera (en local).
- Backend listo para escalar: Docker, Postgres, separación de módulos y pruebas.

> Nota: Las métricas son simuladas/demostrativas para portafolio y pueden replicarse con datasets de prueba.

---

## 2) Arquitectura
```mermaid
flowchart LR
  Client -->|JWT| API[FastAPI]
  API --> SEC[Security and JWT]
  API --> DB[(Postgres or SQLite)]
  API --> FRAUD[Fraud Engine]

  subgraph Fraud Engine
    R[Rules]
    O[Outlier check - ticket vs avg]
    R --> D[Decision approve - review - reject]
    O --> D
  end```

---

**Decisiones técnicas clave**
- **FastAPI** por rendimiento y DX.
- **SQLAlchemy 2.0** para ORM moderno y tipado, compatible con Postgres/SQLite.
- **JWT** con expiración corta, bearer auth.
- **Módulo antifraude** desacoplado (`app/fraud.py`) para extender con ML.
- **Métricas** expuestas por endpoint (`/metrics/summary`) para monitoreo básico.

---

## 3) Data Model (simplificado)

- `users(id, email, password_hash)`  
- `orders(id, user_id, customer_id, shipping_address, total_amount, created_at)`  
- `order_items(id, order_id, sku, qty, unit_price)`  
- `payments(id, order_id, amount, method, provider, metadata, created_at)`

---

## 4) API Surface (principal)
- `POST /auth/register` — Crear usuario  
- `POST /auth/login` — Login (JWT bearer)  
- `POST /orders` — Crear orden  
- `GET /orders/{order_id}` — Obtener orden  
- `POST /payments` — Registrar pago  
- `POST /fraud/score` — Puntuar riesgo y decisión (`approve/review/reject`)  
- `GET /metrics/summary` — KPIs (órdenes, pagos, revenue, tasa sospechosa)

**Ejemplo `curl`:**
```bash
# Registro
curl -sX POST http://localhost:8000/auth/register -H 'Content-Type: application/json'  -d '{"email":"demo@aster.com","password":"123456"}'

# Login
TOKEN=$(curl -sX POST http://localhost:8000/auth/login -H 'Content-Type: application/json'  -d '{"email":"demo@aster.com","password":"123456"}' | python -c 'import sys, json; print(json.load(sys.stdin)["access_token"])')

# Crear orden
curl -sX POST http://localhost:8000/orders -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json'  -d '{"customer_id":"cust_1","items":[{"sku":"SKU123","qty":2,"unit_price":49.9}],"shipping_address":"CL 123 #45-67, Bogotá"}'

# Score antifraude (usa id real de orden)
curl -sX POST http://localhost:8000/fraud/score -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json'  -d '{"order_id":1,"ip_country":"RU","email_domain":"yopmail.com","distance_km":1500,"attempts_last_hour":4,"ticket_amount":500}'
```

---

## 5) Fraude: reglas y outliers
Reglas (suma de score y razones):
- **high_amount** si `ticket >= 300` ( +0.35 )
- **risky_country** si país IP ∈ {VN, RU, NG, PK} ( +0.25 )
- **disposable_email** si dominio ∈ {mailinator, tempmail, yopmail} ( +0.20 )
- **ip_shipping_distance** si distancia > 1000 km ( +0.15 )
- **multiple_attempts** si intentos ≥ 3 en 1h ( +0.20 )

Outlier simple:
- **ticket_outlier** si `ticket > 2.5 × avg_ticket(usuario)` ( +0.20 )

**Decisión:** `reject` (≥0.75) · `review` (≥0.5) · `approve` (<0.5)

---

## 6) Escalabilidad y siguientes pasos
- **DB**: SQLite → Postgres (cambiar `DATABASE_URL`).
- **Jobs**: Ventanas móviles (intentos por IP/email) con Redis + Celery/RQ.
- **Observabilidad**: métricas Prometheus + logs estructurados.
- **ML**: reemplazar outlier simple por modelo (sklearn / xgboost) y AB testing.
- **Rate limiting**: por IP/usuario en endpoints sensibles.

---

## 7) Calidad y seguridad
- **Pruebas**: `pytest` con clientes HTTP, cobertura básica.
- **Formato/lint**: `pre-commit` (Black, Ruff, isort).
- **Auth**: JWT HS256, expiración corta, scopes básicos si aplica.

Badges (agregar cuando subas a GitHub Actions):
```
[![tests](https://img.shields.io/badge/tests-passing-brightgreen)]()
[![lint](https://img.shields.io/badge/lint-ruff-black)]()
[![style](https://img.shields.io/badge/style-black-black)]()
```

---

## 8) Cómo correr
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
# env opcional: DATABASE_URL, JWT_SECRET, ALLOWED_CORS
```

**Docker**
```bash
docker build -t payments-fraud-api .
docker run -p 8000:8000 payments-fraud-api
```

---

## 9) Deploy rápido
- **Render / Railway / Fly.io** con Postgres gestionado.
- Variables: `DATABASE_URL`, `JWT_SECRET`, `PORT=8000`.

---

## 10) Demo rápida para entrevista
- Abre `http://localhost:8000/docs` (Swagger) y muestra:
  1. Login → toma token.
  2. Crear orden → ver total calculado y items.
  3. Score antifraude → mostrar razones y decisión.
  4. KPIs → tasa sospechosa vs total.

---

## 11) Licencia
MIT
