# System Health & Telemetry

## 1. Observability Architecture
ProductIQ AI incorporates local telemetry tracking the status, latency, and throughput of all platform subsystems:

1. **FastAPI Application Server**: Health endpoints (`/health`, `/api/v1/health/system`) exposing platform runtime, Python environment, and endpoint availability.
2. **Relational Database Engine**: SQLite / PostgreSQL table counters, active products, stored sources, and processing job statuses.
3. **Local Ollama Runtime**: Health status of local LLM inference daemon, active model tags, and latency monitoring.

---

## 2. Telemetry Endpoints

- `GET /api/v1/health/system`: Returns consolidated system telemetry, active jobs, and database storage counters.
