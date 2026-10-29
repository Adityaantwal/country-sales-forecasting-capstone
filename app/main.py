from datetime import datetime, timezone
from time import perf_counter
from fastapi import FastAPI, HTTPException, Query
from app.model import COUNTRIES, forecast_country, forecast_all
from app.logging_utils import configure_logging
from app.monitoring import PerformanceMonitor

app = FastAPI(title="Country Sales Forecasting API", version="1.0.0",
              description="Monthly country-level sales predictions and all-country aggregates.")
logger = configure_logging()
monitor = PerformanceMonitor()

@app.get("/health")
def health():
    return {"status": "ok", "service": "country-sales-forecasting"}

@app.get("/countries")
def countries():
    return {"countries": COUNTRIES}

@app.get("/predict")
def predict(country: str | None = Query(default=None), months: int = Query(default=3, ge=1, le=12)):
    start = perf_counter()
    try:
        if country:
            result = forecast_country(country, months=months)
        else:
            result = forecast_all(months=months)
        elapsed = (perf_counter() - start) * 1000
        monitor.record(elapsed, country=country, error=False, timestamp=datetime.now(timezone.utc).isoformat())
        logger.info("prediction_succeeded", extra={"event": "prediction_succeeded", "country": country or "ALL", "latency_ms": round(elapsed, 3)})
        return {"country": country or "ALL", "months": months, "predictions": result}
    except (ValueError, FileNotFoundError) as exc:
        elapsed = (perf_counter() - start) * 1000
        monitor.record(elapsed, country=country, error=True, timestamp=datetime.now(timezone.utc).isoformat())
        logger.warning("prediction_failed", extra={"event": "prediction_failed", "country": country or "ALL", "latency_ms": round(elapsed, 3)})
        status = 400 if isinstance(exc, ValueError) else 503
        raise HTTPException(status_code=status, detail=str(exc)) from exc
    except Exception as exc:
        elapsed = (perf_counter() - start) * 1000
        monitor.record(elapsed, country=country, error=True, timestamp=datetime.now(timezone.utc).isoformat())
        logger.exception("prediction_error", extra={"event": "prediction_error", "country": country or "ALL", "latency_ms": round(elapsed, 3)})
        raise HTTPException(status_code=500, detail="Internal prediction error") from exc

@app.get("/monitoring")
def monitoring():
    return monitor.snapshot()
