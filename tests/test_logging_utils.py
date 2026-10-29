import json
import logging
from app.logging_utils import configure_logging

def test_json_logger_writes_to_isolated_file(tmp_path):
    log_path = tmp_path / "isolated" / "test.log"
    logger = configure_logging(log_path=log_path)
    logger.info("unit_test_event", extra={"event": "test"})
    for handler in logger.handlers:
        handler.flush()
    payload = json.loads(log_path.read_text(encoding="utf-8").strip().splitlines()[-1])
    assert payload["message"] == "unit_test_event"
    assert payload["event"] == "test"
    # Do not alter production logs; this test only writes to tmp_path.
    logger.handlers.clear()
