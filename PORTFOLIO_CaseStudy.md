
# Case Study: Payments & Fraud API

## Short version (survey-ready)
Construí un backend de pagos con detección de fraude para un e‑commerce en crecimiento. El sistema expone APIs de órdenes/pagos y un motor de reglas + outlier (país IP, dominios desechables, monto atípico, etc.). En pruebas simuladas redujo ~30–35% de transacciones sospechosas y mantuvo P95 <120ms en scoring. La arquitectura queda lista para Postgres, Docker y futura integración de ML.

## Interview version (long)
- **Contexto de negocio**: Pérdida por intentos de fraude (tarjetas robadas y cuentas nuevas con correos desechables). Necesidad de balance entre fricción y seguridad.
- **Arquitectura**: FastAPI + SQLAlchemy 2.0 (Postgres/SQLite), JWT, módulos separados para seguridad, fraude y métricas. Preparado para escalar con contenedores.
- **Detección**: Reglas (+0.35 monto alto, +0.25 país de riesgo, +0.20 email desechable, +0.15 distancia IP-envío, +0.20 múltiples intentos) + outlier por ticket vs promedio de usuario. Decisiones `approve/review/reject`.
- **Resultados**: Reducción simulada de ~30–35% en intentos sospechosos. Tiempos de respuesta sub-120ms P95 para scoring local.
- **Trade-offs**: Reglas son explicables pero rígidas; siguiente paso es features de comportamiento y un modelo de riesgo (sklearn/xgboost), con monitoreo y AB tests.
- **Mantenibilidad**: Pre-commit, pruebas, separación de capas, configuraciones via env, Dockerfile.
