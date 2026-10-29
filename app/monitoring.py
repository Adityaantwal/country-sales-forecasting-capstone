from collections import defaultdict
from threading import Lock
from time import perf_counter

class PerformanceMonitor:
    """Thread-safe, process-local metrics; use Prometheus/OTel for multi-worker production."""
    def __init__(self):
        self._lock = Lock()
        self._requests = 0
        self._errors = 0
        self._latency_total_ms = 0.0
        self._last_prediction_at = None
        self._by_country = defaultdict(int)

    def record(self, latency_ms, country=None, error=False, timestamp=None):
        with self._lock:
            self._requests += 1
            self._errors += int(bool(error))
            self._latency_total_ms += float(latency_ms)
            self._last_prediction_at = timestamp
            self._by_country[country or "ALL"] += 1

    def snapshot(self):
        with self._lock:
            return {
                "requests_total": self._requests,
                "errors_total": self._errors,
                "average_latency_ms": round(self._latency_total_ms / self._requests, 3) if self._requests else 0.0,
                "last_prediction_at": self._last_prediction_at,
                "requests_by_country": dict(self._by_country),
            }

    def reset(self):
        with self._lock:
            self._requests = 0
            self._errors = 0
            self._latency_total_ms = 0.0
            self._last_prediction_at = None
            self._by_country.clear()
